import pyrogram
from pyrogram import Client, filters
from pyrogram.errors import UserAlreadyParticipant, InviteHashExpired, UsernameNotOccupied, FloodWait, RPCError
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton

import time
import os
import threading
import json
from os import environ
from queue import Queue

bot_token = environ.get("TOKEN", "6791074208:AAF5wiKiAtGx0FPgQbCjGW52WgdRbPjFngg")
api_hash = environ.get("HASH", "84328889c4abb393ea32a1943a9648ec")
api_id = int(environ.get("ID", "25914518"))
bot = Client("mybot", api_id=api_id, api_hash=api_hash, bot_token=bot_token)

ss = environ.get("STRING", "BQGLbJYAihPH61mkIZ3iYuJwgDXWsE15D2Ooja3eMUiNd6BriLWuIEX2lEEJdNK6zZ4Zlp_MJ-O6xCdkURiY2f00nBUG-c9yKozZmu_Cfqc-KM3xA1Y8OHZyA176E6aPJg9ld_hnpkV7wPxGVgxBKaUvGiiCjUm6OiUCD0z06tHSPEBNq5BXGqwgYHrFmJwpOPTCqu9Oi_1zr9GK5ocDhf5X3mj0iJaWKa3vAI9jmPrDfHruSpYe76bGHCSlDbvFzm8hNQ8k2pYIyA_1l9RGAoMeGKhufVWdSgCica5qHHYFgkxX4W_y6imZoJNemPh7WH0Kjj37vjkXhwYAAhIXCjz9U-prMgAAAAGTYo2SAA")
if ss is not None:
    acc = Client("myacc", api_id=api_id, api_hash=api_hash, session_string=ss)
    acc.start()
else:
    acc = None

# Load channel ID from file or environment variable
def load_channel_id():
    try:
        with open("channel_id.txt", "r") as file:
            return int(file.read().strip())
    except:
        return int(environ.get("NEW_CHANNEL_ID", "0"))

# Save channel ID to file
def save_channel_id(channel_id):
    with open("channel_id.txt", "w") as file:
        file.write(str(channel_id))

new_channel_id = load_channel_id()

# Queue to manage messages
message_queue = Queue()

# download status
def downstatus(statusfile, message):
    while not os.path.exists(statusfile):
        time.sleep(3)

    while os.path.exists(statusfile):
        with open(statusfile, "r") as downread:
            txt = downread.read()
        try:
            bot.edit_message_text(message.chat.id, message.id, f"__Downloaded__ : **{txt}**")
            time.sleep(10)
        except:
            time.sleep(5)

# upload status
def upstatus(statusfile, message):
    while not os.path.exists(statusfile):
        time.sleep(3)

    while os.path.exists(statusfile):
        with open(statusfile, "r") as upread:
            txt = upread.read()
        try:
            bot.edit_message_text(message.chat.id, message.id, f"__Uploaded__ : **{txt}**")
            time.sleep(10)
        except:
            time.sleep(5)

# progress writer
def progress(current, total, message, type):
    with open(f'{message.id}{type}status.txt', "w") as fileup:
        fileup.write(f"{current * 100 / total:.1f}%")

