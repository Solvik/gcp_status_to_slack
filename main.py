#!/usr/bin/env python3

import json
import requests
import pytz
from datetime import datetime
from dateutil import parser

import config

def to_datetime(dt):
    return parser.parse(dt)

class GCPStatusToSlack():
    '''
    Fetch GCP Status json and compare watched services with last run time of
    this script to notify new events in a Slack channel
    '''
    def __init__(self):
        r = requests.get(config.GCP_INCIDENTS_URL)
        r.raise_for_status()
        self.data = r.json()
        self.last_run = None

    def get_last_run(self):
        '''
        Get last run date of the script
        '''
        try:
            fd = open(config.LAST_RUN_FILE, 'r')
            content = fd.read()
            fd.close()
            self.last_run = to_datetime(content)
        except:
            self.last_run = datetime.now(tz=pytz.utc)
        return self.last_run

    def set_last_run(self):
        '''
        Set last run datetime of the script, in UTC
        '''
        fd = open(config.LAST_RUN_FILE, 'w')
        fd.write(
            datetime.now(tz=pytz.utc)
            .strftime('%Y-%m-%dT%H:%M:%SZ')
        )
        fd.close()

    def find_new_events(self):
        '''
        Find new events in the json
        Filters events by keeping only watched services
        '''
        filtered_events = [x for x in self.data if x['service_key'] in config.GCP_SERVICES]

        for event in filtered_events:
            if to_datetime(event['modified']) > self.get_last_run():
                self.notify(event)

    def notify(self, event):
        '''
        Send notification to slack
        '''
        notification = u'{} incident #{} update: {}\n'\
            'More information: {}{}'.format(
                event['service_name'],
                event['number'],
                event['most-recent-update']['text'],
                config.GCP_STATUS_URL,
                event['uri'])

        payload = {
            'payload': json.dumps({
                'channel': config.SLACK_CHANNEL,
                'username': config.SLACK_USERNAME,
                'text': notification,
                'icon_emoji': ':google:'
            })
        }
        r = requests.post(
            config.SLACK_HOOKS_SERVICE,
            data=payload,
        )
        r.raise_for_exception()

    def run(self):
        '''
        Run routine
        '''
        self.get_last_run()
        self.find_new_events()
        self.set_last_run()

if __name__ == '__main__':
    a = GCPStatusToSlack()
    a.run()
