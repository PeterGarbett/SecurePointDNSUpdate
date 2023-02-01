
Scripts to update SecurePointDNS dns service to current public IP
-----------------------------------------------------------------

Files:

README.md                   This file
example-spdns-config.conf   Example configuration file (place on /etc/)
spdns.py                    Python to update spdyn when necessary
run-spdns                   Entry point for update
spdns.service               systemd service file
spdns.timer                 systemd timer file

There needs to be a file spdns-config.conf derived from the
example file example-spdns-config.conf and placed on /etc

The format is:

<name>.spdns.org xxxx-yyyy-zzzz <file location>/ipfile.txt

Account setup and token generation from https://www.spdyn.de/

The spdns.py file updates https://www.spdyn.de/
IP discovery is by using https://api.ipify.org
The IP file is used to suppress updates unless the IP has
actually changed to minimise interactions with the dns service

The run-spdns and spdns.py  files are expected to be on /usr/local/bin/
and and the systemd files on /etc/systemd/system/
The usual incantations are required to enable and start the systemd timer  

