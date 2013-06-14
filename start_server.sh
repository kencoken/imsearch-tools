until python imsearch_http_service.py; do
    echo "'imsearch_http_service' terminated with exit code $?.  Respawning.." >&2
    sleep 1
done