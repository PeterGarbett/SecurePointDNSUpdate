#!/usr/bin/python3
""" Update SecurePointDNS.  File should be on /usr/local/bin/ """

import os
import sys
import requests
from requests import get

#
#   Debug ensuring we don't pester the dns service
#

TRIAL_RUN = False


def update_spdns_record():
    """Find public ip and if its changed update spdns dns record"""

    # Load config file
    print("Loading SecurePointDNS config")

    # Config file is a single line with three parameters separated by a single space.
    # URL token IPFILE

    config_file = open(
        os.path.expanduser("/etc/spdns-config.conf"), "r", encoding="ascii"
    )
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

    ipfilename = tokens[2]

    # Make sure there is a file to record the IP into

    try:
        ipfile = open(ipfilename, "r", encoding="ascii")
    except FileNotFoundError:
        ipfile = open(ipfilename, "w", encoding="ascii")
        ipfile.write("no ip")
        ipfile.close()

    # Retrieve what we think the current IP is

    ipfile = open(ipfilename, "r", encoding="ascii")
    pubip = ipfile.readline()
    ipfile.close()

    # Now find out what IP we currently have

    print("Retrieving external IP address")
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
        ipfile.write(public_ip)
        ipfile.close()
    else:
        print("IP unchanged, quit")
        sys.exit()

    # The IP has changed so need to update spdns

    print("IP: " + str(public_ip))
    print(
        "Updating SecurePointDNS with hostname "
        + str(tokens[0])
        + ", token "
        + str(tokens[1])
    )
    data = {"hostname": tokens[0], "myip": public_ip}

    if TRIAL_RUN:
        print(" SecurePointDNS update suppressed")
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
        "good": "IP of " + tokens[0] + " was updated to " + public_ip,
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
        sys.exit()

    ipfile = open(ipfilename, "w", encoding="ascii")
    ipfile.write("ip update failed")
    ipfile.close()


if __name__ == "__main__":
    update_spdns_record()
