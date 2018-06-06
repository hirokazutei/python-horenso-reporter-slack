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
    SLACK_CHANNEL = "#horenkun-test"

try:
    SLACK_REPORT_ITEMS = os.environ["SLACK_REPORT_ITEMS"]
except Exception:
    SLACK_REPORT_ITEMS = ['stdout', 'stderr', 'startAt', 'endAt']

data = json.load(sys.stdin)

carrier = []
errors = []
if 'stdout' in SLACK_REPORT_ITEMS:
    try:
        jsondata = json.loads(data['tdout'])
        stdout = json.dumps(jsondata, indent=8)
    except Exception:
        stdout = data['stdout']
    load = {
        "title": "StdOut",
        "value": stdout
    }
    carrier.append(load)
if 'stderr' in SLACK_REPORT_ITEMS:
    try:
        jsondata = json.loads(data['stderr'])
        stderr = json.dumps(jsondata, indent=8)
    except Exception:
        stderr = data['stderr']
    load = {
        "title": "StdErr",
        "value": stderr
    }
    carrier.append(load)
if 'result' in SLACK_REPORT_ITEMS:
    try:
        jsondata = json.loads(data['result'])
        result = json.dumps(jsondata, indent=8)
    except Exception:
        result = data['result']
    load = {
        "title": "Result",
        "value": result
    }
    carrier.append(load)
if 'output' in SLACK_REPORT_ITEMS:
    try:
        jsondata = json.loads(data['output'])
        output = json.dumps(jsondata, indent=8)
    except Exception:
        output = data['output']
    load = {
        "title": "Output",
        "value": output
    }
    carrier.append(load)
if 'hostname' in SLACK_REPORT_ITEMS:
    hostname = data['hostname']
    load = {
        "title": "Hostname",
        "value": hostname,
        "short": True
    }
    carrier.append(load)
if 'signaled' in SLACK_REPORT_ITEMS:
    signaled = data['signaled']
    load = {
        "title": "Signaled",
        "value": signaled
    }
    carrier.append(load)
if 'commandArgs' in SLACK_REPORT_ITEMS:
    commandArgs = data['commandArgs']
    load = {
        "title": "Command Args",
        "value": commandArgs
    }
    carrier.append(load)
if 'pid' in SLACK_REPORT_ITEMS:
    pid = data['pid']
    load = {
        "title": "PID",
        "value": pid,
        "short": True
    }
    carrier.append(load)
if 'userTime' in SLACK_REPORT_ITEMS:
    userTime = data['userTime']
    load = {
        "title": "userTime",
        "value": userTime,
        "short": True
    }
    carrier.append(load)
if 'systemTime' in SLACK_REPORT_ITEMS:
    systemTime = data['systemTime']
    load = {
        "title": "systemTime",
        "value": systemTime,
        "short": True
    }
    carrier.append(load)
if 'startAt' in SLACK_REPORT_ITEMS:
    try:
        startAt = parser.parse(data['startAt']).strftime('%y/%m/%d/ %H:%M:%S')
    except Exception as error:
        errors.append(str(error))
        startAt = data['startAt']
    load = {
        "title": "Start At:",
        "value": startAt,
        "short": True
    }
    carrier.append(load)
if 'endAt' in SLACK_REPORT_ITEMS:
    try:
        endAt = parser.parse(data['endAt']).strftime('%y/%m/%d/ %H:%M:%S')
    except Exception as error:
        errors.append(str(error))
        endAt = data['endAt']
    load = {
        "title": "End At:",
        "value": endAt,
        "short": True
    }
    carrier.append(load)

if errors:
    load = {
        "title": "Time Parse Error",
        "value": str(errors)
    }
    carrier.append(load)

command = data['command']
exitCode = data['exitCode']
if exitCode == 0 and SLACK_NOTIFICATION_MUTE_LEVEL == 0:
    icon_emoji = SLACK_SUCCESS_EMOJI
    text = "*PASSED*\nExit Code: {}\nCommand: `{}`".format(exitCode, command)
    color = '#00FA23'
elif exitCode == 1 and SLACK_NOTIFICATION_MUTE_LEVEL <= 1:
    icon_emoji = SLACK_ERROR_EMOJI
    text = "*ERROR*\nExit Code: {}\nCommand: `{}`".format(exitCode, command)
    color = '#FF6600'
elif exitCode >= 2 and SLACK_NOTIFICATION_MUTE_LEVEL <= 2:
    icon_emoji = SLACK_MAJOR_ERROR_EMOJI
    text = "*CRITICAL ERROR*\nExit Code: {}\nCommand: `{}`".format(exitCode, command)
    color = '#B40000'

payload = json.dumps([
    {
        "fallback": "Message Error",
        "color": color,
        "attachment_type": "default",
        "footer_icon": "https://cdn0.iconfinder.com/data/icons/veggie/64/spinach-256.png",
        "footer": "Horenso Report",
        "fields": carrier
    }], indent=4)

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
