##
## Telecord - Simple message forwarder from telegram to discord
##               with its image and reply
##

from discord_hooks import Webhook
from telethon import TelegramClient, events, utils
from imgurpython import ImgurClient
import base64
import json
import logging
import os
import requests

logging.basicConfig(level=logging.INFO, format='%(asctime)s %(name)-12s %(levelname)-8s %(message)s', datefmt='%m-%d %H:%M')
logger = logging.getLogger('telebagger')

with open('config.json') as config_file:
    config = json.load(config_file)

try:
    channels = config['channels']
    api_id = config['telegram']['api_id']
    api_hash = config['telegram']['api_hash']
    phone = config['telegram']['phone']
    loglevel = config['telegram']['loglevel']
    imgur_id = config['imgur']['api_id']
    imgur_hash = config['imgur']['api_hash']
except:
    logger.error('Error processing config file')

logger.setLevel(loglevel)

print('Connecting to Telegram...')
client = TelegramClient('leaker', api_id, api_hash).start()
img_cli = ImgurClient(imgur_id, imgur_hash)

@client.on(events.NewMessage())
async def handler(update):
    try:
        #prints peer ids of channels
        #result = await client.get_dialogs()
        #print("\n List of channels:")
        #for p in result:
        #    print(str(p.id + 2**32) + ": "+p.name)

        if str(update.message.to_id.channel_id) in channels:
            m = update.message
            media = m.media
            reply_msg = await m.get_reply_message()
            if reply_msg is None:
                text = "{}\n".format(m.message)
            else:
                text = "```REPLIED_TO:\n{}```{}\n".format(reply_msg.message, m.message)

            if media is not None and utils.get_extension(media) == '.jpg':
                logger.info("Will download image")
                download_res = await client.download_media(media, './downloads/')
                logger.info("Download done: {}".format(download_res))
                url = img_cli.upload_from_path(download_res, anon=True)['link']
                text += url + "\n"
                os.remove(download_res)
                logger.debug("File deleted")

            if not text == '':
                text += "=======================\n"
                msg = Webhook(channels[str(m.to_id.channel_id)], msg=text)
                msg.post()
                logger.info("Relaying Message from Channel ID: {}".format(update.message.to_id.channel_id))
            else:
                logger.debug('Ignoring empty message: {}'.format(update.message))
        else:
            logger.info("Ignoring Message from Channel ID: {}".format(update.message.to_id.channel_id))
    except:
        logger.debug('Exception occurred while handling:\n')
        logger.debug(update)

try:
    print('(Press Ctrl+C to stop this)')
    client.run_until_disconnected()
finally:
    client.disconnect()
