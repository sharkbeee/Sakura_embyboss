import time
import re # Added
from telethon import events # Added

# Removed: from pyrogram import filters

from bot import bot, owner, prefixes, extra_emby_libs, LOGGER, Now # Ensure prefixes and owner are imported
from bot.func_helper.msg_utils import sendMessage, deleteMessage
from bot.sql_helper.sql_emby import get_all_emby, Emby
from bot.func_helper.emby import emby

# Helper function for command patterns
def command_pattern(command_name: str) -> re.Pattern:
    escaped_prefixes = [re.escape(p) for p in prefixes]
    prefix_match = "|".join(escaped_prefixes)
    # Matches /cmd@botname args or /cmd args or /cmd@botname or /cmd
    return re.compile(rf"^(?:{prefix_match})({command_name})(?:@\w+)?(?:\s+.*)?$")

# embylibs_block
@bot.on(events.NewMessage(pattern=command_pattern('embylibs_blockall'), from_users=owner))
async def embylibs_blockall(event: events.NewMessage.Event):
    await deleteMessage(event)
    reply = await event.reply(f"🍓 正在处理ing····, 正在更新所有用户的媒体库访问权限")
    rst = get_all_emby(Emby.embyid is not None)
    
    sender = await event.get_sender()
    sender_name = sender.first_name if sender else "Unknown"

    if rst is None:
        LOGGER.info(
            f"【关闭媒体库任务】 -{sender_name}({event.sender_id}) 没有检测到任何emby账户，结束")
        return await reply.edit("⚡【关闭媒体库任务】\n\n结束，没有一个有号的")
    
    allcount = 0
    successcount = 0
    start = time.perf_counter()
    text_chunks = [] # Use a list to store text parts
    current_text_part = ''

    all_libs = await emby.get_emby_libs()
    for i in rst:
        success, rep = emby.user(embyid=i.embyid)
        if success:
            allcount += 1
            currentblock = ['播放列表'] + all_libs
            currentblock = list(set(currentblock))
            res = await emby.emby_block(i.embyid, 0, block=currentblock) # Renamed re to res
            line_text = ''
            if res is True:
                successcount += 1
                line_text = f'已关闭了 [{i.name}](tg://user?id={i.tg}) 的媒体库权限\n'
            else:
                line_text = f'🌧️ 关闭失败 [{i.name}](tg://user?id={i.tg}) 的媒体库权限\n'
            
            if len(current_text_part) + len(line_text) > 1000: # Approximate chunk size
                text_chunks.append(current_text_part)
                current_text_part = line_text
            else:
                current_text_part += line_text
    
    if current_text_part: # Add any remaining text
        text_chunks.append(current_text_part)

    for chunk in text_chunks:
        await event.reply(chunk + f'\n**{Now.strftime("%Y-%m-%d %H:%M:%S")}**')
        
    end = time.perf_counter()
    times = end - start
    if allcount != 0:
        await sendMessage(event,
                          text=f"⚡#关闭媒体库任务 done\n  共检索出 {allcount} 个账户，成功关闭 {successcount}个，耗时：{times:.3f}s")
    else:
        await sendMessage(event, text=f"**#关闭媒体库任务 结束！搞毛，没有人被干掉。**")
    LOGGER.info(
        f"【关闭媒体库任务结束】 - {event.sender_id} 共检索出 {allcount} 个账户，成功关闭 {successcount}个，耗时：{times:.3f}s")

