#! /usr/bin/python3
# -*- coding: utf-8 -*-

from asyncio import sleep

import asyncio

from telethon import errors, events, types # Added types
# Removed: from pyrogram import filters
# Removed: from pyrogram.errors import FloodWait, Forbidden, BadRequest
# Removed: from pyrogram.types import CallbackQuery
# Removed: from pyromod.exceptions import ListenerTimeout
from bot import LOGGER, group, bot


# 将来自己要是重写，希望不要把/cancel当关键词，用call.data，省代码还好看，切记。

async def sendMessage(event, text: str, buttons=None, timer=None, send_to_chat=False, chat_id=None): # Renamed 'send' to 'send_to_chat' for clarity
    """
    发送消息
    :param event: Telethon event (NewMessage or CallbackQuery) or Message object
    :param text: 实体
    :param buttons: 按钮
    :param timer: 定时删除
    :param send_to_chat: 非reply,发送到指定chat_id或第一个主授权群组
    :return:
    """
    try:
        current_message_obj = event.message if isinstance(event, events.CallbackQuery.Event) else event
        
        if send_to_chat is True:
            target_chat_id = chat_id if chat_id is not None else group[0]
            sent_msg = await bot.send_message(target_chat_id, text=text, buttons=buttons, link_preview=False)
        else:
            # quote=True is default for event.reply()
            # disable_web_page_preview=True becomes link_preview=False
            sent_msg = await current_message_obj.reply(text, buttons=buttons, link_preview=False)
        
        if timer is not None and sent_msg: # Ensure sent_msg is not None or False
            # deleteMessage will need to be adapted for Telethon message object or event
            return await deleteMessage(sent_msg, timer) 
        return sent_msg # Return the sent message object or True/False from deleteMessage
    except errors.FloodWaitError as f:
        LOGGER.warning(str(f))
        await sleep(f.seconds * 1.2) # f.value in Pyrogram, f.seconds in Telethon
        return await sendMessage(event, text, buttons, timer, send_to_chat, chat_id) # Recursion
    except errors.ChatWriteForbiddenError as e:
        LOGGER.error(f"Cannot send message. Chat write forbidden: {e}")
        # Potentially inform the user or try sending to a fallback chat if applicable
        if isinstance(event, events.NewMessage.Event): # or hasattr(event, 'respond')
             await event.respond("无法在此聊天中发送消息（权限不足）。")
        return False
    except Exception as e:
        LOGGER.error(f"Error in sendMessage: {str(e)}")
        return str(e)


async def editMessage(event_or_msg, text: str, buttons=None, timer=None): # Renamed message to event_or_msg
    """
    编辑消息
    :param event_or_msg: Telethon NewMessage.Event, CallbackQuery.Event, or Message object
    :param text:
    :param buttons:
    :return:
    """
    try:
        message_to_edit = None
        if isinstance(event_or_msg, events.CallbackQuery.Event):
            message_to_edit = event_or_msg.message
        elif isinstance(event_or_msg, events.NewMessage.Event): # Or just a Message object
            message_to_edit = event_or_msg.message # if event, else event_or_msg itself if it's already a message
        else: # Assuming it's a Message object
            message_to_edit = event_or_msg

        if not message_to_edit:
             LOGGER.error("editMessage: Could not determine message to edit.")
             return False

        # disable_web_page_preview=True becomes link_preview=False
        edited_msg = await message_to_edit.edit(text=text, buttons=buttons, link_preview=False)
        
        if timer is not None and edited_msg:
            return await deleteMessage(edited_msg, timer)
        return True
    except errors.FloodWaitError as f:
        LOGGER.warning(str(f))
        await sleep(f.seconds * 1.2)
        return await editMessage(event_or_msg, text, buttons, timer) # Recursion
    except errors.ButtonUrlInvalidError:
        # Original code had: await editMessage(message, text='⚠️ 底部按钮设置失败。', buttons=back_start_ikb)
        # This recursive call needs to be handled carefully, perhaps by returning an error status
        # or sending a new message if the original erroring buttons can't be used.
        LOGGER.warning("Button URL invalid during edit.")
        return False
    except errors.MessageNotModifiedError:
        # Original code had: await callAnswer(message, "慢速模式开启，切勿多点\n慢一点，慢一点，生活更有趣 - zztai", True)
        # callAnswer will be handled later. For now, just log or return.
        LOGGER.info("Message not modified during edit.")
        return False # Or True, as the content is already what was requested
    except errors.MessageIdInvalidError:
        LOGGER.warning("Message ID invalid during edit, perhaps already deleted.")
        return False
    except Exception as e:
        LOGGER.error(f"Error in editMessage: {str(e)}")
        return str(e)


