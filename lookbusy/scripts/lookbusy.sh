#!/usr/bin/env bash
set -ex

export CPU_UTIL=${CPU_UTIL:-"20-30"}
export CPU_CORE=${CPU_CORE:-1}
export MEM_UTIL=${MEM_UTIL:-15}

# lookbusy
MemTotal=$(awk '($1 == "MemTotal:"){printf "%d\n",$2/1024}' /proc/meminfo) # total memory
if [ $CPU_CORE ]; then
    if [ $MEM_UTIL ]; then
        MemUsage=$(($MemTotal / 100 * $MEM_UTIL))
        lookbusy -c $CPU_UTIL -n $CPU_CORE -m ${MemUsage}MB
    else
        lookbusy -c $CPU_UTIL -n $CPU_CORE
    fi
else
    if [ $MEM_UTIL ]; then
        MemUsage=$(($MemTotal / 100 * $MEM_UTIL))
        lookbusy -c $CPU_UTIL -r curve -m ${MemUsage}MB
    else
        lookbusy -c $CPU_UTIL -r curve
    fi
fi