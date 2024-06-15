import os
import time
import logger
import shutil
import logging
import tempfile
import subprocess
from pathlib import Path
from utils import StrmLock, Profile, Utils
from concurrent.futures import ThreadPoolExecutor

class LibStrm(object):
    translation_table = str.maketrans({"\\":"_", "/":"_", ":":"_", "*": "_", "?": "_", "\"": "'", "<": "(", ">": ")", "|": "_","\t": ""})
    def __init__(self):
        self.profile = Profile(os.environ.get("LIBSTRM_PROFILE", "profile.json"))
        self.server = os.environ.get("LIBSTRM_SERVER", self.profile.get("server"))
        self.sync = self.profile.get("sync")
        self.paths = self.profile.get("paths")
        self.formats = self.profile.get("formats")
        self.dest_path = self.profile.get("dest_path")
        self.snapshot_path = self.profile.get("snapshot_path")
        self.source_path = self.profile.get("source_path")
        self.is_win = Utils.is_nt()
    
    def sync_enabled(self):
        return self.sync.get("enabled")

    def back_restore(self):
        try:
            path = self.sync.get("path")
            drive = self.sync.get("drive")
            remote_path = f"{drive}:/{path}"
            path, filename = os.path.split(path)
            temp_dir = os.path.join(tempfile.gettempdir(), "libstrm", path)
            os.makedirs(temp_dir, exist_ok=True)
            subprocess.call(f"rclone copy -P {remote_path} {temp_dir}", shell=True)
            Utils.decompress(os.path.join(temp_dir, filename), self.dest_path)
        except Exception as e:
            logging.error("back restore error: %s", e)
            raise

    def back_up(self):
        try:
            path = self.sync.get("path")
            drive = self.sync.get("drive")
            remote_path, filename = os.path.split(path)
            temp_file = Path(os.path.join(tempfile.gettempdir(), "libstrm/backup", filename))
            os.makedirs(os.path.dirname(temp_file), exist_ok=True)
            Utils.compress(self.dest_path, temp_file)
            subprocess.call(f"rclone copy -P {temp_file} {drive}:/{remote_path}", shell=True)
        except Exception as e:
            logging.error("back up error: %s", e)
            raise

    def create_strm(self,dest_file):
        try:
            video_path = Path(dest_file.replace(self.dest_path, "")).as_posix()
            if video_path.startswith("/"): video_path = video_path[1:]
            video_url = f"{self.server}/{video_path}".replace(" ", "%20").replace("\t","%09")
            parts = Path(video_path).with_suffix(".strm").parts
            # 去除路径每个部分中的两边的空格和不合法的字符
            parts = tuple([part_name.strip().translate(self.translation_table) for part_name in parts])
            strm_file = os.path.join(self.dest_path, *parts)
            snapshot_file = os.path.join(self.snapshot_path, *parts)
            # 只判断快照中是否存在该文件
            if os.path.exists(snapshot_file):
                logging.warning(f"{strm_file} already exists")
                return
            dir = os.path.dirname(strm_file)
            snapshot_dir = os.path.dirname(snapshot_file)
            if not os.path.exists(dir):
                os.makedirs(dir, exist_ok=False)
            if not os.path.exists(snapshot_dir):
                os.makedirs(snapshot_dir, exist_ok=False)
            if self.is_win:
                strm_file = '\\\\?\\'+strm_file
                snapshot_file = '\\\\?\\'+snapshot_file
            with open(strm_file, "w+", encoding="utf-8") as f:
                f.write(video_url)
            with open(snapshot_file, "w+", encoding="utf-8") as f:
                f.write("")
            logging.info("create %s success" % str(strm_file).lstrip("\\\\?\\"))
        except Exception as e:
            logging.error("create strm error: %s", e)

    def check_file_type(self, source_file):
        dest_file = source_file.replace(self.source_path, self.dest_path)
        if self.profile.is_video_file(dest_file):
            self.create_strm(dest_file)
        elif self.profile.is_image_file(dest_file) or self.profile.is_other_file(dest_file):
            dest_file = dest_file.translate(self.translation_table)
            Utils.copy_file(source_file, dest_file)
        else:
            logging.warning(f"skip file {source_file}")

    def walk_source_dir(self, source_path):
        start_time = time.time()
        source_path = Path(os.path.join(self.source_path, source_path))
        logging.info(f"scan {source_path} start.")
        try:
            for curr_dir, sub_dirs, files in os.walk(source_path):
                if len(sub_dirs) != 0: continue
                for file in files:
                    file_path = os.path.join(curr_dir, file)
                    self.check_file_type(file_path)
        except Exception as e:
            logging.error(f"failed to scan {source_path}, error: {e}")
            return
        logging.info(f"scan {source_path} done, cost: {time.time() - start_time}s")

    def clean_dest_dir(self):
        logging.info(f"clean dest dir {self.dest_path} start.")
        try:
            dest = Path(self.dest_path)
            if dest.exists():
                shutil.rmtree(dest)
        except Exception as e:
            logging.error(f"failed to clean dest dir {self.dest_path}, error: {e}")
            return
        logging.info(f"clean dest dir {self.dest_path} done.")

    def flush_all(self, paths = []):
        self.clean_dest_dir()
        paths = paths or self.paths
        start_time = time.time()
        try:
            with ThreadPoolExecutor(max_workers=20) as executor:
                for path in paths:
                    executor.submit(self.walk_source_dir, path.get("source"))
        except Exception as e:
            logging.error("flush all error: %s" % (e,))
        finally:
            executor.shutdown()
            logging.info(f"flush all done, cost: {time.time() - start_time}s")
            logger.stop()
    
def main():
    logger.setup_logging()
    libstrm = LibStrm()
    strm_lock = StrmLock(os.path.join(libstrm.dest_path, "strm.lock"))
    if libstrm.sync_enabled():
        try:
            libstrm.back_restore()
            strm_lock.write("done")
        except Exception as e:
            logging.error("back restore error: %s" % (e,))
    if not strm_lock.exist():
        libstrm.flush_all()
        strm_lock.write("done")
        if libstrm.sync_enabled():
            libstrm.back_up()
        

if __name__ == "__main__":
    profile = Profile(os.environ.get("LIBSTRM_PROFILE", "profile.json"))
    libstrm_log = os.path.join(os.path.dirname(profile.get("dest_path")), "libstrm.log")
    logger.setup_logging(libstrm_log)
    libstrm = LibStrm()
    libstrm.flush_all()
    if libstrm.sync_enabled():
        libstrm.back_up()
    
