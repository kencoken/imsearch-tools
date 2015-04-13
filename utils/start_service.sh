#!/bin/sh

if [ $# -lt 1 ]; then
    SERVER_PORT=35200
else
    if [ $# -ne 1 ]; then
        echo "Usage: `basename $0` [SERVER_PORT]"
        exit $E_BADARGS
    else
        SERVER_PORT=$1
    fi
fi

screen_name=imsearch_$SERVER_PORT

screen -dm -S $screen_name bash -l -c "./imsearch_service_forever.sh $SERVER_PORT"
