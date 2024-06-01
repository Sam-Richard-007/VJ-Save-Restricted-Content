import pyrogram
from pyrogram import Client, filters
from pyrogram.errors import UserAlreadyParticipant, InviteHashExpired, UsernameNotOccupied, FloodWait
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton

import time
import os
import threading
import json
from os import environ

bot_token = environ.get("TOKEN", "YOUR_BOT_TOKEN")
api_hash = environ.get("HASH", "YOUR_API_HASH")
api_id = int(environ.get("ID", "YOUR_API_ID"))
bot = Client("mybot", api_id=api_id, api_hash=api_hash, bot_token=bot_token)

ss = environ.get("STRING", "YOUR_STRING_SESSION")
if ss is not None:
    acc = Client("myacc", api_id=api_id, api_hash=api_hash, session_string=ss)
    acc.start()
else:
    acc = None

# download status
def downstatus(statusfile, message):
    while True:
        if os.path.exists(statusfile):
            break

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
    while True:
        if os.path.exists(statusfile):
            break

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

# Add channel joining functionality
@bot.on_message(filters.command(["joinchannel"]))
def join_channel(client: pyrogram.client.Client, message: pyrogram.types.messages_and_media.message.Message):
    if len(message.command) != 2:
        bot.send_message(message.chat.id, "**Usage:** /joinchannel <invite link>", reply_to_message_id=message.id)
        return

    invite_link = message.command[1]
    if acc is None:
        bot.send_message(message.chat.id, f"**String Session is not Set**", reply_to_message_id=message.id)
        return

    try:
        acc.join_chat(invite_link)
        bot.send_message(message.chat.id, "**Channel Joined**", reply_to_message_id=message.id)
    except UserAlreadyParticipant:
        bot.send_message(message.chat.id, "**Already a member of the channel**", reply_to_message_id=message.id)
    except InviteHashExpired:
        bot.send_message(message.chat.id, "**Invalid Link**", reply_to_message_id=message.id)
    except Exception as e:
        bot.send_message(message.chat.id, f"**Error** : __{e}__", reply_to_message_id=message.id)

@bot.on_message(filters.text)
def save(client: pyrogram.client.Client, message: pyrogram.types.messages_and_media.message.Message):
    print(message.text)

    # joining chats
    if "https://t.me/+" in message.text or "https://t.me/joinchat/" in message.text:
        if acc is None:
            bot.send_message(message.chat.id, f"**String Session is not Set**", reply_to_message_id=message.id)
            return

        try:
            acc.join_chat(message.text)
            bot.send_message(message.chat.id, "**Chat Joined**", reply_to_message_id=message.id)
        except UserAlreadyParticipant:
            bot.send_message(message.chat.id, "**Chat already Joined**", reply_to_message_id=message.id)
        except InviteHashExpired:
            bot.send_message(message.chat.id, "**Invalid Link**", reply_to_message_id=message.id)
        except Exception as e:
            bot.send_message(message.chat.id, f"**Error** : __{e}__", reply_to_message_id=message.id)

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
                handle_private(message, chatid, msgid, forward_to_channel=True)

            # bot
            elif "https://t.me/b/" in message.text:
                username = datas[4]
                if acc is None:
                    bot.send_message(message.chat.id, f"**String Session is not Set**", reply_to_message_id=message.id)
                    return
                try:
                    handle_private(message, username, msgid, forward_to_channel=True)
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
                    bot.copy_message(message.chat.id, msg.chat.id, msg.id, reply_to_message_id=message.id)
                except:
                    if acc is None:
                        bot.send_message(message.chat.id, f"**String Session is not Set**", reply_to_message_id=message.id)
                        return
                    try:
                        handle_private(message, username, msgid, forward_to_channel=True)
                    except Exception as e:
                        bot.send_message(message.chat.id, f"**Error** : __{e}__", reply_to_message_id=message.id)

            # wait time
            time.sleep(3)