async def sendFile(event_or_msg, file_path, file_name=None, caption=None, buttons=None): # Renamed message to event_or_msg, file to file_path
    """
    发送文件
    :param event_or_msg: Telethon NewMessage.Event, CallbackQuery.Event, or Message object
    :param file_path: Path to the file or BytesIO object
    :param file_name: Optional. Telethon usually infers this. If provided, can be used with attributes for InputMediaDocument.
    :param caption:
    :param buttons:
    :return:
    """
    try:
        current_message_obj = None
        if isinstance(event_or_msg, events.CallbackQuery.Event):
            current_message_obj = event_or_msg.message
        elif isinstance(event_or_msg, events.NewMessage.Event):
            current_message_obj = event_or_msg.message
        else: # Assuming it's a Message object
            current_message_obj = event_or_msg
        
        if not current_message_obj:
             LOGGER.error("sendFile: Could not determine message context for replying.")
             return False

        # Telethon's event.reply or message.reply takes 'file' argument.
        # file_name can be set using 'attributes' if needed for specific scenarios,
        # but usually Telethon handles it. Forcing file_name is more complex.
        # Forcing quote=False is default for sending new message, for reply use reply_to=event.id
        # Pyrogram's reply_document(quote=False) implies sending as a new message to the same chat, not a direct reply to the triggering message.
        # If it's a reply to the message:
        # await current_message_obj.reply(file=file_path, caption=caption, buttons=buttons)
        # If it's sending a new document to the same chat (not as a direct reply):
        await bot.send_file(current_message_obj.chat_id, file=file_path, caption=caption, buttons=buttons, 
                            attributes=[types.DocumentAttributeFilename(file_name)] if file_name else None)
        return True
    except errors.FloodWaitError as f:
        LOGGER.warning(str(f))
        await sleep(f.seconds * 1.2)
        return await sendFile(event_or_msg, file_path, file_name, caption, buttons) # Recursion
    except Exception as e:
        LOGGER.error(f"Error in sendFile: {str(e)}")
        return str(e)


async def sendPhoto(event_or_msg, photo, caption=None, buttons=None, timer=None, send_to_chat=False, chat_id=None): # Renamed message to event_or_msg, send to send_to_chat
    """
    发送图片
    :param event_or_msg: Telethon NewMessage.Event, CallbackQuery.Event, or Message object
    :param photo: Path to photo or file ID
    :param caption:
    :param buttons:
    :param timer:
    :param send_to_chat: 是否发送到指定chat_id或授权主群
    :return:
    """
    try:
        current_message_obj = None
        if isinstance(event_or_msg, events.CallbackQuery.Event):
            current_message_obj = event_or_msg.message
        elif isinstance(event_or_msg, events.NewMessage.Event):
            current_message_obj = event_or_msg.message
        else: # Assuming it's a Message object
            current_message_obj = event_or_msg

        sent_msg = None
        if send_to_chat is True:
            target_chat_id = chat_id if chat_id is not None else group[0]
            # bot.send_photo is bot.send_file in Telethon
            sent_msg = await bot.send_file(target_chat_id, file=photo, caption=caption, buttons=buttons)
        else:
            if not current_message_obj:
                 LOGGER.error("sendPhoto: Could not determine message context for replying.")
                 return False
            # message.reply_photo is event.reply(file=photo)
            # disable_notification=True is not directly available in event.reply, default behavior.
            sent_msg = await current_message_obj.reply(file=photo, caption=caption, buttons=buttons)
        
        if timer is not None and sent_msg:
            return await deleteMessage(sent_msg, timer)
        return True
    except errors.FloodWaitError as f:
        LOGGER.warning(str(f))
        await sleep(f.seconds * 1.2)
        # Original called sendFile, but this is sendPhoto, so recurse sendPhoto
        return await sendPhoto(event_or_msg, photo, caption, buttons, timer, send_to_chat, chat_id)
    except errors.ChatWriteForbiddenError as e:
        LOGGER.error(f"Cannot send photo. Chat write forbidden: {e}")
        if hasattr(event_or_msg, 'respond'): # Check if it's an event that can respond
             await event_or_msg.respond("无法在此聊天中发送图片（权限不足）。")
        return False
    except Exception as e:
        LOGGER.error(f"Error in sendPhoto: {str(e)}")
        return str(e)


