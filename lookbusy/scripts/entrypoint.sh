#!/usr/bin/env bash
set -ex

export SPEEDTEST_SCHEDULE=${SPEEDTEST_SCHEDULE:-"*/10 * * * *"}
export LOOKBUSY_SCHEDULE=${LOOKBUSY_SCHEDULE:-"*/10 * * * *"}
export BUSY_TIME=${BUSY_TIME:-"3h"}

echo -e "${LOOKBUSY_SCHEDULE}\t/bin/sh -ec timeout -k 0 ${BUSY_TIME} /script/lookbusy.sh >>/dev/stdout 2>&1 &">/var/spool/cron/crontabs/root
echo -e "${SPEEDTEST_SCHEDULE}\t/bin/sh -ec /script/speedtest.sh >>/dev/stdout 2>&1 &">>/var/spool/cron/crontabs/root
rc-service cron restart
echo "Scheduled task created successfully"

