import smtplib

from datetime import datetime
from email.mime.text import MIMEText
from requests import post

from CTFd.utils import get_config, get_app_config


def alert_cheater(cheater, reason=None):
    """
    Alert us that some team cheated, and optionally why we think so.
    By default this prints to stdout, and sends a message to a slack channel defined by some config vars:
        - SLACK_WEBHOOK_URL: webhook url to post messages to for slack

    If the slack variable is not set, we will not enable slack posting.
    """
    when = datetime.utcnow()
    cheatmsg = '[{} (UTC)] CHEATER DETECTED: `{}`, reason: {}'.format(when, cheater.name, reason)
    print(cheatmsg)
    # post to slack if available
    webhook_url = get_config('SLACK_WEBHOOK_URL')
    if webhook_url:
        post(webhook_url, json={'text':cheatmsg})

    # and/or email
    to_addrs = get_app_config('ALERT_EMAIL_RCPT_ADDRS')
    from_addr = get_config('MAILFROM_ADDR') or 'alerts@osiris.cyber.nyu.edu'
    email_subj = get_app_config('ALERT_EMAIL_SUBJECT') or 'CTFd Cheater Alert'
    if to_addrs:
        msg = MIMEText(cheatmsg)
        msg['Subject'] = email_subj
        srvr = smtplib.SMTP('localhost')
        try:
            srvr.sendmail(from_addr, to_addrs, msg.as_string())
        finally:
            srvr.quit()
