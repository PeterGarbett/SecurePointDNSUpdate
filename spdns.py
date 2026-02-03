#!/usr/bin/python3
"""Update SecurePointDNS/cloudns ."""

import os
import os.path
import sys
import requests
from requests import get
import dns.resolver

#
#   Debug ensuring we don't pester the dns service
#

TRIAL_RUN = False


def name_to_ip(name):
    """Find what ip address the nameservers have for name"""
    try:
        answers = dns.resolver.resolve(name, "A")
        for rdata in answers:
            ip = rdata.address
    except dns.resolver.NXDOMAIN:
        # print("Domain does not exist.")
        ip = ""

    return ip


def spdns_ip_update(public_ip, site, ipfilename, tokens):
    """spdns rigmarole and result decoding"""
    print("IP: " + str(public_ip))
    print(
        "Updating SecurePointDNS with hostname " + site + ", token " + str(ipfilename)
    )
    data = {"hostname": tokens[0], "myip": public_ip}

    if TRIAL_RUN:
        print("SecurePointDNS update suppressed")
        response = "good"
    else:
        resp = requests.get(
            "https://update.spdyn.de/nic/update",
            params=data,
            auth=(tokens[0], tokens[1]),
            timeout=20,
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


def update_cloudns_record(dynamic_dns_url):
    """This is the cloudns defined magic url trick to ask them to update"""

    if not TRIAL_RUN:
        try:
            if sys.version_info[0] < 3:
                import urllib

                page = urllib.urlopen(dynamic_dns_url)
                page.close()
            else:
                import urllib.request

                page = urllib.request.urlopen(dynamic_dns_url)
                page.close()
        except Exception as err:
            print(err)
            return False
    else:
        print("Dummy call to update IP")

    return True


def update_spdns_record(cloudns_url):
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

    # Find out what IP we currently have
    # print("Retrieving external IP address")

    try:
        public_ip = get("https://api.ipify.org", timeout=20).content.decode("utf8")
    except:
        print("Failed to get IP address")
        sys.exit()

    address = name_to_ip(site)

    # If the IP has changed update our records
    # If not there is nothing at all to do

    if address != public_ip:
        print("IP changed, update IP file and dns")
        ipfile = open(ipfilename, "w", encoding="ascii")
        line = public_ip + " " + site
        ipfile.write(line)
        ipfile.close()

        if os.path.exists(script):
            os.system(script)
    else:
        print("IP unchanged, quit")
        sys.exit()

    # The IP has changed so need to update cloudns/spdns

    if not cloudns_url:
        print("use spdns")
        success = spdns_ip_update(public_ip, site, ipfilename, tokens)
        if not success:
            ipfile = open(ipfilename, "w", encoding="ascii")
            ipfile.write("ip update failed")
            ipfile.close()
    else:
        print("use cloudns")
        success = update_cloudns_record(cloudns_url)
        if not success:
            print("Cloudns update failed")


def main():
    """if using cloudns the url we need to look at to update our ip is passed as an argument"""
    inputargs = sys.argv
    sys.argv.pop(0)

    if len(inputargs) == 1:
        dynamic_dns_url = inputargs[0]
    else:
        dynamic_dns_url = ""

    update_spdns_record(dynamic_dns_url)


if __name__ == "__main__":
    main()