# start command
@bot.on_message(filters.command(["start"]))
def send_start(client: pyrogram.client.Client, message: pyrogram.types.messages_and_media.message.Message):
    bot.send_message(message.chat.id, f"**__👋 Hi** **{message.from_user.mention}**, **I am Save Restricted Bot, I can send you restricted content by its post link__**\n\n{USAGE}",
                     reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🌐 Update Channel", url="https://t.me/VJ_Botz")]]), reply_to_message_id=message.id)

# Set channel ID command
@bot.on_message(filters.command(["setchannel"]) & filters.forwarded)
def set_channel(client: pyrogram.client.Client, message: pyrogram.types.messages_and_media.message.Message):
    global new_channel_id
    if message.forward_from_chat:
        new_channel_id = message.forward_from_chat.id
        save_channel_id(new_channel_id)
        bot.send_message(message.chat.id, f"**Channel ID set to:** `{new_channel_id}`", reply_to_message_id=message.id)
    else:
        bot.send_message(message.chat.id, "**Please forward a message from the target channel to set it.**", reply_to_message_id=message.id)

@bot.on_message(filters.text)
def save(client: pyrogram.client.Client, message: pyrogram.types.messages_and_media.message.Message):
    print(message.text)

    # joining chats
    if "https://t.me/+" in message.text or "https://t.me/joinchat/" in message.text:
        if acc is None:
            bot.send_message(message.chat.id, f"**String Session is not Set**", reply_to_message_id=message.id)
            return

        try:
            try:
                acc.join_chat(message.text)
            except Exception as e:
                bot.send_message(message.chat.id, f"**Error** : __{e}__", reply_to_message_id=message.id)
                return
            bot.send_message(message.chat.id, "**Chat Joined**", reply_to_message_id=message.id)
        except UserAlreadyParticipant:
            bot.send_message(message.chat.id, "**Chat already Joined**", reply_to_message_id=message.id)
        except InviteHashExpired:
            bot.send_message(message.chat.id, "**Invalid Link**", reply_to_message_id=message.id)

    # getting message
    elif "https://t.me/" in message.text:
        datas = message.text.split("/")
        temp = datas[-1].replace("?single", "").split("-")
        fromID = int(temp[0].strip())
        try:
            toID = int(temp[1].strip())
        except:
            toID = fromID

        for msgid in range(fromID, toID + 1):
            # private
            if "https://t.me/c/" in message.text:
                chatid = int("-100" + datas[4])

                if acc is None:
                    bot.send_message(message.chat.id, f"**String Session is not Set**", reply_to_message_id=message.id)
                    return

                message_queue.put((message, chatid, msgid))

            # bot
            elif "https://t.me/b/" in message.text:
                username = datas[4]

                if acc is None:
                    bot.send_message(message.chat.id, f"**String Session is not Set**", reply_to_message_id=message.id)
                    return
                try:
                    message_queue.put((message, username, msgid))
                except Exception as e:
                    bot.send_message(message.chat.id, f"**Error** : __{e}__", reply_to_message_id=message.id)

            # public
            else:
                username = datas[3]

                try:
                    msg = bot.get_messages(username, msgid)
                except UsernameNotOccupied:
                    bot.send_message(message.chat.id, f"**The username is not occupied by anyone**", reply_to_message_id=message.id)
                    return

                try:
                    bot.copy_message(new_channel_id, msg.chat.id, msg.id)
                except Exception as e:
                    if acc is None:
                        bot.send_message(message.chat.id, f"**String Session is not Set**", reply_to_message_id=message.id)
                        return
                    try:
                        message_queue.put((message, username, msgid))
                    except Exception as e:
                        bot.send_message(message.chat.id, f"**Error** : __{e}__", reply_to_message_id=message.id)

            # wait time
            time.sleep(1)

# Process the message queue
def process_queue():
    while True:
        message, chatid, msgid = message_queue.get()
        try:
            handle_private(message, chatid, msgid)
        except FloodWait as e:
            time.sleep(e.x)
            message_queue.put((message, chatid, msgid))
        except RPCError as e:
            bot.send_message(message.chat.id, f"**RPC Error** : __{e}__", reply_to_message_id=message.id)
        finally:
            message_queue.task_done()

# handle private
def handle_private(message: pyrogram.types.messages_and_media.message.Message, chatid: int, msgid: int):
    try:
        msg = acc.get_messages(chatid, msgid)
    except FloodWait as e:
        time.sleep(e.x)
        msg = acc.get_messages(chatid, msgid)
    except RPCError as e:
        bot.send_message(message.chat.id, f"**RPC Error** : __{e}__", reply_to_message_id=message.id)
        return

    msg_type = get_message_type(msg)

    if "Text" == msg_type:
        bot.send_message(new_channel_id, msg.text, entities=msg.entities)
        return

    smsg = bot.send_message(message.chat.id, '__Downloading__', reply_to_message_id=message.id)
    dosta = threading.Thread(target=lambda: downstatus(f'{message.id}downstatus.txt', smsg), daemon=True)
    dosta.start()
    try:
        file = acc.download_media(msg, progress=progress, progress_args=[message, "down"])
    except FloodWait as e:
        time.sleep(e.x)
        file = acc.download_media(msg, progress=progress, progress_args=[message, "down"])
    os.remove(f'{message.id}downstatus.txt')

    upsta = threading.Thread(target=lambda: upstatus(f'{message.id}upstatus.txt', smsg), daemon=True)
    upsta.start()

    if "Document" == msg_type:
        try:
            thumb = acc.download_media(msg.document.thumbs[0].file_id)
        except:
            thumb = None

        bot.send_document(new_channel_id, file, thumb=thumb, caption=msg.caption, caption_entities=msg.caption_entities, progress=progress, progress_args=[message, "up"])
        if thumb is not None:
            os.remove(thumb)

    elif "Video" == msg_type:
        try:
            thumb = acc.download_media(msg.video.thumbs[0].file_id)
        except:
            thumb = None

        bot.send_video(new_channel_id, file, duration=msg.video.duration, width=msg.video.width, height=msg.video.height, thumb=thumb, caption=msg.caption, caption_entities=msg.caption_entities, progress=progress, progress_args=[message, "up"])
        if thumb is not None:
            os.remove(thumb)

    elif "Animation" == msg_type:
        bot.send_animation(new_channel_id, file, caption=msg.caption, caption_entities=msg.caption_entities, progress=progress, progress_args=[message, "up"])

    elif "Sticker" == msg_type:
        bot.send_sticker(new_channel_id, file, progress=progress, progress_args=[message, "up"])

    elif "Voice" == msg_type:
        bot.send_voice(new_channel_id, file, caption=msg.caption, caption_entities=msg.caption_entities, progress=progress, progress_args=[message, "up"])

    elif "Audio" == msg_type:
        try:
            thumb = acc.download_media(msg.audio.thumbs[0].file_id)
        except:
            thumb = None

        bot.send_audio(new_channel_id, file, caption=msg.caption, caption_entities=msg.caption_entities, progress=progress, progress_args=[message, "up"])
        if thumb is not None:
            os.remove(thumb)

    elif "Photo" == msg_type:
        bot.send_photo(new_channel_id, file, caption=msg.caption, caption_entities=msg.caption_entities)

    os.remove(file)
    if os.path.exists(f'{message.id}upstatus.txt'):
        os.remove(f'{message.id}upstatus.txt')
    bot.delete_messages(message.chat.id, [smsg.id])

# get the type of message
def get_message_type(msg: pyrogram.types.messages_and_media.message.Message):
    try:
        msg.document.file_id
        return "Document"
    except:
        pass

    try:
        msg.video.file_id
        return "Video"
    except:
        pass

    try:
        msg.animation.file_id
        return "Animation"
    except:
        pass

    try:
        msg.sticker.file_id
        return "Sticker"
    except:
        pass

    try:
        msg.voice.file_id
        return "Voice"
    except:
        pass

    try:
        msg.audio.file_id
        return "Audio"
    except:
        pass

    try:
        msg.photo.file_id
        return "Photo"
    except:
        pass

    try:
        msg.text
        return "Text"
    except:
        pass

USAGE = """**FOR PUBLIC CHATS**

**__just send post/s link__**

**FOR PRIVATE CHATS**

**__first send invite link of the chat (unnecessary if the account of string session already member of the chat)
then send post/s link__**

**FOR BOT CHATS**

**__send link with** '/b/', **bot's username and message id, you might want to install some unofficial client to get the id like below__**


https://t.me/b/botusername/4321


**MULTI POSTS**

**__send public/private posts link as explained above with format "from - to" to send multiple messages like below__**

https://t.me/xxxx/1001-1010

https://t.me/c/xxxx/101 - 120


**__note that space in between doesn't matter__**
"""

# Start processing the queue in a separate thread
queue_thread = threading.Thread(target=process_queue, daemon=True)
queue_thread.start()

# infinite polling
bot.run()
