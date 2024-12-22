
from pyrogram import Client, filters
from pyrogram.types import Message
from config import *
from pyrogram.types import Message, InputMediaPhoto, InputMediaVideo
import asyncio
# Initialize @LazyDeveloperr Instaloader 
from pyrogram import Client, filters
from pyrogram.types import Message
import re
from pyrogram import enums
from script import Script
import time
from collections import defaultdict
from lazydeveloper.database import db
from plugins.LazyDev_F_Sub import lazy_force_sub, is_subscribed
from plugins.terabox_lazydeveloper import download_from_terabox
user_tasks = {}
# user_message_count = {}
user_message_count = defaultdict(list)

LAZY_REGEX = re.compile(
    pattern=r'(https?:\/\/(?:www\.)?[-a-zA-Z0-9@:%._\+~#=]{1,256}\.[a-zA-Z0-9()]{1,6}\b(?:[-a-zA-Z0-9()@:%_\+.~#?&//=]*))(.*)?')

@Client.on_message(filters.private & filters.text & ~filters.forwarded & ~filters.command(['start','users','broadcast']))
async def handle_incoming_message(client: Client, message: Message):
    try:
        await client.send_chat_action(message.chat.id, enums.ChatAction.TYPING)
        user_id = message.from_user.id  # Get user ID dynamically
        # Extract the message text and user ID
            # if user_id not in ADMIN:
            #     await client.send_message(chat_id=message.chat.id, text=f"Sorry Sweetheart! cant talk to you \nTake permission from my Lover @LazyDeveloperr")
        if not await db.is_user_exist(user_id):
            await db.add_user(user_id)

        if (FORCE_SUB_CHANNEL or FORCE_SUB_CHANNEL2 or FORCE_SUB_CHANNEL3) and not await is_subscribed(client, message):
            # User is not subscribed to any of the required channels, trigger force_sub logic
            return await lazy_force_sub(client, message) 
      
        # Message rate-limiting logic
        current_time = time.time()
        # Ensure the user has a list of message timestamps initialized
        if user_id not in user_message_count:
            user_message_count[user_id] = []

        # Filter out messages older than 1 second
        user_messages = user_message_count[user_id]
        user_message_count[user_id] = [timestamp for timestamp in user_messages if current_time - timestamp <= 5]  # Keep only messages within the last second
        message_count = len(user_message_count[user_id])  # Count messages sent in the last second
        
        # Check if the user exceeds the allowed maximum number of messages in 1 second
        if message_count >= MAXIMUM_TASK:
            await message.reply(Script.PLUS_SPAM_TEXT.format(MAXIMUM_TASK))
            return
        
        # Append the current message timestamp
        user_message_count[user_id].append(current_time)
        
        # assuming text sent by user @LazyDeveloperr
        match = LAZY_REGEX.search(message.text.strip())
        if not match:
            # No URL found in the message, ask the user to send a URL
            await client.send_chat_action(message.chat.id, enums.ChatAction.TYPING)
            ass = await message.reply(Script.WARNING_TEXT)
            await asyncio.sleep(6)
            await ass.delete()
            return
        # Initialize task list for the user if not already present
        if user_id not in user_tasks:
            user_tasks[user_id] = []

        # Check if the user already has 3 active tasks
        if len(user_tasks[user_id]) >= MAXIMUM_TASK:
            await client.send_chat_action(message.chat.id, enums.ChatAction.TYPING)
            sorry_lazy_sms = await message.reply(f"⏳ ʏᴏᴜ ᴀʟʀᴇᴀᴅʏ ʜᴀᴠᴇ {MAXIMUM_TASK} ᴀᴄᴛɪᴠᴇ ᴅᴏᴡɴʟᴏᴀᴅs. ᴘʟᴇᴀsᴇ ᴡᴀɪᴛ ғᴏʀ ᴏɴᴇ ᴛᴏ ꜰɪɴɪsʜ ʙᴇғᴏʀᴇ ᴀddɪɴɢ ᴍᴏʀᴇ.")
            await asyncio.sleep(10)
            await sorry_lazy_sms.delete()
            return
        
        url = message.text.strip()
        asyncio.create_task(lazydeveloper_handle_url(client, message, url, user_id))
        return
    except Exception as lazyerror:
        print(f"error => {lazyerror}")

