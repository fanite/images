FROM ubuntu:20.04 as base

RUN apt-get update && apt-get install -y \
    fuse \
    rclone

FROM amilys/embyserver_arm64v8:4.8.7.0

# COPY --from=base /usr/bin/fuse /usr/bin/fuse
# COPY --from=base /dev/fuse /dev/fuse
COPY --from=base /etc/fuse.conf /etc/fuse.conf
COPY --from=base /usr/sbin/mount.fuse /usr/sbin/mount.fuse
COPY --from=base /usr/bin/fusermount /usr/bin/fusermount
COPY --from=base /usr/bin/rclone /usr/bin/rclone

RUN chmod +x /usr/sbin/mount.fuse /usr/bin/rclone /usr/bin/fusermount