async def deleteMessage(event_or_msg, timer=None): # Renamed message to event_or_msg
    """
    删除消息,带定时
    :param event_or_msg: Telethon NewMessage.Event, CallbackQuery.Event, or Message object
    :param timer:
    :return:
    """
    if timer is not None:
        await asyncio.sleep(timer)
    
    message_to_delete = None
    is_callback = False

    if isinstance(event_or_msg, events.CallbackQuery.Event):
        message_to_delete = event_or_msg.message # The message associated with the callback
        is_callback = True # To handle callAnswer part if needed later
        # For deleting the callback query message itself, Telethon's event.delete() works on the message.
        # If the intention was to delete the message *that triggered the callback button*, this is correct.
    elif isinstance(event_or_msg, events.NewMessage.Event): # Or just a Message object
        message_to_delete = event_or_msg.message 
    else: # Assuming it's a Message object directly
        message_to_delete = event_or_msg

    if not message_to_delete:
        LOGGER.error("deleteMessage: Could not determine message to delete.")
        return False

    try:
        await message_to_delete.delete()
        # if is_callback:
        #     # TODO: callAnswer will be migrated later. For now, this is a placeholder.
        #     # await callAnswer(event_or_msg, '✔️ Done!') 
        #     pass
        return True  # 返回 True 表示删除成功
    except errors.FloodWaitError as f:
        LOGGER.warning(str(f))
        await asyncio.sleep(f.seconds * 1.2)
        return await deleteMessage(event_or_msg, None)  # Retry without timer next, timer already waited
    except errors.ChatWriteForbiddenError as e: # Mapping for Forbidden
        LOGGER.warning(f"Delete forbidden: {e}")
        if is_callback:
            # TODO: callAnswer for 'message expired'
            # await callAnswer(event_or_msg, f'⚠️ 消息已过期，请重新 唤起面板\n/start', True)
            pass
        elif hasattr(message_to_delete, 'reply'): # If it's a message object we can reply to
             # Check if message_to_delete.chat is not None before accessing message_to_delete.chat.id
            chat_id_info = f"in chat {message_to_delete.chat.id}" if message_to_delete.chat else "in unknown chat"
            await message_to_delete.reply(f'⚠️ **错误！**检查群组 {chat_id_info} 权限 【删除消息】')
        return False
    except errors.MessageDeleteForbiddenError as e: # More specific delete error
        LOGGER.warning(f"Message delete forbidden: {e}")
        # Similar handling to ChatWriteForbiddenError for callbacks or replies
        if is_callback:
            # TODO: callAnswer
            pass
        return False
    # Pyrogram's BadRequest for message deletion issues might map to various Telethon errors
    # such as MessageIdInvalidError if the message is already gone.
    # Telethon's delete() is quite resilient and often doesn't raise if message not found.
    except Exception as e:
        # Catching generic Exception for other Telethon errors like MessageIdInvalidError, etc.
        # which might occur if message is already deleted or ID is bad.
        LOGGER.error(f"Error in deleteMessage: {str(e)}")
        return str(e)  # 返回异常字符串表示删除出错


