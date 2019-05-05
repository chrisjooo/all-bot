import os
from decouple import config
from flask import (
    Flask, request, abort
)
from linebot import (
    LineBotApi, WebhookHandler
)
from linebot.exceptions import InvalidSignatureError
from linebot.models import (
    MessageEvent, TextMessage, TextSendMessage,
)
app = Flask(__name__)
# get LINE_CHANNEL_ACCESS_TOKEN from your environment variable
line_bot_api = LineBotApi(
    config("LINE_CHANNEL_ACCESS_TOKEN",
           default=os.environ.get('LINE_ACCESS_TOKEN'))
)
# get LINE_CHANNEL_SECRET from your environment variable
handler = WebhookHandler(
    config("LINE_CHANNEL_SECRET",
           default=os.environ.get('LINE_CHANNEL_SECRET'))
)

bool echo = False

def get_source(event):
    if event.source.type == 'user':
        return {'line_bot_api':os.environ.get('line_bot_api', None), 'group_id':None, 'user_id':event.source.user_id}
    elif event.source.type == 'group':
        return {'line_bot_api':os.environ.get('line_bot_api', None), 'group_id':event.source.group_id, 'user_id':event.source.user_id}
    elif event.source.type == 'room':
        return {'line_bot_api':os.environ.get('line_bot_api', None), 'group_id':event.source.room_id, 'user_id':event.source.user_id}
    else:
        raise Exception('event.source.type:%s' % event.source.type)


@app.route("/callback", methods=['POST'])
def callback():
    signature = request.headers['X-Line-Signature']


    # get request body as text
    body = request.get_data(as_text=True)
    app.logger.info("Request body: " + body)


    # handle webhook body
    try:
        handler.handle(body, signature)
    except InvalidSignatureError:
        abort(400)


    return 'OK'


@handler.add(MessageEvent, message=TextMessage)
def handle_text_message(event):
    if echo :
        line_bot_api.reply_message(
                event.reply_token,
                TextSendMessage(text=event.message.text)
            )
    else :    
        if event.message.text == '!test' :
            line_bot_api.reply_message(
                event.reply_token,
                TextSendMessage(text='testing command')
            )
        elif event.message.text == '!echo' :
            echo = True   
        elif event.message.text == '!leave' :
            line_bot_api.leave_group(event.source.group_id)




if __name__ == "__main__":
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)