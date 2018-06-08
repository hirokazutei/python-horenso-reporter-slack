# python-horenso-reporter-slack
A simple reporter for horenso with Python
![Demo Image](https://github.com/hirokazutei/python-horenso-reporter-slack/blob/master/demoimg.png)

# Usage
### Download horenso by Songmu [[GitHub](https://github.com/Songmu/horenso "GitHub page of Horenso")]
~~~
$ go get github.com/Songmu/horenso/cmd/horenso
~~~

### Download slack reporter
~~~
$ git clone https://github.com/hirokazutei/python-horenso-reporter-slack.git
~~~

### Set Environment Variables
~~~
$ export SLACK_TOKEN="<SLACK TOKEN>"
$ export SLACK_CHANNEL="<SLACK CHANNEL>"
$ export SLACK_SUCCESS_EMOJI="<SLACK EMOJI>"
$ export SLACK_ERROR_EMOJI="<SLACK EMOJI>"
$ export SLACK_MAJOR_ERROR_EMOJI="<SLACK EMOJI>"
$ export SLACK_NOTIFICATION_MUTE_LEVEL="<0 ~ 2>"
$ export SLACK_REPORT_ITEMS=['ITEMS','TO','REPORT']
$ export SLACK_FORMAT_ERROR=False
~~~

#### SLACK TOKEN
* Required, can be found on the Slack API page.

#### SLACK CHANNEL
* The name of the channel you would like to send the message to.
* Default is #general

#### SLACK SUCCESS EMOJI
* The icon used when the command runs without any errors.
* Default is :white_check_mark:

#### SLACK ERROR EMOJI
* The icon used when the command encounters an exit code of 1.
* Default is :warning:

#### SLACK MAJOR ERROR EMOJI
* The icon used when the command encounters an exit code of 2 or others.
* Default is :no_entry:

#### SLACK NOTIFICATION MUTE LEVEL
* A value between 0 and 2 inclusive.
* 0 displays all messages.
* 1 ignores commands successfully ran.
* 2 ignores commands successfully ran and regular errors.

#### SLACK NOTIFICATION MUTE LEVEL
* List of strings representing the items that one wishes to report
* Default is: `['stdout', 'stderr', 'startAt', 'endAt']`
* `exitCode` and `command` are reported as default. Change that in the code if you wish
  * Other Items:
    * `'systemTime'`
    * `'commandArgs'`
    * `'userTime'`
    * `'hostname'`
    * `'pid'`
    * `'signaled'`
    * `'result'`
    * `'output'`

#### SLACK FORMAT ERROR
* This is just to show if there were any errors in fornatting the outputs or time.
* Everything should still work even if errors occur during formatting.
* Default is set to `False`.

### Run horenso to get report on Slack
~~~
$ horenso -r "python DIR/slack_reporter.py" -- <COMMAND>
~~~

*Note: If you are using python3, you will need install dateutil*


### Future
* Mentions
* Proper bot support
* Pastebin/Fluend support
* Please suggest more
