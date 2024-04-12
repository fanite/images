#!/bin/sh

export MYSQL_USER=${MYSQL_USER:-"fanite"}
export MYSQL_ROOT_USER=${MYSQL_ROOT_USER:-"root"}
export MYSQL_ROOT_PASSWORD=${MYSQL_ROOT_PASSWORD:-"root"}
export MYSQL_HOST=${MYSQL_HOST:-"mysql-headless.default.svc.cluster.local"}
export BASE_NAME=${BASE_NAME:-"mysql-backup"}
export STORAGE_PROVIDER=${STORAGE_PROVIDER:-"onedrive"}
export STORAGE_BACKUP_PATH=${STORAGE_BACKUP_PATH:-"/storages/backups/databases/k3s-common-db"}
export BACKUP_NUMBER_LIMIT=${BACKUP_NUMBER_LIMIT:-30}
export RCLONE_CONFIG=${RCLONE_CONFIG:-"/workspace/config/rclone.conf"}
REMOTE_BACKUP_PATH=${STORAGE_PROVIDER}:${STORAGE_BACKUP_PATH}
DATE=$(date +"%Y%m%d")

if [ -e ${RCLONE_CONFIG} ]; then
    echo "Rclone 配置文件 ${RCLONE_CONFIG} 存在"
    mkdir -p /root/.config/rclone/
    cp ${RCLONE_CONFIG} /root/.config/rclone/rclone.conf
    chmod 777 /root/.config/rclone/rclone.conf
    export RCLONE_CONFIG="/root/.config/rclone/rclone.conf"
else
    echo "Rclone 配置文件 ${RCLONE_CONFIG} 不存在"
    exit 1
fi

function backup() {
    local TEMPDIR=$(mktemp -d)
    local db_names=$(mysql -e "show databases;" -u${MYSQL_ROOT_USER} -p${MYSQL_ROOT_PASSWORD} -h ${MYSQL_HOST} | grep -Ev "Database|information_schema|performance_schema|mysql|sys")
    for db in $db_names; do
        echo "Backing up $db database"
        mysqldump -u${MYSQL_ROOT_USER} -p${MYSQL_ROOT_PASSWORD} -h ${MYSQL_HOST} --triggers --routines --events --databases $db > ${TEMPDIR}/${db}.sql
    done
    echo "压缩备份的数据库文件：${BASE_NAME}-${DATE}.tar.gz ${BASE_NAME}-latest.tar.gz"
    tar -czf ${BASE_NAME}-${DATE}.tar.gz -C ${TEMPDIR} .
    tar -czf ${BASE_NAME}-latest.tar.gz -C ${TEMPDIR} .
    echo "只保留最近 ${BACKUP_NUMBER_LIMIT} 个备份文件，删除其他文件"
    rclone --config ${RCLONE_CONFIG} ls ${REMOTE_BACKUP_PATH}/ | awk '{print $2}' | sort -r | tail -n +$(($BACKUP_NUMBER_LIMIT + 1)) | xargs -i -t rclone --config ${RCLONE_CONFIG} delete ${REMOTE_BACKUP_PATH}/{}
    echo "${BASE_NAME}-${DATE}.tar.gz ${BASE_NAME}-latest.tar.gz" | xargs -n 1 echo | xargs -i -t rclone --config ${RCLONE_CONFIG} copy ./{} ${REMOTE_BACKUP_PATH}/
    echo "备份完成，删除临时文件"
    rm -rf ./${BASE_NAME}-${DATE}.tar.gz
    rm -rf ./${BASE_NAME}-latest.tar.gz
    rm -rf ${TEMPDIR}
}

function restore() {
    local FILE_DATE=${2:-"latest"}
    local FILE_NAME=${BASE_NAME}-${FILE_DATE}.tar.gz
    local REMOTE_FILE_PATH=${REMOTE_BACKUP_PATH}/${FILE_NAME}
    local TEMPDIR=$(mktemp -d)
    echo "下载数据库备份文件：${REMOTE_FILE_PATH}"
    rclone --config ${RCLONE_CONFIG} -P copy ${REMOTE_FILE_PATH} ${TEMPDIR}
    mkdir ${TEMPDIR}/data
    echo "解压数据库备份文件：${REMOTE_FILE_PATH}"
    tar -xzvf ${TEMPDIR}/${FILE_NAME} -C ${TEMPDIR}/data
    echo "查询数据库中是否存在用户：${MYSQL_USER}"
    user=$(mysql -e "select concat(User, '@', Host) as user from mysql.user where User='${MYSQL_USER}';" -u${MYSQL_ROOT_USER} -p${MYSQL_ROOT_PASSWORD} -h ${MYSQL_HOST} | grep -v "user")
    for db in $(ls ${TEMPDIR}/data); do
        echo "Restore $db database"
        mysql -u${MYSQL_ROOT_USER} -p${MYSQL_ROOT_PASSWORD} -h ${MYSQL_HOST} < ${TEMPDIR}/data/${db}
        if [ -n "${user}" ]; then
            echo "grant all privileges on ${db:0:-4}.* to '${MYSQL_USER}'@'%';flush privileges;"
            mysql -u${MYSQL_ROOT_USER} -p${MYSQL_ROOT_PASSWORD} -h ${MYSQL_HOST} -e "grant all privileges on ${db:0:-4}.* to '${MYSQL_USER}'@'%';flush privileges;"
        fi
    done
    rm -rf ${TEMPDIR}
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
    MYSQL_HOST: mysql 地址，默认为 mysql-headless.default.svc.cluster.local
    BASE_NAME: 备份文件名，默认为 mysql-backup
    STORAGE_PROVIDER: Rclone 存储提供商，默认为 onedrive
    STORAGE_BACKUP_PATH: Rclone 远程备份存储路径，默认为 /storages/backups/databases/k3s-common-db
    BACKUP_NUMBER_LIMIT: 备份文件数量限制，默认为 30
    RCLONE_CONFIG: Rclone 配置文件路径，默认为 /workspace/config/rclone.conf
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