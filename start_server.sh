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

while true; do
    screen -S $screen_name -d -m python imsearch_http_service.py $SERVER_PORT
    sleep 1
    
    while [ `wget localhost:${SERVER_PORT}/ --no-cache --timeout 3 -O - 2>/dev/null | grep "imsearch HTTP service is running" | wc -l` -eq 1 ]; do
        sleep 3;
    done
    
    screen -S $screen_name -X quit > /dev/null
    date
    echo "'imsearch_http_service' terminated.  Respawning.." >&2
done
