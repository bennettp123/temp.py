#!/usr/bin/env bash

mkdir -p ./data
mkdir -p ./www

DB="./data/temperatures.db"
if [ ! -e "$DB" ]; then
  sqlite3 "$DB" 'BEGIN; CREATE TABLE temperature (timestamp DATETIME, temperature NUMERIC); COMMIT;'
fi
