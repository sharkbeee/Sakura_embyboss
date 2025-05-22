"""
兑换注册码exchange
"""
from datetime import timedelta, datetime
import re # Added
from telethon import events # Added

from bot import bot, _open, LOGGER, bot_photo
from bot.func_helper.emby import emby
from bot.func_helper.fix_bottons import register_code_ikb
from bot.func_helper.msg_utils import sendMessage, sendPhoto
from bot.sql_helper.sql_code import Code
from bot.sql_helper.sql_emby import sql_get_emby, Emby
from bot.sql_helper import Session
from bot.func_helper.filters import user_in_group_on_filter # Keep for now for the wrapper


def is_renew_code(input_string):
    if "Renew" in input_string:
        return True
    else:
        return False


async def rgs_code(event: events.NewMessage.Event, register_code: str): # Updated signature
    if _open.stat: return await sendMessage(event, "🤧 自由注册开启下无法使用注册码。") # Use event

    data = sql_get_emby(tg=event.sender_id) # Use event.sender_id
    if not data: return await sendMessage(event, "出错了，不确定您是否有资格使用，请先 /start") # Use event
    embyid = data.embyid
    ex = data.ex
    lv = data.lv
    
    sender = await event.get_sender() # Get sender object
    sender_name = sender.first_name if sender else "Unknown"

    if embyid: # User has an Emby account, this is a renewal attempt
        if not is_renew_code(register_code): return await sendMessage(event, # Use event
                                                                      "🔔 很遗憾，您使用的是注册码，无法启用续期功能，请悉知",
                                                                      timer=60)
        with Session() as session:
            r = session.query(Code).filter(Code.code == register_code).with_for_update().first()
            if not r: return await sendMessage(event, "⛔ **你输入了一个错误de续期码，请确认好重试。**", timer=60) # Use event
            
            # Attempt to mark the code as used by the current user
            update_count = session.query(Code).filter(Code.code == register_code, Code.used.is_(None)).with_for_update().update(
                {Code.used: event.sender_id, Code.usedtime: datetime.now()})
            session.commit()
            
            if update_count == 0: # Code was already used or doesn't exist (though caught by `if not r`)
                # Fetch the user who actually used it, if any
                code_info = session.query(Code.used).filter(Code.code == register_code).first()
                used_by_id = code_info.used if code_info and code_info.used else "未知用户"
                return await sendMessage(event, # Use event
                                         f'此 `{register_code}` \n续期码已被使用，是 [{used_by_id}](tg://user?id={used_by_id}) 的形状了喔')
            
            # Code successfully claimed by this user
            tg1 = r.tg # Original code creator's TG ID
            us1 = r.us # Days/value of the code
            
            first = await event.client.get_entity(tg1) # Use event.client.get_entity
            ex_new = datetime.now() # Base for renewal
            
            if ex_new > ex : # If current expiry is in the past, renew from now
                ex_new_calculated = ex_new + timedelta(days=us1)
                await emby.emby_change_policy(id=embyid, method=False) # Unsuspend Emby account
                if lv == 'c': # If user was 'c' (presumably disabled/expired), upgrade to 'b'
                    session.query(Emby).filter(Emby.tg == event.sender_id).update({Emby.ex: ex_new_calculated, Emby.lv: 'b'})
                else:
                    session.query(Emby).filter(Emby.tg == event.sender_id).update({Emby.ex: ex_new_calculated})
                await sendMessage(event, f'🎊 少年郎，恭喜你，已收到 [{first.first_name}](tg://user?id={tg1}) 的{us1}天🎁\n' # Use event
                                       f'__已解封账户并延长到期时间至(以当前时间计)__\n到期时间：{ex_new_calculated.strftime("%Y-%m-%d %H:%M:%S")}')
            else: # If current expiry is in the future, add to existing expiry
                ex_new_calculated = ex + timedelta(days=us1) # Use 'ex' (original expiry) not 'data.ex' (stale)
                session.query(Emby).filter(Emby.tg == event.sender_id).update({Emby.ex: ex_new_calculated})
                await sendMessage(event, # Use event
                                  f'🎊 少年郎，恭喜你，已收到 [{first.first_name}](tg://user?id={tg1}) 的{us1}天🎁\n到期时间：{ex_new_calculated.strftime("%Y-%m-%d %H:%M:%S")}__')
            session.commit()
            
            new_code_display = register_code[:-7] + "░" * 7
            await sendMessage(event, # Use event
                              f'· 🎟️ 续期码使用 - [{sender_name}](tg://user?id={event.sender_id}) [{event.sender_id}] 使用了 {new_code_display}\n· 📅 实时到期 - {ex_new_calculated.strftime("%Y-%m-%d %H:%M:%S")}',
                              send_to_chat=True) # send=True becomes send_to_chat=True
            LOGGER.info(f"【续期码】：{sender_name}[{event.sender_id}] 使用了 {register_code}，到期时间：{ex_new_calculated.strftime('%Y-%m-%d %H:%M:%S')}")

    else: # No embyid, so this is a registration attempt
        if is_renew_code(register_code): return await sendMessage(event, # Use event
                                                                  "🔔 很遗憾，您使用的是续期码，无法启用注册功能，请悉知",
                                                                  timer=60)
        if data.us > 0: return await sendMessage(event, "已有注册资格，请先使用【创建账户】注册，勿重复使用其他注册码。") # Use event
        with Session() as session:
            r = session.query(Code).filter(Code.code == register_code).with_for_update().first()
            if not r: return await sendMessage(event, "⛔ **你输入了一个错误de注册码，请确认好重试。**") # Use event
            
            update_count = session.query(Code).filter(Code.code == register_code, Code.used.is_(None)).with_for_update().update(
                {Code.used: event.sender_id, Code.usedtime: datetime.now()})
            session.commit() 
            
            if update_count == 0:
                code_info = session.query(Code.used).filter(Code.code == register_code).first()
                used_by_id = code_info.used if code_info and code_info.used else "未知用户"
                return await sendMessage(event, # Use event
                                         f'此 `{register_code}` \n注册码已被使用,是 [{used_by_id}](tg://user?id={used_by_id}) 的形状了喔')
            
            tg1 = r.tg # Original code creator's TG ID
            us1 = r.us # Days/value of the code (registration eligibility duration)
            
            first = await event.client.get_entity(tg1) # Use event.client.get_entity
            x = data.us + us1 # Add registration eligibility period
            session.query(Emby).filter(Emby.tg == event.sender_id).update({Emby.us: x})
            session.commit()
            
            await sendPhoto(event, photo=bot_photo, # Use event
                            caption=f'🎊 少年郎，恭喜你，已经收到了 [{first.first_name}](tg://user?id={tg1}) 发送的邀请注册资格\n\n请选择你的选项~',
                            buttons=register_code_ikb)
            new_code_display = register_code[:-7] + "░" * 7
            await sendMessage(event, # Use event
                              f'· 🎟️ 注册码使用 - [{sender_name}](tg://user?id={event.sender_id}) [{event.sender_id}] 使用了 {new_code_display}',
                              send_to_chat=True) # send=True becomes send_to_chat=True
            LOGGER.info(
                f"【注册码】：{sender_name}[{event.sender_id}] 使用了 {register_code} - {us1}")

