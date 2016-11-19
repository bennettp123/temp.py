#!/usr/bin/env bash

mkdir -p ./data
mkdir -p ./www

DB="./data/temperatures.db"
if [ ! -e "$DB" ]; then
  sqlite3 "$DB" 'BEGIN; CREATE TABLE temperature (timestamp INTEGER, temperature NUMERIC); COMMIT;'
  sqlite3 "$DB" 'BEGIN; CREATE INDEX idx_temperature_timestamp ON temperature(timestamp); COMMIT;'
  sqlite3 "$DB" 'BEGIN; PRAGMA journal_mode=WAL; COMMIT;'
fi

