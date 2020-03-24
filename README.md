# Cisco Content Security Management Appliance (SMA) Example

## Summary

This is a simple example of how to interact with the Cisco Content Security Management Appliance (SMA) through the APIs that were added in AsyncOS 13.

This sample script will gather data around all email messages sent/recieved in the last 7 days using the message tracking API.  The script will then filter the data for incoming email, and then organize the data by sender - storing the recipients and subjects for each message.  Finally, a CSV file is created for each sender which will list each incoming email, who the reciepients were, and the subject of the message.

## Requirements

1. Python 3.x
2. Cisco Content Security Management Appliance running AsyncOS 13.0 or higher

## Configuration File

The ***config.json*** file contains the following variables:

- SMA_HOSTNAME: The IP or FQDN of the Security Management Appliance (SMA). (String)
- SMA_USERNAME: The Username to be used to authenticate to the Security Management Appliance (SMA). (String)
- SMA_PASSWORD: The Password to be used to authenticate to the Security Management Appliance (SMA). (String)

## How To Run

1. Install the required packages from the ***requirements.txt*** file.
    * ```pip install -r requirements.txt```
    * You'll probably want to set up a virtual environment: [Python 'venv' Tutorial](https://docs.python.org/3/tutorial/venv.html)
    * Activate the Python virtual environment, if you created one.
3. Run the script by executing the following command:
    * ```python sma_example.py```
    * On the first run, you will be prompted for the Hostname, Username, and Password for accessing the SMA's API.  Subsequent runs will use the stored values.
