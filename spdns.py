#!/usr/bin/python3
"""Update SecurePointDNS.  File should be on /usr/local/bin/"""

import os
import os.path
import sys
import requests
from requests import get

#
#   Debug ensuring we don't pester the dns service
#

TRIAL_RUN = False


#
#   Debug ensuring we don't pester the dns service
#

TRIAL_RUN = True


def spdns_ip_update(public_ip, site, ipfilename, tokens):

    print("IP: " + str(public_ip))
    print(
        "Updating SecurePointDNS with hostname " + site + ", token " + str(ipfilename)
    )
    data = {"hostname": tokens[0], "myip": public_ip}
    auth = (tokens[0], tokens[1])

    if TRIAL_RUN:
        print("SecurePointDNS update suppressed")
        response = "good"
    else:
        resp = requests.get(
            "https://update.spdyn.de/nic/update",
            params=data,
            auth=(tokens[0], tokens[1]),
        )
        response = resp.text.split(" ")[0]

    print("response:", response)

    rescodes = {
        "abuse": "The host is locked because of too many failed attempts.",
        "badauth": "The given username / token was not accepted",
        "!yours": "The host could not be managed by your account",
        "nochg": "Your IP has not changed since the last update",
        "good": "IP of " + site + " was updated to " + public_ip,
        "notfqdn": "The host is not an FQDN",
        "nohost": "The host does not exist or was deleted",
        "fatal": "The host was manually deactivated",
    }

    # Decode the response

    if response in rescodes:
        print("Response: " + rescodes[response])
    else:
        print("Unknown response, " + response)

    # If the update failed, make our idea of what the
    # ip is 'wrong' so it will attempt to reset next time

    if response == "good" or response == "nochg":
        return True

    return False


def update_spdns_record():
    """Find public ip and if its changed update spdns dns record"""

    # Load config file (this would arguably be better down using json)
    # print("Loading SecurePointDNS config")

    # Config file is a single line with three parameters separated by a single space.
    # URL token IPFILE

    config_file = open(os.path.expanduser("/etc/spdns.conf"), "r", encoding="ascii")
    contents = config_file.readlines()
    config_file.close()

    # Expect a single line with info in it
    # and any number of comment lines to ignore
    # the real data line shouldn't have any #'s in it

    for line in contents:
        if "#" in line:
            continue
        conf = line

    tokens = conf.strip().split(" ")

    # URL=tokens[0] token=tokens[2] IPFILE=tokens[2]

    try:
        site = tokens[0]
        ipfilename = tokens[2]
    except:
        print("ERROR in config file", tokens)
        sys.exit()

    try:
        script = tokens[3]
    except:
        script = ""

    # Make sure there is a file to record the IP into

    try:
        ipfile = open(ipfilename, "r", encoding="ascii")
    except FileNotFoundError:
        ipfile = open(ipfilename, "w", encoding="ascii")
        ipfile.write("Unknown")
        ipfile.close()

    # Retrieve what we think the current IP is
    try:

        ipfile = open(ipfilename, "r", encoding="ascii")
        ipdata = ipfile.readline()
        ip_and_site = ipdata.strip().split(" ")
        pubip = ip_and_site[0]
        print("IP from file:", pubip, " for ", site)
        ipfile.close()
    except Exception as err:
        print("ERROR in IP file", err)
        pubip = "Unknown"

    # Now find out what IP we currently have

    # print("Retrieving external IP address")
    try:
        public_ip = get("https://api.ipify.org").content.decode("utf8")
    except:
        print("Failed to get IP address")
        sys.exit()

    # If the IP has changed update our records
    # If not there is nothing at all to do

    if pubip != public_ip:
        print("IP changed, update IP file")
        ipfile = open(ipfilename, "w", encoding="ascii")
        line = public_ip + " " + site
        ipfile.write(line)
        ipfile.close()

        if os.path.exists(script):
            os.system(script)
    else:
        #    print("IP unchanged, quit")
        sys.exit()

    # The IP has changed so need to update spdns

    success = spdns_ip_update(public_ip, site, ipfilename, tokens)

    if not success:
        ipfile = open(ipfilename, "w", encoding="ascii")
        ipfile.write("ip update failed")
        ipfile.close()


if __name__ == "__main__":
    update_spdns_record()
