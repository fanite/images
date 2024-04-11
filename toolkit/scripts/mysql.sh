#!/bin/sh

MYSQL_ROOT_USER=${MYSQL_ROOT_USER:-"root"}
MYSQL_ROOT_PASSWORD=${MYSQL_ROOT_PASSWORD:-"root"}
MYSQL_MASTER_HOST=${MYSQL_MASTER_HOST:-"mysql-headless.default.svc.cluster.local"}
DATE=$(date +"%Y%m%d")
BASE_NAME=${BASE_NAME:-"mysql-backup"}
STORAGE_PROVIDER=${STORAGE_PROVIDER:-"onedrive"}
STORAGE_BACKUP_PATH=${STORAGE_BACKUP_PATH:-"/storages/backups/databases/k3s-common-db"}
REMOTE_BACKUP_PATH=${STORAGE_PROVIDER}:${STORAGE_BACKUP_PATH}
BACKUP_NUMBER_LIMIT=${BACKUP_NUMBER_LIMIT:-30}

function backup() {
    set -ev
    local TEMPDIR=$(mktemp -d)
    local db_names=$(mysql -e "show databases;" -u${MYSQL_ROOT_USER} -p${MYSQL_ROOT_PASSWORD} -h ${MYSQL_MASTER_HOST} | grep -Ev "Database|information_schema|performance_schema|mysql|sys")
    for db in $db_names; do
        echo "Backing up $db database"
        mysqldump -u${MYSQL_ROOT_USER} -p${MYSQL_ROOT_PASSWORD} -h ${MYSQL_MASTER_HOST} --triggers --routines --events --databases $db > ${TEMPDIR}/${db}.sql
    done
    tar -czf ${BASE_NAME}-${DATE}.tar.gz -C ${TEMPDIR} .
    tar -czf ${BASE_NAME}-latest.tar.gz -C ${TEMPDIR} .
    rclone ls ${REMOTE_BACKUP_PATH}/ | awk '{print $2}' | sort -r | tail -n +$(($BACKUP_NUMBER_LIMIT + 1)) | xargs -i -t rclone delete ${REMOTE_BACKUP_PATH}/{}
    echo "${BASE_NAME}-${DATE}.tar.gz ${BASE_NAME}-latest.tar.gz" | xargs -n 1 echo | xargs -i -t rclone copy ${TEMPDIR}/{} ${REMOTE_BACKUP_PATH}/
    rm -rf ${TEMPDIR}
    set +ev
}

function restore() {
    set -ev
    local FILE_DATE=${2:-"latest"}
    local FILE_NAME=${BASE_NAME}-${FILE_DATE}.tar.gz
    local REMOTE_FILE_PATH=${REMOTE_BACKUP_PATH}/${FILE_NAME}
    local TEMPDIR=$(mktemp -d)
    rclone copy ${REMOTE_FILE_PATH} ${TEMPDIR}
    mkdir ${TEMPDIR}/data
    tar -xzf ${TEMPDIR}/${FILE_NAME} -C ${TEMPDIR}/data
    for db in $(ls ${TEMPDIR}/data); do
        mysql -u${MYSQL_ROOT_USER} -p${MYSQL_ROOT_PASSWORD} -h ${MYSQL_MASTER_HOST} < ${TEMPDIR}/data/${db}
    done
    rm -rf ${TEMPDIR}
    set +ev
}

function usage() {
    cat <<EOF
Usage: $0 [backup|restore]

Options:
    backup: 备份数据库
    restore <date>: 恢复数据库, date 为备份日期, 格式为 %Y%m%d，默认值为 latest

Environment:
    MYSQL_ROOT_USER: mysql 用户名，默认为 root
    MYSQL_ROOT_PASSWORD: mysql 密码，若为 root 请留空
    MYSQL_MASTER_HOST: mysql 地址，默认为 mysql-headless.default.svc.cluster.local
    BASE_NAME: 备份文件名，默认为 mysql-backup
    STORAGE_PROVIDER: Rclone 存储提供商，默认为 onedrive
    STORAGE_BACKUP_PATH: Rclone 远程备份存储路径，默认为 /storages/backups/databases/k3s-common-db
    BACKUP_NUMBER_LIMIT: 备份文件数量限制，默认为 30
EOF
}

case "$1" in
backup)
    backup
    ;;
restore)
    restore
    ;;
*)
    usage
    ;;
esac