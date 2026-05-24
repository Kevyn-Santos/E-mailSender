#!/bin/zsh

URL="http://127.0.0.1:8001/sendMail"
RPS=15
INTERVAL=$((1.0/$RPS))

trap "echo 'Parando...'; kill 0; exit" SIGINT


while true; do
    curl -X POST "$URL" \
    -H "Content-Type: application/json" \
    -d '{"userName": "Kevyn Silva", "userMail": "kevynsantoss10@gmail.com"}' \
    -o /dev/null -w " %{http_code}\t %{errormsg}\n" &
    sleep $INTERVAL
done