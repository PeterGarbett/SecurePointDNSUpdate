
Scripts to update SecurePointDNS/cloudns  dns service to current public IP
-----------------------------------------------------------------

Files:

README.md                   This file
spdns.conf   	            Example configuration file (modify and place on /etc/)
spdns.py                    Python to update spdyn when necessary
spdns.service               systemd service file
spdns.timer                 systemd timer file
cloudns.service		    example systemd service file if using cloudns
cloudns.timer               systemd timer file if using cloudns
copy-script		    Called on ipfile update so you can process or copy it etc.
setup-virt                  virtualenv, pip etc for dns and requests 


The format is:

<name>.spdns.org xxxx-yyyy-zzzz <file location>/ipfile.txt script-to-run-on-ip-change

Account setup and token generation from https://www.spdyn.de/

The spdns.py file updates https://www.spdyn.de/
IP discovery is by using https://api.ipify.org
The IP file is used to suppress updates unless the IP has
actually changed to minimise interactions with the dns service.
It is possible to get false results where the ip isn't updated
so theres a check via dns lookup is the ip looks unchanged

Cloudns updates are now integrated with this code, the url
needed to update can be passed on the command line, with
examples cloudns.service and cloudns.timer 

The spdns.py  file is run from /home/embed/SecurePointDNSUpdate/
and and the systemd files on /etc/systemd/system/
The usual incantations are required to enable and start the systemd timer  



