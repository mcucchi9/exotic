import os
from slackclient import SlackClient

# instantiate Slack client
sc = SlackClient(os.environ.get('SLACK_BOT_TOKEN'))

sc.api_call(
"chat.postMessage",
channel="#general",
text="Hello from Python!"
)