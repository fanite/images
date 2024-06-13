from logging.handlers import QueueHandler
import os
import json
import shutil
import logging
import tarfile
from pathlib import Path

logger = logging.getLogger(__name__)

class Utils:
    @staticmethod
    def is_nt():
        return os.name == "nt"

    @staticmethod
    def is_available_path(source_path):
        """
        Check if a path exists.

        This static method takes a `source_path` parameter, which is the path to be checked. It uses the `os.path.exists()` function to determine if the path exists.

        Parameters:
            source_path (str): The path to be checked.

        Returns:
            bool: True if the path exists, False otherwise.
        """
        return os.path.exists(source_path)

    @staticmethod
    def is_available_file(file_path):
        """
        Check if a file exists at the given path.

        Args:
            file_path (str): The path of the file to check.

        Returns:
            bool: True if the file exists, False otherwise.
        """
        return os.path.isfile(file_path)
    
    @staticmethod
    def copy_file(source_file, dest_file):
        """
        Copies a file from the source file path to the destination file path.

        Args:
            source_file (str): The path of the source file.
            dest_file (str): The path of the destination file.

        Raises:
            Exception: If an error occurs during the file copy operation.

        Returns:
            None
        """
        try:
            os.makedirs(os.path.dirname(dest_file), exist_ok=True)
            shutil.copy2(source_file, dest_file)
            logger.info(f"create {source_file} success")
        except Exception as e:
            logger.error("copy file error: %s", e)

    @staticmethod
    def console_progressbar(display_text, step = 10):
        import time
        for i in range(1,step+1):
            print(display_text, end=" "+i*"."+(step-i)*" "+"\r", flush=True)
            time.sleep(1)

    @staticmethod
    def change_file_extension(file_path, new_extension):
        """
        Change the file extension of a given file path.

        Args:
            file_path (str): The path of the file whose extension needs to be changed.
            new_extension (str): The new extension to be applied to the file.

        Returns:
            str: The new file path with the updated extension.
        """
        directory, filename = os.path.split(file_path)
        filename_with_extension = os.path.splitext(filename)[0] + '.' + new_extension
        return os.path.join(directory, filename_with_extension)
    
    @staticmethod
    def compress(source, dest):
        """
        Compresses a directory or file into a gzipped tarball.

        Args:
            source (str or Path): The path of the directory or file to be compressed.
            dest (str or Path): The path of the output tarball.

        Returns:
            None
        """
        source = Path(source)
        dest = Path(dest)
        with tarfile.open(dest, 'w:gz', encoding="utf-8") as tar:
            for root_dir, sub_dirs, files in os.walk(source):
                for file in files:
                    filename = os.path.join(root_dir, file)
                    tar.add(filename, arcname=Path(filename).as_posix().replace(source.as_posix(), ""))
                    logger.info(f"compressed {filename} to {dest} successfully.")
            logger.info(f"compressed {source} to {dest} successfully.")

    @staticmethod
    def decompress(source, dest):
        """
        Decompresses a gzipped tarball.

        Args:
            source (str): The path of the gzipped tarball.
            dest (str): The destination directory where the extracted files will be saved.

        Returns:
            None
        """
        with tarfile.open(source, 'r:gz', encoding="utf-8") as tar:
            for member in tar.getmembers():
                logger.info(f"extracting {member.name} to {dest}")
                tar.extract(member, dest)
            logger.info(f"extract all files completely.")


    


class Profile(dict):
    def __init__(self, profile_file = "profile.json", *args, **kwargs):
        if not os.path.exists(profile_file):
            raise Exception("profile.json not found")

        with open(profile_file, "r", encoding="utf-8") as f:
            self.profile = json.load(f)

        if os.environ.get("LIBSTRM_SERVER"):
            self.profile.update("server", os.environ.get("LIBSTRM_SERVER"))

        super(Profile, self).__init__(self.profile)

    def is_video_file(self, file_path):
        """
        Check if a file is a video file in theprofile.get("formats").get("video").

        Args:
            file_path (str): The path of the file to check.

        Returns:
            bool: True if the file is a video file, False otherwise.
        """
        suffix = os.path.splitext(file_path)[1].lower()
        return suffix in self.get("formats").get("video")

    def is_image_file(self, file_path):
        """
        Check if a file is an image file in the profile.get("formats").get("image").

        Args:
            file_path (str): The path of the file to check.

        Returns:
            bool: True if the file is an image file, False otherwise.
        """
        suffix = os.path.splitext(file_path)[1].lower()
        return suffix in self.get("formats").get("image")

    def is_other_file(self, file_path):
        """
        Check if a file is of type 'other' in the profile.get("formats").get("other").

        Args:
            file_path (str): The path of the file to check.

        Returns:
            bool: True if the file is of type 'other', False otherwise.
        """
        suffix = os.path.splitext(file_path)[1].lower()
        return suffix in self.get("formats").get("other")
    
class StrmLock:
    def __init__(self, lock_file = "strm.lock"):
        self.lock_file = lock_file

    def exist(self):
        return os.path.exists(self.lock_file)

    def write(self,str):
        with open(self.lock_file, "w", encoding="utf-8") as f:
            f.write(str)

    def remove(self):
        if os.path.exists(self.lock_file):
            os.remove(self.lock_file)

