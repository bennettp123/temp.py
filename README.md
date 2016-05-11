Raspberry Pi Temperature Logger
===============================

Largely ripped from [https://github.com/Pyplate/rpi_temp_logger](here), but modified to be non-cgi. (Produces static html content).

Installation and setup: see `db-setup.sh` and `crontab.example`.

Sample nginx config:

        location /temperature {
                root /home/bennett/src/temp.py/www;
                allow all;
        }
