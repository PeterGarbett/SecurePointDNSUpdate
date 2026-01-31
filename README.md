
Scripts to update SecurePointDNS dns service to current public IP
-----------------------------------------------------------------

Files:

README.md                   This file
spdns.conf   	            Example configuration file (modify and place on /etc/)
spdns.py                    Python to update spdyn when necessary
spdns.service               systemd service file
spdns.timer                 systemd timer file


The format is:

<name>.spdns.org xxxx-yyyy-zzzz <file location>/ipfile.txt script-to-run-on-ip-change

Account setup and token generation from https://www.spdyn.de/

The spdns.py file updates https://www.spdyn.de/
IP discovery is by using https://api.ipify.org
The IP file is used to suppress updates unless the IP has
actually changed to minimise interactions with the dns service.
It is possible to get false results where the ip isn't updated
so theres a check via dns lookup is the ip looks unchanged

The spdns.py  file is run from /home/embed/SecurePointDNSUpdate/
and and the systemd files on /etc/systemd/system/
The usual incantations are required to enable and start the systemd timer  

