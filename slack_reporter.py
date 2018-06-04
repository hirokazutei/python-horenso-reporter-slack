import sys
import os
import json
from slackclient import SlackClient

SLACK_TOKEN = os.environ["SLACK_TOKEN"]

SLACK_SUCCESS_EMOJI = os.environ["SLACK_SUCCESS_EMOJI"]\
    if os.environ["SLACK_SUCCESS_EMOJI"] else ":white_check_mark:"
SLACK_ERROR_EMOJI = os.environ["SLACK_ERROR_EMOJI"]\
    if os.environ["SLACK_ERROR_EMOJI"] else ":warning:"
SLACK_MAJOR_ERROR_EMOJI = os.environ["SLACK_MAJOR_ERROR_EMOJI"]\
    if os.environ["SLACK_MAJOR_ERROR_EMOJI"] else ":no_entry:"
SLACK_NOTIFICATION_MUTE_LEVEL = int(os.environ["SLACK_NOTIFICATION_MUTE_LEVEL"])\
    if os.environ["SLACK_NOTIFICATION_MUTE_LEVEL"] else 0
SLACK_CHANNEL = os.environ["SLACK_CHANNEL"]\
    if os.environ["SLACK_CHANNEL"] else "#general"

slack_client = SlackClient(SLACK_TOKEN)
api_call = slack_client.api_call("im.list")


sc = SlackClient(SLACK_TOKEN)

data = json.load(sys.stdin)
stdout = data['stdout']
stderr = data['stderr']
command = data['command']
exitCode = data['exitCode']

if exitCode == 0 and SLACK_NOTIFICATION_MUTE_LEVEL == 0:
    icon_emoji = SLACK_SUCCESS_EMOJI
    text = "Exit Code: {}\n`{}` executed successfully.\n# OUTPUT\n{}".format(exitCode, command, stdout)
elif exitCode == 1 and SLACK_NOTIFICATION_MUTE_LEVEL <= 1:
    icon_emoji = SLACK_ERROR_EMOJI
    text = "Exit Code: {}\n`{}` encountered an error:\n# ERROR\n{}".format(exitCode, command, stderr)
elif exitCode >= 2 and SLACK_NOTIFICATION_MUTE_LEVEL <= 2:
    icon_emoji = SLACK_MAJOR_ERROR_EMOJI
    text = "Exit Code: {}\n`{}` encountered a major error:\n# ERROR\n{}".format(exitCode, command, stderr)

response = sc.api_call(
    "chat.postMessage",
    icon_emoji=icon_emoji,
    channel=SLACK_CHANNEL,
    text=text,
)
if not response['ok']:
    sc.api_call(
        "chat.postMessage",
        icon_emoji=SLACK_MAJOR_ERROR_EMOJI,
        channel=SLACK_CHANNEL,
        text="Message Could Not Be Sent because of `{}`".format(response['error'])
    )

# as_user parameter removes the ability to use the icon
