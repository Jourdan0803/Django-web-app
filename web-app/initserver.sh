#!/bin/bash
python3 manage.py makemigrations
python3 manage.py migrate
chmod 777 ./token.json
chmod 777 ./danger_log.txt
res="$?"
while [ "$res" != "0" ]
do
    sleep 3;
    python3 manage.py migrate
    res="$?"
done

