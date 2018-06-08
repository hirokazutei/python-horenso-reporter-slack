import sys
import os
import json
from dateutil import parser
from slackclient import SlackClient


def parseTime(time):
    try:
        time_parsed = parser.parse(time).strftime('%y/%m/%d/ %H:%M:%S')
    except (ValueError, AttributeError) as error:
        return time, str(error)
    except (ModuleNotFoundError) as error:
        return time, "there seems to be a problem with dateutil.\n\
                      If you are using Python3, make sure to pip install py-dateutil"
    return time_parsed, None


def jsonfy(output):
    try:
        jsondata = json.loads(output)
        pretty_json = json.dumps(jsondata, indent=8)
    except ValueError as error:
        return output, error
    except TypeError as error:
        return output, error
    return pretty_json, None


if __name__ == '__main__':
    SLACK_TOKEN = os.environ["SLACK_TOKEN"]
    assert SLACK_TOKEN, "token not set in environment variable"
    slack_client = SlackClient(SLACK_TOKEN)
    api_call = slack_client.api_call("im.list")
    sc = SlackClient(SLACK_TOKEN)

    SLACK_SUCCESS_EMOJI = os.getenv("SLACK_SUCCESS_EMOJI", ":white_check_mark:")
    SLACK_ERROR_EMOJI = os.getenv("SLACK_ERROR_EMOJI", ":warning:")
    SLACK_MAJOR_ERROR_EMOJI = os.getenv("SLACK_MAJOR_ERROR_EMOJI", ":no_entry:")
    SLACK_NOTIFICATION_MUTE_LEVEL = int(os.getenv("SLACK_NOTIFICATION_MUTE_LEVEL", 0))
    SLACK_CHANNEL = os.getenv("SLACK_CHANNEL", "#general")
    SLACK_REPORT_ITEMS = os.getenv("SLACK_REPORT_ITEMS", ['stdout', 'stderr', 'startAt', 'endAt'])
    SLACK_FORMAT_ERROR = os.getenv("SLACK_FORMAT_ERROR", False)

    data = json.load(sys.stdin)

    carrier = []
    errors = []
    if 'stdout' in SLACK_REPORT_ITEMS:
        stdout, error = jsonfy(data['stdout'])
        if error:
            errors.append(error)
        load = {
            "title": "Standard Output",
            "value": stdout
        }
        carrier.append(load)
    if 'stderr' in SLACK_REPORT_ITEMS:
        stderr, error = jsonfy(data['stderr'])
        if error:
            errors.append(error)
        load = {
            "title": "Standard Error",
            "value": stderr
        }
        carrier.append(load)
    if 'result' in SLACK_REPORT_ITEMS:
        result, error = jsonfy(data['result'])
        if error:
            errors.append(error)
        load = {
            "title": "Result",
            "value": result
        }
        carrier.append(load)
    if 'output' in SLACK_REPORT_ITEMS:
        output, error = jsonfy(data['output'])
        if error:
            errors.append(error)
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
            "title": "Command Arguments",
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
            "title": "User Time",
            "value": userTime,
            "short": True
        }
        carrier.append(load)
    if 'systemTime' in SLACK_REPORT_ITEMS:
        systemTime = data['systemTime']
        load = {
            "title": "System Time",
            "value": systemTime,
            "short": True
        }
        carrier.append(load)
    if 'startAt' in SLACK_REPORT_ITEMS:
        startAt, error = parseTime(data['startAt'])
        if error:
            errors.append(error)
        load = {
            "title": "Start At:",
            "value": startAt,
            "short": True
        }
        carrier.append(load)
    if 'endAt' in SLACK_REPORT_ITEMS:
        endAt, error = parseTime(data['endAt'])
        if error:
            errors.append(error)
        load = {
            "title": "End At:",
            "value": endAt,
            "short": True
        }
        carrier.append(load)

    if errors and SLACK_FORMAT_ERROR:
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
