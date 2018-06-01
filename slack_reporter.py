import sys
import os
import json
from slackclient import SlackClient

SLACK_TOKEN = os.environ["SLACK_TOKEN"]
slack_client = SlackClient(SLACK_TOKEN)
api_call = slack_client.api_call("im.list")
user_slack_id = "horensan"


sc = SlackClient(SLACK_TOKEN)

data = json.load(sys.stdin)
output = data['output']
stdout = data['stdout']
stderr = data['stderr']
exitCode = data['exitCode']

sc.api_call(
  "chat.postMessage",
  channel="#horenkun-test",
  text=output
)
