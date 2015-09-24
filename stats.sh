#!/bin/bash

LOGS_DIR=/home/gerrit2/review_site/logs

rm -rf results

LOG_FILTER="replication_log*"
#LOG_FILTER="replication_log.2015-09-17.gz"

for log in $(find $LOGS_DIR -name "$LOG_FILTER"); do
    echo $log
    while read line; do
        sched_id=$(echo $line | awk '{print $3}' | sed 's/\[\(.*\)\]/\1/g')
        commit=$(zgrep $sched_id $log | grep Push | sed 's/.*\.\.\.\([a-z0-9]*\).*/\1/g' | head -1)
        if [ -z "$commit" ]; then
            commit="noref-$sched_id"
        fi
        remote=$(echo $line | awk '{print $6}' | sed 's/.*@\([^\/]*\)\/.*/\1/g')
        project=$(echo $line | awk '{print $6}' | sed 's^.*git/\(.*\)\.git^\1^g' | tr '/' '_')
        delay=$(echo $line | awk '{print $9}')
        datetime=$(echo $line | awk '{print $1 " " $2}' | sed 's/\[\(.*\)\]/\1/g')
        timestamp=$(date -d "$datetime" +%s)
        echo "$sched_id,$commit,$project,$remote,$timestamp,$delay"

        if ! [ -e "results/$remote" ]; then
            mkdir -p results/$remote
        fi

        echo "$timestamp $delay $commit" >> results/$remote/$project

    done < <(zgrep completed $log)
done

