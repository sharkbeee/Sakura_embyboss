from telethon import events # Added

# Removed: from pyrogram import filters
# Removed: from pyrogram.enums import ChatMemberStatus
# Removed: from pyrogram.types import ChatMemberUpdated

from bot import bot, group, LOGGER, _open # group is imported
from bot.func_helper.utils import tem_deluser
from bot.sql_helper.sql_emby import sql_get_emby, sql_update_emby, Emby
from bot.func_helper.emby import emby


@bot.on(events.ChatAction)
async def leave_del_emby(event: events.ChatAction.Event):
    # Filter for specific group(s)
    # Assuming 'group' is a list of chat IDs. If it's a single ID, adjust accordingly.
    # The event.chat_id will be negative for groups/channels.
    # Ensure 'group' stores IDs as Telethon expects them (e.g., -100xxxx for channels/supergroups)
    # or convert them if they are stored as positive integers from Pyrogram.
    # For simplicity, assuming 'group' contains comparable IDs.
    
    # Convert event.chat_id to positive if group IDs are stored as positive, or ensure group IDs are negative.
    # Pyrogram IDs are usually negative for groups/channels. Telethon's event.chat_id is also usually negative.
    # If `group` from config is positive, it needs to be `int(f"-100{gid}")` or similar.
    # For now, we assume `group` contains IDs directly comparable to `event.chat_id`.
    if event.chat_id not in group:
        return

    if event.user_left or event.user_kicked or event.user_banned:
        user_id = event.user_id
        if not user_id: # Should always be present for these events
            return

        user = await event.get_user()
        user_fname = user.first_name if user else f"User_{user_id}"

        try:
            e_data = sql_get_emby(tg=user_id) # Renamed 'e' to 'e_data' to avoid conflict with exception 'e'
            if e_data is None or e_data.embyid is None:
                return
            
            action_text = "离开了群组"
            if event.user_kicked:
                action_text = "被踢出了群组"
            elif event.user_banned:
                action_text = "被封禁出群组"

            if await emby.emby_del(id=e_data.embyid):
                sql_update_emby(Emby.embyid == e_data.embyid, embyid=None, name=None, pwd=None, pwd2=None, lv='d', cr=None, ex=None)
                tem_deluser() # Assuming this handles any temp user data cleanup
                log_message = f'【退群删号】- {user_fname} ({user_id}) {action_text}，咕噜噜，ta的账户被吃掉啦！'
                LOGGER.info(log_message)
                await bot.send_message(event.chat_id, text=f'✅ [{user_fname}](tg://user?id={user_id}) {action_text}，咕噜噜，ta的账户被吃掉啦！')
            else:
                log_message = f'【退群删号】- {user_fname} ({user_id}) {action_text}，但是没能吃掉ta的账户，请管理员检查！'
                LOGGER.error(log_message)
                await bot.send_message(event.chat_id, text=f'❎ [{user_fname}](tg://user?id={user_id}) {action_text}，但是没能吃掉ta的账户，请管理员检查！')
            
            # Ban user if configured, and if the event was a leave or kick.
            # If already banned (event.user_banned), no need to re-ban explicitly unless specific permission changes are desired.
            if _open.leave_ban and (event.user_left or event.user_kicked):
                try:
                    # Ban by setting view_messages to False. Other permissions can be set too.
                    await bot.edit_permissions(event.chat_id, user_id, view_messages=False)
                    LOGGER.info(f"Banned user {user_fname} ({user_id}) due to leave/kick from {event.chat_id}.")
                except Exception as ban_e:
                    LOGGER.error(f"Failed to ban user {user_id} in {event.chat_id} after leave/kick: {ban_e}")
        
        except Exception as ex_main: # Renamed outer exception to avoid conflict
            LOGGER.error(f"【退群删号】- Error processing user {user_id}: {ex_main}")
            # pass # Original code had a pass here in the else block of the try, implying errors were logged but execution continued.
