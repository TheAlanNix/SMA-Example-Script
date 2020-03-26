#! /usr/bin/env python
# -*- coding: utf-8 -*-
"""
This is an example Python script to demonstrate the API capabilities of
the Cisco Content Security Management Appliance (SMA)

This script will get all incoming emails for the past day, and create a
CSV file for each sender listing the recipients and subjects of the emails.
"""

import argparse
import csv
import getpass
import json
import os
import shutil
import time

import requests

from datetime import datetime, timedelta
from requests.auth import HTTPBasicAuth
from requests.packages import urllib3

# Disable SSL Certificate warnings
try:
    urllib3.disable_warnings()
except Exception as ex:
    pass

# Config Paramters
CONFIG_FILE = "config.json"
CONFIG_DATA = {}

# Set a wait interval (in seconds) - 1 Day
INTERVAL = 86400


####################
#    FUNCTIONS     #
####################


def load_config(retry=False):
    """Load configuration data from file."""

    print("Loading configuration data...")

    # If we have a stored config file, then use it, otherwise terminate
    if os.path.isfile(CONFIG_FILE):

        # Open the CONFIG_FILE and load it
        with open(CONFIG_FILE, "r") as config_file:
            CONFIG_DATA = json.loads(config_file.read())

        print("Configuration data loaded successfully.")

        return CONFIG_DATA

    else:
        # Check to see if this is the initial load_config attempt
        if not retry:

            # Print that we couldn't find the config file, and attempt to copy the example
            print("The configuration file was not found. Copying 'config.example.json' file to '{}', and retrying...".format(CONFIG_FILE))
            shutil.copyfile('config.example.json', CONFIG_FILE)

            # Try to reload the config
            return load_config(retry=True)
        else:

            # Exit gracefully if we cannot load the config
            print("Unable to automatically create config file. Please copy 'config.example.json' to '{}' manually.".format(CONFIG_FILE))
            exit()


def save_config():
    """Save configuration data to file."""

    with open(CONFIG_FILE, "w") as output_file:
        json.dump(CONFIG_DATA, output_file, indent=4)


def get_message_tracking_data(start_date, end_date, offset: int = 0, limit: int = 20):
    """A function to retrieve message tracking data from the SMA."""

    print("Fetching data from the SMA...")

    # Instantiate the returned results variable
    returned_results = limit

    # Instantiate a results placeholder
    return_data = []

    # Loop through each "page" until the results returned is under the limit
    while returned_results == limit:

        url = f"https://{CONFIG_DATA['SMA_HOSTNAME']}:6443/sma/api/v2.0/message-tracking/messages?" \
              f"startDate={start_date}.000Z&endDate={end_date}.000Z&ciscoHost=All_Hosts&searchOption=messages" \
              f"&offset={offset}&limit={limit}"

        print(url)

        try:
            # Fetch the data from the SMA
            response = requests.get(url, auth=HTTPBasicAuth(CONFIG_DATA["SMA_USERNAME"], CONFIG_DATA["SMA_PASSWORD"]), verify=False)

            # If the response is in the 2xx range
            if response.status_code >= 200 and response.status_code < 300:

                # Set the returned results variable
                returned_results = response.json()["meta"]["num_bad_records"] + response.json()["meta"]["totalCount"]

                # Add all the messages to the return data
                for message in response.json()["data"]:
                    return_data.append(message)

            else:
                print(json.dumps(response.json(), indent=4))
        except Exception as err:
            print("Error fetching info from SMA: " + str(err))

        # Increment the offset
        offset += limit

    return return_data


def main():
    """This is the main function to run the SMA Example script."""

    # Make a timestamp for a week ago
    seven_days_ago = datetime.utcnow().replace(second=0, microsecond=0) - timedelta(days=1)

    # Convert the timestamp to ISO Format
    start_date = seven_days_ago.isoformat()

    # Get the current timestamp in ISO Format
    end_date = datetime.utcnow().replace(second=0, microsecond=0).isoformat()

    # Get the last weeks worth of messages from the SMA
    message_data = get_message_tracking_data(start_date, end_date)

    print(f"Messages retrieved: {len(message_data)}")

    csv_data = {}

    # Iterate through all messages
    for message in message_data:

        # Filter for "incoming" messages
        if message["attributes"]["direction"] == "incoming":

            # If the sender exists, append, otherwise create
            if message["attributes"]["sender"] in csv_data.keys():

                # Append to the existing dictionary
                csv_data[message["attributes"]["sender"]].append({
                    "recipients": message["attributes"]["recipient"],
                    "subject": message["attributes"]["subject"]
                })

            else:

                # Create an initial dictionary
                csv_data[message["attributes"]["sender"]] = [{
                    "recipients": message["attributes"]["recipient"],
                    "subject": message["attributes"]["subject"]
                }]

    # Write a CSV of incoming emails
    for sender, emails in csv_data.items():

        with open(f"csv_files/{sender}_incoming_emails.csv", "w", newline="") as file:
            fieldnames = ["recipients", "subject"]
            writer = csv.DictWriter(file, fieldnames=fieldnames)

            writer.writeheader()

            for email in emails:
                writer.writerow(email)


###################
# !!! DO WORK !!! #
###################


if __name__ == "__main__":

    # Set up an argument parser
    parser = argparse.ArgumentParser(
        description="A script to get data from a Cisco Content Security Management Appliance (SMA) "
                    "and generate organized CSV files from it."
    )
    parser.add_argument("-d", "--daemon", help="Run the script as a daemon", action="store_true")
    args = parser.parse_args()

    # Load configuration data from file
    CONFIG_DATA = load_config()

    # If not hard coded, get the SMA Address, Username and Password
    if not CONFIG_DATA["SMA_HOSTNAME"]:
        CONFIG_DATA["SMA_HOSTNAME"] = input("SMA IP/FQDN Address: ")
        save_config()
    if not CONFIG_DATA["SMA_USERNAME"]:
        CONFIG_DATA["SMA_USERNAME"] = input("SMA Username: ")
        save_config()
    if not CONFIG_DATA["SMA_PASSWORD"]:
        CONFIG_DATA["SMA_PASSWORD"] = getpass.getpass("SMA Password: ")
        save_config()

    if args.daemon:
        while True:
            main()
            print("Waiting {} seconds...".format(INTERVAL))
            time.sleep(INTERVAL)
    else:
        main()
