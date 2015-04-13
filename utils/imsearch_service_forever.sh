#/bin/bash

CRASH_LOG=logs/imsearch_service_crash.log
STDERR_LOG=logs/imsearch_service_stderr.log

if [ ! -d ../logs ]
then
    mkdir -p ../logs
fi

cd ../

until python imsearch_http_service.py "$@" 1>&1 2> >(tee -a $STDERR_LOG >&2); do
    echo "$@"
    ERR_CODE=$?
    echo "Server './imsearch_http_service.py' crashed with exit code $ERR_CODE.  Respawning..." >&2

    now=$(date "+%Y-%m-%d %H:%M:%S")
    echo "$now: Exited with code $ERR_CODE " >> $CRASH_LOG

    sleep 1
done
