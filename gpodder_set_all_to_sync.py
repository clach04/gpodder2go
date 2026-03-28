#!/usr/bin/env python
# -*- coding: us-ascii -*-
# vim:ts=4:sw=4:softtabstop=4:smarttab:expandtab
#
"""Mark ALL devices known to username, as syncronized.

gpodder2go notes

1. Need fixed version with Episode sync support - https://github.com/oxtyped/gpodder2go/pull/44
2. can't use a device with no subscriptions, see readme in https://github.com/clach04/gpodder2go for specific steps. This script handles step #5

"""

import argparse
import json
import os
import sys

import requests  # pip install requests


def doit(args, timeout=10):
    """arguments:
        args.username
        args.password
        args.url
    """

    url_root = args.url
    while url_root.endswith('/'):
        print(url_root)
        url_root = url_root[:-1]
    print(url_root)

    # https://gpoddernet.readthedocs.io/en/latest/api/reference/auth.html
    url_login = url_root + '/api/2/auth/%s/login.json' % (args.username,)

    # https://gpoddernet.readthedocs.io/en/latest/api/reference/devices.html
    # https://gpoddernet.readthedocs.io/en/latest/api/reference/sync.html
    url_devices = url_root + '/api/2/devices/%s.json' % (args.username,)
    url_sync_devices = url_root + '/api/2/sync-devices/%s.json' % (args.username,)

    # Using a session object allows for (in-memory) cookie persistence
    session = requests.Session()

    try:
        # use HTTP Basic Auth and login
        auth = (args.username, args.password) if args.username and args.password else None
        response = session.post(url_login, auth=auth, timeout=timeout)
        response.raise_for_status()
        print(f"--- POST Status Code: {response.status_code} ---")
        print(response.text)

        all_devices_ids = []
        response = session.get(url_devices, timeout=timeout)
        response.raise_for_status()
        print(f"--- GET Status Code: {response.status_code} ---")
        print(response.text)
        print(response.json())
        print(json.dumps(response.json(), indent=4))
        print(dir(response))
        for device in response.json():
            all_devices_ids.append(device["id"])

        response = session.get(url_sync_devices, timeout=timeout)
        response.raise_for_status()
        print(f"--- GET Status Code: {response.status_code} ---")
        print(response.text)

        print(all_devices_ids)
        sync_dict = {
            "synchronize": [
                all_devices_ids  # Yes, list in a list (array in an array)
            ],
            #"stop-synchronize": [],
            #"stop-synchronize": None,
        }
        response = session.post(url_sync_devices, auth=auth, timeout=timeout, json=sync_dict)
        response.raise_for_status()
        print(f"--- POST Status Code: {response.status_code} ---")
        print(response.text)

        response = session.get(url_sync_devices, timeout=timeout)
        response.raise_for_status()
        print(f"--- GET Status Code: {response.status_code} ---")
        print(response.text)

    except requests.exceptions.HTTPError as errh:
        print(f"HTTP Error: {errh}")
    except requests.exceptions.ConnectionError as errc:
        print(f"Error Connecting: {errc}")
    except requests.exceptions.Timeout as errt:
        print(f"Timeout Error: {errt}")
    except requests.exceptions.RequestException as err:
        print(f"An unexpected error occurred: {err}")
    finally:
        # Close the session to free up resources
        session.close()

def main(argv=None):
    if argv is None:
        argv = sys.argv

    # FIXME argv
    parser = argparse.ArgumentParser(description="Root URL for gpodder compatible server, omit /api/2/...")
    parser.add_argument("url", help="The target URL (e.g., http://localhost:3005)")
    parser.add_argument("-u", "--username", help="Username for authentication")
    parser.add_argument("-p", "--password", help="Password for authentication")

    args = parser.parse_args()

    print('Python %s on %s' % (sys.version.replace('\n', ' '), sys.platform.replace('\n', ' ')))

    doit(args)

    return 0


if __name__ == "__main__":
    sys.exit(main())
