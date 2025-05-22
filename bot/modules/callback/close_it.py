#! /usr/bin/python3
import re # Added
from telethon import events # Added

# Removed: from pyrogram import filters
# Removed: from pyrogram.enums import ChatType

from bot import bot
from bot.func_helper.msg_utils import callAnswer, deleteMessage
from bot.func_helper.utils import judge_admins


# Using Telethon's event handling
@bot.on(events.CallbackQuery(pattern=re.compile(b"closeit(?:_(\\d+))?")))
async def close_it(event: events.CallbackQuery.Event):
    if event.is_private: # Check if the chat is private
        await deleteMessage(event) # Pass event
    else:
        target_user_id = None
        if event.pattern_match.group(1): # Check if a user ID was captured
            try:
                target_user_id = int(event.pattern_match.group(1).decode())
            except ValueError:
                pass # Should not happen if regex matches digits, but good to be safe

        if target_user_id is not None:
            if target_user_id == event.sender_id:
                return await deleteMessage(event) # Pass event
            # else: # Original code commented this out, keeping it commented
            #     return await callAnswer(event, '此非你的专属', True)
        
        # If no target_user_id in callback_data or target_user_id doesn't match sender_id,
        # then check for admin privileges.
        if judge_admins(event.sender_id): # Pass event.sender_id
            await deleteMessage(event) # Pass event
        else:
            await callAnswer(event, '⚠️ 请不要以下犯上，ok？', True) # Pass event
