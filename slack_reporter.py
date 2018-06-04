import sys
import os
import json

from dateutil import parser
from slackclient import SlackClient

SLACK_TOKEN = os.environ["SLACK_TOKEN"]
slack_client = SlackClient(SLACK_TOKEN)
api_call = slack_client.api_call("im.list")
sc = SlackClient(SLACK_TOKEN)

try:
    SLACK_SUCCESS_EMOJI = os.environ["SLACK_SUCCESS_EMOJI"]
except Exception:
    SLACK_SUCCESS_EMOJI = ":white_check_mark:"

try:
    SLACK_ERROR_EMOJI = os.environ["SLACK_ERROR_EMOJI"]
except Exception:
    SLACK_ERROR_EMOJI = ":warning:"

try:
    SLACK_MAJOR_ERROR_EMOJI = os.environ["SLACK_MAJOR_ERROR_EMOJI"]
except Exception:
    SLACK_MAJOR_ERROR_EMOJI = ":no_entry:"

try:
    SLACK_NOTIFICATION_MUTE_LEVEL = int(os.environ["SLACK_NOTIFICATION_MUTE_LEVEL"])
except Exception:
    SLACK_NOTIFICATION_MUTE_LEVEL = 0

try:
    SLACK_CHANNEL = os.environ["SLACK_CHANNEL"]
except Exception:
    SLACK_CHANNEL = "#general"

data = json.load(sys.stdin)
stdout = data['stdout']
stderr = data['stderr']
command = data['command']
exitCode = data['exitCode']
startAt = parser.parse(data['startAt']).strftime('%y/%m/%d/ %H:%M:%S')
endAt = parser.parse(data['endAt']).strftime('%y/%m/%d/ %H:%M:%S')

if exitCode == 0 and SLACK_NOTIFICATION_MUTE_LEVEL == 0:
    icon_emoji = SLACK_SUCCESS_EMOJI
    text = "*PASSED*\nExit Code: {}\nCommand: `{}`".format(exitCode, command)
    title = "Output"
    message = stdout
    color = '#00FA23'
elif exitCode == 1 and SLACK_NOTIFICATION_MUTE_LEVEL <= 1:
    icon_emoji = SLACK_ERROR_EMOJI
    text = "*ERROR*\nExit Code: {}\nCommand: `{}`".format(exitCode, command)
    title = "Error"
    message = stderr
    color = '#FF6600'
elif exitCode >= 2 and SLACK_NOTIFICATION_MUTE_LEVEL <= 2:
    icon_emoji = SLACK_MAJOR_ERROR_EMOJI
    text = "*CRITICAL ERROR*\nExit Code: {}\nCommand: `{}`".format(exitCode, command)
    title = "Error"
    message = stderr
    color = '#B40000'

payload = json.dumps([
    {
        "text": str(SLACK_NOTIFICATION_MUTE_LEVEL),
        "title": title,
        "fallback": "Message Error",
        "color": color,
        "attachment_type": "default",
        "footer_icon": "https://cdn0.iconfinder.com/data/icons/veggie/64/spinach-256.png",
        "footer": "Horenso Report",
        "fields": [
            {
                "title": "Start At:",
                "value": startAt,
                "short": True
            },
            {
                "title": "End At:",
                "value": endAt,
                "short": True
            }
        ]
    }])

response = sc.api_call(
    "chat.postMessage",
    icon_emoji=icon_emoji,
    channel=SLACK_CHANNEL,
    text=text,
    attachments=payload
)
if not response['ok']:
    sc.api_call(
        "chat.postMessage",
        icon_emoji=SLACK_MAJOR_ERROR_EMOJI,
        channel=SLACK_CHANNEL,
        text="Message Could Not Be Sent because of `{}`".format(response['error'])
    )

# as_user parameter removes the ability to use the icon
# Add a method to download files
