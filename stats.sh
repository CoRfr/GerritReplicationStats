#!/bin/bash

LOGS_DIR=/home/gerrit2/review_site/logs

rm -rf results

for log in $(find $LOGS_DIR -name "replication_log*"); do
    echo $log
    while read line; do
        commit=$(echo $line | awk '{print $3}' | sed 's/\[\(.*\)\]/\1/g')
        remote=$(echo $line | awk '{print $6}' | sed 's/.*@\([^\/]*\)\/.*/\1/g')
        project=$(echo $line | awk '{print $6}' | sed 's^.*git/\(.*\)\.git^\1^g' | tr '/' '_')
        delay=$(echo $line | awk '{print $9}')
        datetime=$(echo $line | awk '{print $1 " " $2}' | sed 's/\[\(.*\)\]/\1/g')
        timestamp=$(date -d "$datetime" +%s)
        echo "$commit,$project,$remote,$timestamp,$delay"

        if ! [ -e "results/$remote" ]; then
            mkdir -p results/$remote
        fi

        echo "$timestamp $delay $commit" >> results/$remote/$project

    done < <(zgrep completed $log)
done

