#/bin/bash

CRASH_LOG=logs/imsearch_service_crash.log
STDERR_LOG=logs/imsearch_service_stderr.log

if [ ! -d ../logs ]
then
    mkdir -p ../logs
fi

cd ../

until python -m imsearchtools.http_service "$@" 1>&1 2> >(tee -a $STDERR_LOG >&2); do
    echo "$@"
    ERR_CODE=$?
    echo "Server 'imsearchtools.http_service' crashed with exit code $ERR_CODE.  Respawning..." >&2

    now=$(date "+%Y-%m-%d %H:%M:%S")
    echo "$now: Exited with code $ERR_CODE " >> $CRASH_LOG

    sleep 1
done
