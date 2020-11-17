#!/usr/bin/zsh

if lsof -i:5000
then
    sudo kill -9 $(sudo lsof -t -i:5000)
fi

if lsof -i:6379
then
    sudo kill -9 $(sudo lsof -t -i:6379)
fi

redis-server --port 6379 &
sleep 1s
python3 worker.py &
sleep 1s
flask run --port=5000 --host=0.0.0.0 &
