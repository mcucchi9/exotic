import os
from slackclient import SlackClient

# instantiate Slack client
sc = SlackClient(os.environ.get('SLACK_BOT_TOKEN'))

sc.api_call(
    "chat.postMessage",
    channel="#general",
    text="Hello from Python!"
)

with open('/home/marco/Pictures/prova.png', 'rb') as f:
    sc.api_call(
        "files.upload",
        channels='#general',
        filename='prova.png',
        title='prova',
        initial_comment='commento',
        file=f
    )