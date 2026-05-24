#!/bin/zsh

URL="http://127.0.0.1:8001/sendMail"
RPS=15
INTERVAL=$((1.0/$RPS))
DURATION=5
END=$((SECONDS + DURATION))

trap "echo 'Parando...'; kill 0; exit" SIGINT

while (($SECONDS < $END)); do
    curl -X POST "$URL" \
    -H "Content-Type: application/json" \
    -d '{"userName": "Kevyn Silva", "userMail": "kevynsantoss10@gmail.com"}' \
    -o /dev/null \
    -w "HTTP: %{http_code}\t ERR: %{errormsg}\t TIME:%{time_total}\n" \
    | ts '%H:%M:%S' & 
    sleep $INTERVAL
done