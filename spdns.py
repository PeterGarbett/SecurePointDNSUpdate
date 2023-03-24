#!/usr/bin/python3
#
#    Update SecurePointDNS.  File should be on /usr/local/bin/
#
#
import requests
import json
import os
from requests import get

#
#   Debug ensuring we don't pester the dns service
#
trialrun=False


# Load config file
print("Loading SecurePointDNS config")

# Config file is a single line with three parameters separated by a single space.
# URL token IPFILE
f = open(os.path.expanduser("/etc/spdns-config.conf"), "r")

contents = f.readlines()
f.close()

# expect a single line with info in it
# and any number of comment lines to ignore
# the real data line shouldn't have any #'s in it

for line in contents:
    if "#" in line:
        continue
    else:
        conf = line

toks = conf.strip().split(" ")

# URL=toks[0] token=toks[2] IPFILE=toks[2]

ipfilename = toks[2]

# Make sure there is a file to record the IP into

try:
    ipfile = open(ipfilename, "r")
except FileNotFoundError:
    ipfile = open(ipfilename, "w")
    ipfile.write("no ip")
ipfile.close()

# Retrieve what we think the current IP is

ipfile = open(ipfilename, "r")
pubip = ipfile.readline()
ipfile.close()

# Now find out what IP we currently have

print("Retrieving external IP address")
try:
    ip = get("https://api.ipify.org").content.decode("utf8")
except:
    print("Failed to get IP address")
    quit()



# If the IP has changed update our records
# If not there is nothing at all to do

if pubip != ip:
    print("IP changed, update IP file")
    ipfile = open(ipfilename, "w")
    ipfile.write(ip)
    ipfile.close()
else:
    print("IP unchanged, quit")
    quit()

# The IP has changed so need to update spdns

print("IP: " + str(ip))
print(
    "Updating SecurePointDNS with hostname " + str(toks[0]) + ", token " + str(toks[1])
)
data = {"hostname": toks[0], "myip": ip}

if trialrun:
    
    print("dns update suppressed to develop and debug systemd timer/service")
    r = "good"
else:
    resp = requests.get(
    "https://update.spdyn.de/nic/update", params=data, auth=(toks[0], toks[1])
 )
    r = resp.text.split(" ")[0]


rescodes = {
    "abuse": "The host is locked because of too many failed attempts.",
    "badauth": "The given username / token was not accepted",
    "!yours": "The host could not be managed by your account",
    "nochg": "Your IP has not changed since the last update",
    "good": "IP of " + toks[0] + " was updated to " + ip,
    "notfqdn": "The host is not an FQDN",
    "nohost": "The host does not exist or was deleted",
    "fatal": "The host was manually deactivated",
}

# Decode the response

if r in rescodes:
    print("Response: " + rescodes[r])
else:
    print("Unknown response, " + r)