# embylibs_unblock
@bot.on(events.NewMessage(pattern=command_pattern('embylibs_unblockall'), from_users=owner))
async def embylibs_unblockall(event: events.NewMessage.Event):
    await deleteMessage(event)
    reply = await event.reply(f"🍓 正在处理ing····, 正在更新所有用户的媒体库访问权限")
    rst = get_all_emby(Emby.embyid is not None)

    sender = await event.get_sender()
    sender_name = sender.first_name if sender else "Unknown"

    if rst is None:
        LOGGER.info(
            f"【开启媒体库任务】 -{sender_name}({event.sender_id}) 没有检测到任何emby账户，结束")
        return await reply.edit("⚡【开启媒体库任务】\n\n结束，没有一个有号的")
    
    allcount = 0
    successcount = 0
    start = time.perf_counter()
    text_chunks = []
    current_text_part = ''

    for i in rst:
        success, rep = emby.user(embyid=i.embyid)
        if success:
            allcount += 1
            currentblock = ['播放列表']
            res = await emby.emby_block(i.embyid, 0, block=currentblock) # Renamed re to res
            line_text = ''
            if res is True:
                successcount += 1
                line_text = f'已开启了 [{i.name}](tg://user?id={i.tg}) 的媒体库权限\n'
            else:
                line_text = f'🌧️ 开启失败 [{i.name}](tg://user?id={i.tg}) 的媒体库权限\n'

            if len(current_text_part) + len(line_text) > 1000:
                text_chunks.append(current_text_part)
                current_text_part = line_text
            else:
                current_text_part += line_text
    
    if current_text_part:
        text_chunks.append(current_text_part)

    for chunk in text_chunks:
        await event.reply(chunk + f'\n**{Now.strftime("%Y-%m-%d %H:%M:%S")}**')
        
    end = time.perf_counter()
    times = end - start
    if allcount != 0:
        await sendMessage(event,
                          text=f"⚡#开启媒体库任务 done\n  共检索出 {allcount} 个账户，成功开启 {successcount}个，耗时：{times:.3f}s")
    else:
        await sendMessage(event, text=f"**#开启媒体库任务 结束！搞毛，没有人被干掉。**")
    LOGGER.info(
        f"【开启媒体库任务结束】 - {event.sender_id} 共检索出 {allcount} 个账户，成功开启 {successcount}个，耗时：{times:.3f}s")

@bot.on(events.NewMessage(pattern=command_pattern('extraembylibs_blockall'), from_users=owner))
async def extraembylibs_blockall(event: events.NewMessage.Event):
    await deleteMessage(event)
    reply = await event.reply(f"🍓 正在处理ing····, 正在更新所有用户的额外媒体库访问权限")

    rst = get_all_emby(Emby.embyid is not None)
    sender = await event.get_sender()
    sender_name = sender.first_name if sender else "Unknown"

    if rst is None:
        LOGGER.info(
            f"【关闭额外媒体库任务】 -{sender_name}({event.sender_id}) 没有检测到任何emby账户，结束")
        return await reply.edit("⚡【关闭额外媒体库任务】\n\n结束，没有一个有号的")

    allcount = 0
    successcount = 0
    start = time.perf_counter()
    text_chunks = []
    current_text_part = ''

    for i in rst:
        success, rep = emby.user(embyid=i.embyid)
        if success:
            allcount += 1
            line_text = ''
            try:
                currentblock = list(set(rep["Policy"]["BlockedMediaFolders"] + ['播放列表']))
            except KeyError:
                currentblock = ['播放列表'] + extra_emby_libs
            
            if not set(extra_emby_libs).issubset(set(currentblock)):
                currentblock = list(set(currentblock + extra_emby_libs))
                res = await emby.emby_block(i.embyid, 0, block=currentblock) # Renamed re to res
                if res is True:
                    successcount += 1
                    line_text = f'已关闭了 [{i.name}](tg://user?id={i.tg}) 的额外媒体库权限\n'
                else:
                    line_text = f'🌧️ 关闭失败 [{i.name}](tg://user?id={i.tg}) 的额外媒体库权限\n'
            else: # Already blocked
                successcount += 1
                line_text = f'已关闭了 [{i.name}](tg://user?id={i.tg}) 的额外媒体库权限\n'
            
            if len(current_text_part) + len(line_text) > 1000:
                text_chunks.append(current_text_part)
                current_text_part = line_text
            else:
                current_text_part += line_text

    if current_text_part:
        text_chunks.append(current_text_part)

    for chunk in text_chunks:
        await event.reply(chunk + f'\n**{Now.strftime("%Y-%m-%d %H:%M:%S")}**')
        
    end = time.perf_counter()
    times = end - start
    if allcount != 0:
        await sendMessage(event,
                          text=f"⚡#关闭额外媒体库任务 done\n  共检索出 {allcount} 个账户，成功关闭 {successcount}个，耗时：{times:.3f}s")
    else:
        await sendMessage(event, text=f"**#关闭额外媒体库任务 结束！搞毛，没有人被干掉。**")
    LOGGER.info(
        f"【关闭额外媒体库任务结束】 - {event.sender_id} 共检索出 {allcount} 个账户，成功关闭 {successcount}个，耗时：{times:.3f}s")


