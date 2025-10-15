#!/bin/bash
echo "Starting PhotoPro AI Backend..."
exec gunicorn app:app -w 4 -k uvicorn.workers.UvicornWorker --bind 0.0.0.0:$PORT