async def callAnswer(event: events.CallbackQuery.Event, text_message: str, show_alert: bool = False):
    """
    Answers a callback query.
    :param event: The CallbackQuery.Event object.
    :param text_message: The message to send as an answer.
    :param show_alert: Whether to show the message as an alert.
    :return: True if successful, False or error string otherwise.
    """
    try:
        if not hasattr(event, 'answer'):
            LOGGER.error("callAnswer: Provided event object does not have an 'answer' method.")
            return False
            
        await event.answer(message=text_message, alert=show_alert)
        return True
    except errors.FloodWaitError as e:
        LOGGER.warning(f"FloodWaitError in callAnswer: {str(e)}")
        await asyncio.sleep(e.seconds * 1.2) # Ensure asyncio is imported
        return await callAnswer(event, text_message, show_alert) # Recursive call
    except errors.QueryIdInvalidError:
        # This error means the callback query has expired or is invalid.
        # In Pyrogram, this was e.ID == "QUERY_ID_INVALID" under BadRequest.
        LOGGER.warning("Query ID invalid for callAnswer, likely expired or already answered.")
        return False
    except errors.TelegramBadRequestError as e: # Catch other Telegram-related bad requests
        LOGGER.error(f"TelegramBadRequestError in callAnswer: {e}")
        return False
    except Exception as e:
        LOGGER.error(f"Generic error in callAnswer: {e}")
        # Returning str(e) was the old pattern, consider returning False for consistency
        return str(e) 


async def callListen(callback_query_event, timer: int = 120, buttons=None):
    # TODO: This function relied on Pyromod's listen.
    # It needs to be refactored. The calling code should manage a
    # `bot.conversation()` context, and this function might become
    # a wrapper around `conv.get_response()` or similar,
    # or be removed if callers handle conversation logic directly.
    # The original timeout behavior (e.g., ListenerTimeout) would also
    # need to be replicated using `asyncio.timeout_after` or `conv.get_response(timeout=...)`.
    pass
    return None


async def call_dice_listen(callback_query_event, timer: int = 120, buttons=None):
    # TODO: This function relied on Pyromod's listen (for dice).
    # It needs to be refactored. The calling code should manage a
    # `bot.conversation()` context, and this function might become
    # a wrapper around `conv.get_response()` filtering for dice messages,
    # or be removed if callers handle conversation logic directly.
    # The original timeout behavior would also need to be replicated.
    pass
    return None


async def callAsk(callback_query_event, text, timer: int = 120, button=None):
    # TODO: This function relied on Pyromod's ask.
    # It needs to be refactored. The calling code should manage a
    # `bot.conversation()` context. This function might involve sending a message
    # (the 'ask' part) and then getting a response, e.g.,
    # `await conv.send_message(text, buttons=button); response = await conv.get_response()`.
    # The original timeout behavior would also need to be replicated.
    pass
    return None


async def ask_return(event_or_msg, text, timer: int = 120, button=None): # Renamed update to event_or_msg
    # TODO: This function relied on Pyromod's ask.
    # It needs to be refactored. The calling code should manage a
    # `bot.conversation()` context. This function might involve sending a message
    # (the 'ask' part) and then getting a response, e.g.,
    # `await conv.send_message(text, buttons=button); response = await conv.get_response()`.
    # The original timeout behavior and error handling (ListenerTimeout)
    # would also need to be replicated.
    pass
    return None


import re
import html


# 转义特殊字符
def escape_html_special_chars(text):
    # 定义一些常用的字符
    pattern = r"[\\`*_{}[\]()#+-.!|]"
    # 使用正则表达式替换掉特殊字符
    text = re.sub(pattern, r"\\\g<0>", text)
    # 使用html模块转义HTML的特殊字符
    text = html.escape(text)
    return text


def escape_markdown(text):
    return (
        re.sub(r"([_*\[\]()~`>\#\+\-=|{}\.!\\])", r"\\\1", html.unescape(text))
        if text
        else str()
    )