# handle private
def handle_private(message: pyrogram.types.messages_and_media.message.Message, chatid: int, msgid: int, forward_to_channel=False):
    try:
        msg: pyrogram.types.messages_and_media.message.Message = acc.get_messages(chatid, msgid)
        msg_type = get_message_type(msg)

        if "Text" == msg_type:
            bot.send_message(message.chat.id, msg.text, entities=msg.entities, reply_to_message_id=message.id)
            return

        smsg = bot.send_message(message.chat.id, '__Downloading__', reply_to_message_id=message.id)
        dosta = threading.Thread(target=lambda: downstatus(f'{message.id}downstatus.txt', smsg), daemon=True)
        dosta.start()
        file = acc.download_media(msg, progress=progress, progress_args=[message, "down"])
        os.remove(f'{message.id}downstatus.txt')

        upsta = threading.Thread(target=lambda: upstatus(f'{message.id}upstatus.txt', smsg), daemon=True)
        upsta.start()

        caption = msg.caption if msg.caption else ""
        if "Document" == msg_type:
            if forward_to_channel:
                bot.send_document(DEST_CHANNEL_ID, file, caption=caption, progress=progress, progress_args=[message, "up"])
            else:
                bot.send_document(message.chat.id, file, caption=caption, reply_to_message_id=message.id, progress=progress, progress_args=[message, "up"])

        elif "Video" == msg_type:
            if forward_to_channel:
                bot.send_video(DEST_CHANNEL_ID, file, caption=caption, progress=progress, progress_args=[message, "up"])
            else:
                bot.send_video(message.chat.id, file, caption=caption, reply_to_message_id=message.id, progress=progress, progress_args=[message, "up"])

        elif "Animation" == msg_type:
            if forward_to_channel:
                bot.send_animation(DEST_CHANNEL_ID, file, caption=caption, progress=progress, progress_args=[message, "up"])
            else:
                bot.send_animation(message.chat.id, file, caption=caption, reply_to_message_id=message.id, progress=progress, progress_args=[message, "up"])

        elif "Sticker" == msg_type:
            if forward_to_channel:
                bot.send_sticker(DEST_CHANNEL_ID, file, progress=progress, progress_args=[message, "up"])
            else:
                bot.send_sticker(message.chat.id, file, reply_to_message_id=message.id, progress=progress, progress_args=[message, "up"])

        elif "Voice" == msg_type:
            if forward_to_channel:
                bot.send_voice(DEST_CHANNEL_ID, file, caption=caption, progress=progress, progress_args=[message, "up"])
            else:
                bot.send_voice(message.chat.id, file, caption=caption, reply_to_message_id=message.id, progress=progress, progress_args=[message, "up"])

        elif "Audio" == msg_type:
            if forward_to_channel:
                bot.send_audio(DEST_CHANNEL_ID, file, caption=caption, progress=progress, progress_args=[message, "up"])
            else:
                bot.send_audio(message.chat.id, file, caption=caption, reply_to_message_id=message.id, progress=progress, progress_args=[message, "up"])

        elif "Photo" == msg_type:
            if forward_to_channel:
                bot.send_photo(DEST_CHANNEL_ID, file, caption=caption, progress=progress, progress_args=[message, "up"])
            else:
                bot.send_photo(message.chat.id, file, caption=caption, reply_to_message_id=message.id, progress=progress, progress_args=[message, "up"])

        try:
            os.remove(f'{message.id}upstatus.txt')
        except FileNotFoundError:
            pass
        os.remove(file)
        bot.delete_messages(message.chat.id, smsg.id)
    except FloodWait as e:
        wait_time = e.x
        bot.send_message(message.chat.id, f"Flood wait error. Waiting for {wait_time} seconds.")
        time.sleep(wait_time)
        handle_private(message, chatid, msgid, forward_to_channel)
    except FileNotFoundError as e:
        bot.send_message(message.chat.id, f"File not found error: {e}")
    except Exception as e:
        bot.send_message(message.chat.id, f"An unexpected error occurred: {e}")

# get message type
def get_message_type(msg: pyrogram.types.messages_and_media.message.Message) -> str:
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

    return "Text"

USAGE = """**FOR PUBLIC CHATS**
`https://t.me/username/2` - `https://t.me/username/2-100`
`https://t.me/c/12345678/2` - `https://t.me/c/12345678/2-100`

**FOR BOTS**
`https://t.me/b/username/2` - `https://t.me/b/username/2-100`

**FOR PRIVATE CHATS**
`https://t.me/c/12345678/2` - `https://t.me/c/12345678/2-100`

**JOIN CHAT USING LINK**
`https://t.me/+/link` - `https://t.me/joinchat/link`
"""

DEST_CHANNEL_ID = -1001234567890  # Replace with your channel's ID

bot.run()