# TODO: user_in_group_on_filter needs full migration for Telethon.
# This is a temporary wrapper and will likely not work as intended.
async def wrapped_user_filter_exchange(event: events.NewMessage.Event) -> bool:
    if not event.is_private: # Ensure command is in private chat
        return False
    LOGGER.warning("user_in_group_on_filter for exchange handler needs full migration. Temporarily returning True for private chats.")
    # Placeholder: return await user_in_group_on_filter(bot, event) # This would be the optimistic call
    return True

# TODO: Review if this command handler should be active. 
# It assumes the command format is /exchange YOUR_CODE or similar.
# The original filter was `filters.regex('exchange') & filters.private & user_in_group_on_filter`.
# This suggests it was intended for messages containing 'exchange', not necessarily as a command.
# For Telethon, a command pattern like `/exchange(?: (.*))?` would be more typical.
#
# @bot.on(events.NewMessage(pattern=re.compile(r'/exchange(?: (.*))?', re.IGNORECASE), func=wrapped_user_filter_exchange))
# async def exchange_command_handler(event: events.NewMessage.Event):
#     register_code_from_text = None
#     if event.pattern_match.group(1):
#         register_code_from_text = event.pattern_match.group(1).strip()
#
#     if register_code_from_text:
#         await rgs_code(event, register_code_from_text)
#     else:
#         # This message might be better if it's a reply to a prompt or part of a conversation flow
#         await sendMessage(event, "请提供注册码，例如：`/exchange YOUR_CODE_HERE`")
#     # Original handler was `async def exchange_buttons(_, call): await rgs_code(_, msg)`
#     # This implies it might have been a callback or that `msg` was available from context.
#     # The current implementation assumes it's a new message command.
#     pass