@bot.on(events.NewMessage(pattern=command_pattern('extraembylibs_unblockall'), from_users=owner))
async def extraembylibs_unblockall(event: events.NewMessage.Event):
    await deleteMessage(event)
    reply = await event.reply(f"🍓 正在处理ing····, 正在更新所有用户的额外媒体库访问权限")

    rst = get_all_emby(Emby.embyid is not None)
    sender = await event.get_sender()
    sender_name = sender.first_name if sender else "Unknown"

    if rst is None:
        LOGGER.info(
            f"【开启额外媒体库任务】 -{sender_name}({event.sender_id}) 没有检测到任何emby账户，结束")
        return await reply.edit("⚡【开启额外媒体库任务】\n\n结束，没有一个有号的")

    allcount = 0
    successcount = 0
    start = time.perf_counter()
    text_chunks = []
    current_text_part = ''

    for i in rst:
        success, rep = emby.user(embyid=i.embyid)
        if success:
            allcount += 1
            line_text = ''
            try:
                currentblock = list(set(rep["Policy"]["BlockedMediaFolders"] + ['播放列表']))
                # To unblock, remove extra_emby_libs from currentblock
                currentblock = [x for x in currentblock if x not in extra_emby_libs]
            except KeyError: # No BlockedMediaFolders key, means nothing is blocked beyond defaults
                currentblock = ['播放列表'] # Default, effectively unblocked for extras
            
            # The logic here seems to be: if extra_emby_libs was part of currentblock, unblock it.
            # The condition `if not set(extra_emby_libs).issubset(set(currentblock))` in original
            # was for BLOCKING. For UNBLOCKING, we always want to set the policy
            # to a state where extra_emby_libs are NOT in BlockedMediaFolders.
            # The `currentblock` calculated above already reflects the desired unblocked state.
            
            res = await emby.emby_block(i.embyid, 0, block=currentblock) # Renamed re to res
            if res is True:
                successcount += 1
                line_text = f'已开启了 [{i.name}](tg://user?id={i.tg}) 的额外媒体库权限\n'
            else:
                line_text = f'🌧️ 开启失败 [{i.name}](tg://user?id={i.tg}) 的额外媒体库权限\n'
            # The original else branch (already unblocked) is covered by successful `emby_block` call
            # setting the policy to the unblocked state.

            if len(current_text_part) + len(line_text) > 1000:
                text_chunks.append(current_text_part)
                current_text_part = line_text
            else:
                current_text_part += line_text

    if current_text_part:
        text_chunks.append(current_text_part)
        
    for chunk in text_chunks:
        await event.reply(chunk + f'\n**{Now.strftime("%Y-%m-%d %H:%M:%S")}**')
        
    end = time.perf_counter()
    times = end - start
    if allcount != 0:
        await sendMessage(event,
                          text=f"⚡#开启额外媒体库任务 done\n  共检索出 {allcount} 个账户，成功开启 {successcount}个，耗时：{times:.3f}s")
    else:
        await sendMessage(event, text=f"**#开启额外媒体库任务 结束！搞毛，没有人被干掉。**")
    LOGGER.info(
        f"【开启额外媒体库任务结束】 - {event.sender_id} 共检索出 {allcount} 个账户，成功开启 {successcount}个，耗时：{times:.3f}s")
