import requests
# import aria2p
from datetime import datetime
# from status import format_progress_bar
import asyncio
import os, time
import logging
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from lazydeveloper.lazyprogress import progress_for_pyrogram
from plugins.utitles import Mdata01

# aria2 = aria2p.API(
#     aria2p.Client(
#         host="http://localhost",
#         port=6800,
#         secret=""
#     )
# )

# options = {
#     "max-tries": "50",
#     "retry-wait": "3",
#     "continue": "true"
# }

# aria2.set_global_options(options)
from pyrogram import enums

from urllib.parse import urlparse

def extract_short_url(url):
    """
    Extracts the short URL (identifier) from a given TeraBox URL.

    Args:
        url (str): The TeraBox URL.

    Returns:
        str: The short URL (identifier).
    """
    # Parse the URL
    parsed_url = urlparse(url)
    
    # Extract the path and split to get the last part
    path_parts = parsed_url.path.strip('/').split('/')
    if len(path_parts) > 1 and path_parts[0] == "s":
        return path_parts[1]
    return None

async def download_from_terabox(client, message, url, platform):
    await client.send_chat_action(message.chat.id, enums.ChatAction.TYPING)
    progress_message2 = await message.reply("<i>⚙ ᴘʀᴇᴘᴀʀɪɴɢ\nᴀɴᴀʟʏsɪɴɢ yᴏᴜʀ ᴜʀʟ...</i>")
    TEMP_DOWNLOAD_FOLDER = f"./downloads/{message.from_user.id}/{time.time()}"
    if not os.path.exists(TEMP_DOWNLOAD_FOLDER):
        os.makedirs(TEMP_DOWNLOAD_FOLDER)
    # Using the temporary download folder
    destination_folder = TEMP_DOWNLOAD_FOLDER
    # -------------------------------------
    # -------------------------------------
    # -------------------------------------
    short_url = extract_short_url(url)
    print(f"Extracted Short URL: {short_url}")

    # Step 1: Fetch file info
    response = requests.get(f"https://terabox.hnn.workers.dev/api/get-info?shorturl={short_url}")
    response.raise_for_status()
    data = response.json()

    if data.get("ok") and "list" in data and len(data["list"]) > 0:
        video_info = data["list"][0]
        video_title = video_info.get("filename", "Untitled Video")
        video_size = int(video_info.get("size", 0))
        fs_id = video_info.get("fs_id")
        shareid = data.get("shareid")
        uk = data.get("uk")
        sign = data.get("sign")
        timestamp = data.get("timestamp")

        # Format the file size (human-readable)
        def format_file_size(size):
            units = ['B', 'KB', 'MB', 'GB', 'TB']
            unit_index = 0
            while size >= 1024 and unit_index < len(units) - 1:
                size /= 1024
                unit_index += 1
            return f"{size:.2f} {units[unit_index]}"

        file_size = format_file_size(video_size)

        # Notify user with file details
        file_info_message = (
            f"**Video Title:** {video_title}\n"
            f"**File Size:** {file_size}\n\n"
            "Starting download..."
        )
        await progress_message2.edit_text(file_info_message)
        await asyncio.sleep(1)
        
        # api
        api_url = "https://terabox.hnn.workers.dev/api/get-download"

        # Payload
        payload = {
            "fs_id": fs_id,
            "shareid": shareid,
            "sign": sign,
            "timestamp": timestamp,
            "uk": uk
        }

        # Headers
        headers = {
            "Content-Type": "application/json"
        }

        try:
            # Send POST Request
            response = requests.post(api_url, json=payload, headers=headers)
            response.raise_for_status()  # Raise an error for HTTP codes 4xx/5xx

            # Parse JSON Response
            data = response.json()
            if data.get("ok"):
                download_link = data["downloadLink"]
                print(f"Download Link: {download_link}")

                # 
                response = requests.get(download_link, stream=True)
                response.raise_for_status()
                video_filename = os.path.join(destination_folder, video_title)  # Define the path to save the file
                with open(video_filename, "wb") as file:
                    for chunk in response.iter_content(chunk_size=8192):  # Save in chunks
                        file.write(chunk)
                # return download_link, video_title

                # Step 3: Upload the video to Telegram
                #======================================
                bot_username = client.username if client.username else "👩‍💻Powered By LazyDeveloper"
                caption_lazy = f"ᴡɪᴛʜ ❤ @{bot_username}"
                title = video_title if video_title else "===========🍟==========="
                while len(caption) + len(caption_lazy) > 1024:
                    caption = caption[:-1]  # Trim caption if it's too long
                caption = f'<b><a href="{url}">{title}</a>\n\n<blockquote>{caption_lazy}</blockquote></b>'
 
                #====================================== 
                xlx = await progress_message2.edit_text("⚡ ᴘʀᴏᴄᴇssɪɴɢ ʏᴏᴜʀ ꜰɪʟᴇ ᴛᴏ ᴜᴘʟᴏᴀᴅ ᴏɴ ᴛᴇʟᴇɢʀᴀᴍ...")
                start_time = time.time()
                # sent_video = await client.send_video(
                #     message.from_user.id,  # The recipient ID (or channel)
                #     video_filename,  # Path to the video on your server
                #     caption=f"Here is your video: {video_title}",  # Video caption
                #     parse_mode=enums.ParseMode.HTML  # Optional: Parse mode for HTML
                # )
                width, height, duration = await Mdata01(video_filename)
                succ = await client.send_video(
                    message.chat.id,
                    video_filename,
                    caption=caption,
                    duration=duration,
                    width=width,
                    height=height,
                    parse_mode=enums.ParseMode.HTML,
                    supports_streaming=True,
                    progress=progress_for_pyrogram,
                    progress_args=(
                        f"<blockquote>🍟ᴜᴘʟᴏᴀᴅing ʏᴏᴜʀ ᴠɪᴅᴇᴏ... 📤</blockquote>============x============<blockquote><code>{caption}</code></blockquote>",
                        xlx,
                        start_time,
                    )
                )

                # -----------------------------------
                # -----------------------------------
                sticker_message = await message.reply_sticker("CAACAgIAAxkBAAEZdwRmJhCNfFRnXwR_lVKU1L9F3qzbtAAC4gUAAj-VzApzZV-v3phk4DQE")
                os.remove(video_filename)
                await asyncio.sleep(5)
                await sticker_message.delete()
            else:
                print(f"API Error: {data.get('message')}")
                return 
            
        except requests.exceptions.RequestException as e:
            print(f"Request Error: {e}")
            return
    # -------------------------------------
    # -------------------------------------
    # -------------------------------------
    # -------------------------------------




