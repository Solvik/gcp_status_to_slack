#!/usr/bin/env python3

import json
import sys
import requests
from datetime import date
from dateutil import parser

import config

def to_datetime(dt):
    return parser.parse(dt)

class GCPStatusToSlack():
    '''
    Fetch GCP Status json and compare the last update of watched services incidents
    to notify new events in a Slack channel
    '''
    def __init__(self):
        r = requests.get(config.GCP_INCIDENTS_URL)
        r.raise_for_status()
        self.data = r.json()
        self.delta = None
        self.today = date.today()

    def get_last_run(self):
        '''
        Get last state of delta file
        '''
        try:
            fd = open(config.LAST_RUN_FILE, 'r')
            content = fd.read()
            fd.close()
            self.delta = json.loads(content)
        except Exception as e:
            sys.stderr.write('Cannot read/parse delta file : {}. Using an empty'
                             'delta\n'.format(e))
            self.delta = {}

    def set_last_run(self):
        '''
        Write the delta state in file
        '''
        fd = open(config.LAST_RUN_FILE, 'w')
        fd.write(
            json.dumps(self.delta)
        )
        fd.close()

    def cleanup(self):
        '''
        Delete old entries of the delta dict
        '''
        to_delete = [event for event, last_modified in self.delta.items() if \
                     to_datetime(last_modified).date() < self.today]
        for key in to_delete:
            del self.delta[key]

    def find_new_events(self):
        '''
        Find new events in the json
        Filters events by keeping only watched services
        '''
        filtered_events = [x for x in self.data if x['service_key'] in \
                           config.GCP_SERVICES and \
                           to_datetime(x['modified']).date() == self.today]

        for event in filtered_events:
            if str(event['number']) not in self.delta or \
               self.delta[str(event['number'])] < event['modified']:
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

        # Save the last evend in the delta file
        self.delta[str(event['number'])] = event['modified']

        for channel in config.SLACK_CHANNELS:
            payload = {
                'payload': json.dumps({
                    'channel': channel,
                    'username': config.SLACK_USERNAME,
                    'text': notification,
                    'icon_emoji': ':google:'
                })
            }
            r = requests.post(
                config.SLACK_HOOKS_SERVICE,
                data=payload,
            )

    def run(self):
        '''
        Run routine
        '''
        self.get_last_run()
        self.cleanup()
        self.find_new_events()
        self.set_last_run()

if __name__ == '__main__':
    a = GCPStatusToSlack()
    a.run()