async def lazydeveloper_handle_url(client, message, url, user_id):
    try:
        await client.send_chat_action(message.chat.id, enums.ChatAction.TYPING)
        ok = await message.reply("🔄 ᴅᴇᴛᴇᴄᴛɪɴɢ ᴜʀʟ ᴛʏᴘᴇ ᴀɴᴅ ᴘʀᴏᴄᴇssɪɴɢ ᴛʜᴇ ᴅᴏᴡɴʟᴏᴀᴅ...")

        PLATFORM_HANDLERS = [
                'terabox.com', 'nephobox.com', '4funbox.com', 'mirrobox.com', 
                'momerybox.com', 'teraboxapp.com', '1024tera.com', 
                'terabox.app', 'gibibox.com', 'goaibox.com', 'terasharelink.com', 'teraboxlink.com'
                ]
        
        if not any(domain in url for domain in PLATFORM_HANDLERS):
            await message.reply_text("ᴘʟᴇᴀsᴇ sᴇɴᴅ ᴀ ᴠᴀʟɪᴅ ᴛᴇʀᴀʙᴏx ʟɪɴᴋ.")
            return
    
        # for platform in PLATFORM_HANDLERS.items():
        #     if platform in url: 
        await client.send_chat_action(message.chat.id, enums.ChatAction.TYPING)
        await ok.edit(f"Sure sir... 🚀!")
        # Create a task for the handler function
        lazytask = asyncio.create_task(download_from_terabox(client, message, url, "terabox"))
        user_tasks[user_id].append(lazytask)
        lazytask.add_done_callback(lambda t: asyncio.create_task(task_done_callback(client, message, user_id, t)))
        await ok.delete()
        # return
            
        # await client.send_chat_action(message.chat.id, enums.ChatAction.TYPING)
        # await ok.edit("😞 oᴏps! lᴏᴏks lɪᴋᴇ wᴇ'ʀᴇ nᴏᴛ frɪᴇnds wɪᴛʜ ᴛʜᴀᴛ lɪɴᴋ yᴇᴛ. 🌐\n💔 bᴜᴛ dᴏɴ'ᴛ wᴏʀʀʏ, wᴇ'ʀᴇ wᴏʀᴋɪɴɢ hᴀʀᴅ ᴛᴏ bʀɪɴɢ ɪᴛ ᴛᴏ ᴛʜᴇ pᴀʀᴛʏ! 🎉 \n\nsᴛᴀʏ ᴛᴜɴᴇᴅ! 👀")
        # await client.send_message(LOG_CHANNEL,
        #                         f"<b>🚨 ᴜɴᴋɴᴏᴡɴ ᴘʟᴀᴛꜰᴏʀᴍ ʟɪɴᴋ sᴇɴᴛ!</b>\n\n<b>ᴛʜᴇ ᴜsᴇʀ ᴇɴᴛᴇʀᴇᴅ ᴀ ʟɪɴᴋ ғʀᴏᴍ ᴀ ᴘʟᴀᴛꜰᴏʀᴍ ᴡᴇ ᴅᴏɴ'ᴛ ʀᴇᴄᴏɢɴɪᴢᴇ. ᴘʟᴇᴀsᴇ ᴄʜᴇᴄᴋ ᴛʜᴇ ʟɪɴᴋ ᴏʀ ᴜᴘᴅᴀᴛᴇ ᴏᴜʀ ᴘʟᴀᴛꜰᴏʀᴍ ʜᴀɴᴅʟᴇʀ.</b>\n\n⚡hᴇʀᴇ ɪs ᴛʜᴇ ʟɪɴᴋ::\n{url}\n\n👫ᴜsᴇʀ::{message.from_user.mention}\n\n<blockquote>🦋 with love {client.mention} 🍟</blockquote>",
        #                         disable_web_page_preview = True, 
        #                         parse_mode=enums.ParseMode.HTML)
    except Exception as e:
        # Handle any errors
        await ok.delete()
        await client.send_chat_action(message.chat.id, enums.ChatAction.TYPING)
        await client.send_message(message.chat.id, f"sᴏᴍᴇᴛʜɪɴɢ ᴡᴇɴᴛ ᴡʀᴏɴɢ...\nᴘʟᴇᴀsᴇ ᴛʀʏ ᴀɢᴀɪɴ ʟᴀᴛᴇʀ ᴏʀ ᴄᴏɴᴛᴀᴄᴛ ᴏᴡɴᴇʀ.")
        print(f"❌ An error occurred: {e}")

async def task_done_callback(client, message, user_id, t):
    try:
        await client.send_chat_action(message.chat.id, enums.ChatAction.TYPING)
        if user_id in user_tasks and t in user_tasks[user_id]:
            user_tasks[user_id].remove(t)

        # Notify the user
        await client.send_chat_action(message.chat.id, enums.ChatAction.TYPING)
        workdonemsg = await client.send_message(
            chat_id=message.chat.id,
            text="❤ ꜰᴇᴇʟ ꜰʀᴇᴇ ᴛᴏ sʜᴀʀᴇ ᴍᴇ ᴛᴏ ʏᴏᴜʀ ꜰʀɪᴇɴᴅ ᴄɪʀᴄʟᴇ..."
        )
        await asyncio.sleep(15)
        await client.send_chat_action(message.chat.id, enums.ChatAction.TYPING)
        await workdonemsg.delete()
    except KeyError:
        print(f"Task or user ID not found during task cleanup: {t}")
    except Exception as e:
        print(f"Error in task_done_callback: {e}")


@Client.on_message(filters.private & filters.forwarded)
async def handle_forwarded(client, message):
    try:
        user_id = message.from_user.id
        await client.send_chat_action(message.chat.id, enums.ChatAction.TYPING)
        ass = await message.reply(Script.NO_SPAM_TEXT)
        await asyncio.sleep(10)
        await ass.delete()
        return
    except Exception as lazyerror:
        print(f"Error occured : {lazyerror}")
