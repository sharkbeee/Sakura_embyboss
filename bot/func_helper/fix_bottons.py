from cacheout import Cache
from telethon.tl.custom import Button # Added
from typing import List, Union, Optional, Any, Dict # Added for type hinting and data structures
# Removed: from pykeyboard import InlineKeyboard, InlineButton
# Removed: from pyrogram.types import InlineKeyboardMarkup (was not explicitly there but good to ensure)
# Removed: from pyromod.helpers import ikb, array_chunk
from bot import chanel, main_group, bot_name, extra_emby_libs, tz_id, tz_ad, tz_api, _open, sakura_b, \
    schedall, auto_update, fuxx_pitao, kk_gift_days, moviepilot, red_envelope
from bot.func_helper import nezha_res
from bot.func_helper.emby import emby
from bot.func_helper.utils import members_info

cache = Cache()

# Re-implemented array_chunk from pyromod.helpers
def array_chunk(input_list: List[Any], size: int) -> List[List[Any]]:
    return [input_list[i:i + size] for i in range(0, len(input_list), size)]

def _create_telethon_buttons(data_list: List[List[Union[List[str], tuple]]]) -> List[List[Button]]:
    """
    Helper function to convert a list of button definitions to Telethon buttons.
    Each item in the inner list can be:
    - ['text', 'callback_data']
    - ['text', 'url', 'url_type_flag'] (where 'url_type_flag' is 'url')
    - ('text', 'callback_data')
    - ('text', 'url', 'url_type_flag')
    """
    keyboard = []
    for row_data in data_list:
        row_buttons = []
        for item in row_data:
            text = item[0]
            if len(item) == 3 and item[2] == 'url':
                row_buttons.append(Button.url(text, item[1]))
            elif len(item) == 2:
                # Ensure callback_data is bytes
                callback_data = item[1].encode('utf-8') if isinstance(item[1], str) else item[1]
                row_buttons.append(Button.inline(text, data=callback_data))
            else:
                # Fallback for unknown structure, or simple callback
                callback_data = item[1].encode('utf-8') if isinstance(item[1], str) else item[1]
                row_buttons.append(Button.inline(text, data=callback_data))
        keyboard.append(row_buttons)
    return keyboard

"""start面板 ↓"""


def judge_start_ikb(is_admin: bool, account: bool) -> List[List[Button]]:
    """
    start面板按钮
    """
    button_defs_flat = []
    if not account:
        button_defs_flat.append(['🎟️ 使用注册码', 'exchange'])
        button_defs_flat.append(['👑 创建账户', 'create'])
        button_defs_flat.append(['⭕ 换绑TG', 'changetg'])
        button_defs_flat.append(['🔍 绑定TG', 'bindtg'])
        if _open.invite_lv == 'd':
            button_defs_flat.append(['🏪 兑换商店', 'storeall'])
    else:
        button_defs_flat.append(['️👥 用户功能', 'members'])
        button_defs_flat.append(['🌐 服务器', 'server'])
        if schedall.check_ex:
            button_defs_flat.append(['🎟️ 使用续期码', 'exchange'])
    
    if _open.checkin:
        button_defs_flat.append([f'🎯 签到', 'checkin'])
    
    lines_of_button_defs = array_chunk(button_defs_flat, 2)
    
    if is_admin:
        lines_of_button_defs.append([['👮🏻‍♂️ admin', 'manage']])
        
    return _create_telethon_buttons(lines_of_button_defs)


# un_group_answer
group_f = _create_telethon_buttons([[('点击我(●ˇ∀ˇ●)', f't.me/{bot_name}', 'url')]])
# un in group
judge_group_ikb = _create_telethon_buttons([[('🌟 频道入口 ', f't.me/{chanel}', 'url'),
                                           ('💫 群组入口', f't.me/{main_group}', 'url')],
                                          [('❌ 关闭消息', 'closeit')]])

"""members ↓"""


def members_ikb(is_admin: bool = False, account: bool = False) -> List[List[Button]]:
    """
    判断用户面板
    """
    if account:
        normal = [[('🏪 兑换商店', 'storeall'), ('🗑️ 删除账号', 'delme')],
                  [('🎬 显示/隐藏', 'embyblock'), ('⭕ 重置密码', 'reset')],
                  [('💖 我的收藏', 'my_favorites'), ('💠 我的设备', 'my_devices')],
                 ]
        if moviepilot.status:
            normal.append([('🍿 点播中心', 'download_center')])
        normal.append([('♻️ 主界面', 'back_start')])
        return _create_telethon_buttons(normal)
    else:
        return judge_start_ikb(is_admin, account)


back_start_ikb = _create_telethon_buttons([[('💫 回到首页', 'back_start')]])
back_members_ikb = _create_telethon_buttons([[('💨 返回', 'members')]])
back_manage_ikb = _create_telethon_buttons([[('💨 返回', 'manage')]])
re_create_ikb = _create_telethon_buttons([[('🍥 重新输入', 'create'), ('💫 用户主页', 'members')]])
re_changetg_ikb = _create_telethon_buttons([[('✨ 换绑TG', 'changetg'), ('💫 用户主页', 'members')]])
re_bindtg_ikb = _create_telethon_buttons([[('✨ 绑定TG', 'bindtg'), ('💫 用户主页', 'members')]])
re_delme_ikb = _create_telethon_buttons([[('♻️ 重试', 'delme')], [('🔙 返回', 'members')]])
re_reset_ikb = _create_telethon_buttons([[('♻️ 重试', 'reset')], [('🔙 返回', 'members')]])
re_exchange_b_ikb = _create_telethon_buttons([[('♻️ 重试', 'exchange'), ('❌ 关闭', 'closeit')]])
re_born_ikb = _create_telethon_buttons([[('✨ 重输', 'store-reborn'), ('💫 返回', 'storeall')]])


def send_changetg_ikb(cr_id, rp_id) -> List[List[Button]]:
    """
    :param cr_id: 当前操作id
    :param rp_id: 替换id
    :return:
    """
    return _create_telethon_buttons([[('✅ 通过', f'changetg_{cr_id}_{rp_id}'), ('❎ 驳回', f'nochangetg_{cr_id}_{rp_id}')]])


def store_ikb() -> List[List[Button]]:
    return _create_telethon_buttons([[(f'♾️ 兑换白名单', 'store-whitelist'), (f'🔥 兑换解封禁', 'store-reborn')],
                                   [(f'🎟️ 兑换注册码', 'store-invite'), (f'🔍 查询注册码', 'store-query')],
                                   [(f'❌ 取消', 'members')]])


re_store_renew = _create_telethon_buttons([[('✨ 重新输入', 'changetg'), ('💫 取消输入', 'storeall')]])


def del_me_ikb(embyid) -> List[List[Button]]:
    return _create_telethon_buttons([[('🎯 确定', f'delemby-{embyid}')], [('🔙 取消', 'members')]])


def emby_block_ikb(embyid) -> List[List[Button]]:
    return _create_telethon_buttons(
        [[("✔️️ - 显示", f"emby_unblock-{embyid}"), ("✖️ - 隐藏", f"emby_block-{embyid}")], [("🔙 返回", "members")]])


user_emby_block_ikb = _create_telethon_buttons([[('✅ 已隐藏', 'members')]])
user_emby_unblock_ikb = _create_telethon_buttons([[('❎ 已显示', 'members')]])

"""server ↓"""


@cache.memoize(ttl=120)
async def cr_page_server(): # -> Tuple[Optional[List[List[Button]]], Optional[List[Dict[str, Any]]]]
    """
    翻页服务器面板
    :return:
    """
    sever_data = nezha_res.sever_info(tz_ad, tz_api, tz_id) # Renamed sever to sever_data
    if not sever_data:
        return _create_telethon_buttons([[('🔙 - 用户', 'members'), ('❌ - 上一级', 'back_start')]]), None
    
    button_defs_flat = []
    for i in sever_data:
        button_defs_flat.append([i['name'], f'server:{i["id"]}'])
    
    lines_of_button_defs = array_chunk(button_defs_flat, 3)
    lines_of_button_defs.append([['🔙 - 用户', 'members'], ['❌ - 上一级', 'back_start']])
    return _create_telethon_buttons(lines_of_button_defs), sever_data


"""admins ↓"""

# gm_ikb_content was refactored in the previous step with _create_telethon_buttons
gm_ikb_content = _create_telethon_buttons([[('⭕ 注册状态', 'open-menu'), ('🎟️ 注册/续期码', 'cr_link')],
                                         [('💊 查询注册', 'ch_link'), ('🏬 兑换设置', 'set_renew')],
                                         [('👥 用户列表', 'normaluser'), ('👑 白名单列表', 'whitelist'), ('💠 设备列表', 'user_devices')],
                                         [('🌏 定时', 'schedall'), ('🕹️ 主界面', 'back_start'), ('其他 🪟', 'back_config')]])


def open_menu_ikb(openstats, timingstats) -> List[List[Button]]:
    return _create_telethon_buttons([[(f'{openstats} 自由注册', 'open_stat'), (f'{timingstats} 定时注册', 'open_timing')],
                                   [('⭕ 注册限制', 'all_user_limit')], [('🌟 返回上一级', 'manage')]])


back_free_ikb = _create_telethon_buttons([[('🔙 返回上一级', 'open-menu')]])
back_open_menu_ikb = _create_telethon_buttons([[('🪪 重新定时', 'open_timing'), ('🔙 注册状态', 'open-menu')]])
re_cr_link_ikb = _create_telethon_buttons([[('♻️ 继续创建', 'cr_link'), ('🎗️ 返回主页', 'manage')]])
close_it_ikb = _create_telethon_buttons([[('❌ - Close', 'closeit')]])


def ch_link_ikb(ls: list) -> List[List[Button]]: # Assuming ls is list of button defs like [['text','data'],...]
    button_defs_flat = []
    for item in ls: # item is expected to be like ['text', 'data']
        if isinstance(item, list) and len(item) == 2:
             button_defs_flat.append(item)
        elif isinstance(item, tuple) and len(item) == 2: # Handle tuples too
             button_defs_flat.append(list(item))

    lines_of_button_defs = array_chunk(button_defs_flat, 2)
    lines_of_button_defs.append([["💫 回到首页", "manage"]])
    return _create_telethon_buttons(lines_of_button_defs)


def date_ikb(i) -> List[List[Button]]:
    return _create_telethon_buttons([[('🌘 - 月', f'register_mon_{i}'), ('🌗 - 季', f'register_sea_{i}'),
                                    ('🌖 - 半年', f'register_half_{i}')],
                                   [('🌕 - 年', f'register_year_{i}'), ('🌑 - 未用', f'register_unused_{i}'), ('🎟️ - 已用', f'register_used_{i}')],
                                   [('🔙 - 返回', 'ch_link')]])

# Helper for pagination logic
def _create_pagination_buttons(total_pages: int, current_page: int, callback_pattern: str, 
                               page_param_name: str = "{number}", 
                               max_buttons: int = 5,  # Number of page number buttons to show
                               nav_buttons: Optional[Dict[str, str]] = None, # e.g. {'first':'<<', 'prev':'<', ...}
                               extra_nav_row: Optional[List[Button]] = None
                               ) -> List[List[Button]]:
    buttons = []
    if total_pages <= 1:
        if extra_nav_row:
            buttons.append(extra_nav_row)
        return buttons

    # Page numbers row
    page_buttons_row = []
    
    start_page = max(1, current_page - max_buttons // 2)
    end_page = min(total_pages, start_page + max_buttons - 1)
    if end_page - start_page + 1 < max_buttons: # Adjust start_page if at the end
        start_page = max(1, end_page - max_buttons + 1)

    if nav_buttons and 'first' in nav_buttons and current_page > 1:
        page_buttons_row.append(Button.inline(nav_buttons['first'], callback_pattern.replace(page_param_name, "1").encode('utf-8')))
    if nav_buttons and 'prev' in nav_buttons and current_page > 1:
        page_buttons_row.append(Button.inline(nav_buttons['prev'], callback_pattern.replace(page_param_name, str(current_page - 1)).encode('utf-8')))

    for page_num in range(start_page, end_page + 1):
        text = f"[{page_num}]" if page_num == current_page else str(page_num)
        page_buttons_row.append(Button.inline(text, callback_pattern.replace(page_param_name, str(page_num)).encode('utf-8')))

    if nav_buttons and 'next' in nav_buttons and current_page < total_pages:
        page_buttons_row.append(Button.inline(nav_buttons['next'], callback_pattern.replace(page_param_name, str(current_page + 1)).encode('utf-8')))
    if nav_buttons and 'last' in nav_buttons and current_page < total_pages:
        page_buttons_row.append(Button.inline(nav_buttons['last'], callback_pattern.replace(page_param_name, str(total_pages)).encode('utf-8')))
    
    if page_buttons_row:
        buttons.append(page_buttons_row)
    
    # Additional navigation row (like "close" or "+5/-5 pages")
    if extra_nav_row:
        buttons.append(extra_nav_row)
        
    return buttons

# Generic pagination function
async def generate_pagination_keyboard(total_pages: int, current_page: int, base_callback_data: str, 
                                     page_arg_name: str = "page",  # e.g. "users_iv:{page}_{tg}" -> page_arg_name = "page"
                                     # For "pagination_keyboard:{number}_{n}" -> page_arg_name = "{number}"
                                     # This needs to be the placeholder that is replaced.
                                     # Let's assume the callback structure is "action:value_value_value:{page_placeholder}"
                                     # Or "action:{page_placeholder}_value_value"
                                     nav_row_buttons: Optional[List[Button]] = None,
                                     max_page_buttons: int = 7 # PyKeyboard default
                                     ) -> List[List[Button]]:
    
    keyboard_rows = []
    
    # Page number buttons
    if total_pages > 1:
        page_row = []
        
        # Determine the actual placeholder for page number
        if "{number}" in base_callback_data:
            page_placeholder = "{number}"
        elif "{page}" in base_callback_data: # Common alternative
            page_placeholder = "{page}"
        else: # Default or error
            LOGGER.warning(f"generate_pagination_keyboard: Could not determine page placeholder in {base_callback_data}")
            page_placeholder = "{number}" # Fallback

        # Simplified: << < Page > >>
        # More complex: 1 2 3 [4] 5 6 7 ... Last
        
        # First page button
        if current_page > 2 and total_pages > max_page_buttons : # Show if not in first few pages
            page_row.append(Button.inline("« 1", base_callback_data.replace(page_placeholder, "1").encode('utf-8')))

        # Prev page button
        if current_page > 1:
            page_row.append(Button.inline("‹", base_callback_data.replace(page_placeholder, str(current_page - 1)).encode('utf-8')))

        # Page number buttons (e.g., 3 to 5 page numbers)
        # Calculate start and end page numbers
        # This logic is from pykeyboard's paginate
        if total_pages <= max_page_buttons:
            start_page = 1
            end_page = total_pages
        else:
            start_page = max(1, current_page - (max_page_buttons // 2))
            end_page = start_page + max_page_buttons -1 
            if end_page > total_pages:
                end_page = total_pages
                start_page = max(1, end_page - max_page_buttons + 1)
        
        for i in range(start_page, end_page + 1):
            text = f"[{i}]" if i == current_page else str(i)
            page_row.append(Button.inline(text, base_callback_data.replace(page_placeholder, str(i)).encode('utf-8')))
        
        # Next page button
        if current_page < total_pages:
            page_row.append(Button.inline("›", base_callback_data.replace(page_placeholder, str(current_page + 1)).encode('utf-8')))

        # Last page button
        if current_page < total_pages -1 and total_pages > max_page_buttons : # Show if not in last few pages
            page_row.append(Button.inline(f"{total_pages} »", base_callback_data.replace(page_placeholder, str(total_pages)).encode('utf-8')))
            
        if page_row:
            keyboard_rows.append(page_row)

    if nav_row_buttons:
        keyboard_rows.append(nav_row_buttons)
        
    return keyboard_rows


# Old cr_paginate is removed / will be replaced by calls to generate_pagination_keyboard by specific functions.
# The functions below (users_iv_button, plays_list_button etc.) will be refactored to use generate_pagination_keyboard.

async def users_iv_button(total_page: int, current_page: int, tg_id: Union[int, str]) -> List[List[Button]]:
    base_callback = f"users_iv:{{number}}_{tg_id}"
    
    nav_buttons = [Button.inline('❌ 关闭', b'closeit')]
    if total_page > 5: # This +/- 5 logic is specific
        if current_page - 5 >= 1:
            nav_buttons.append(Button.inline('⏮️ 前进-5', f'users_iv:{current_page - 5}_{tg_id}'.encode('utf-8')))
        if current_page + 5 <= total_page: # Corrected logic for next +5
            nav_buttons.append(Button.inline('⏭️ 后退+5', f'users_iv:{current_page + 5}_{tg_id}'.encode('utf-8'))) # Note: text was "后退+5", callback implies next
            
    return await generate_pagination_keyboard(total_page, current_page, base_callback, nav_row_buttons=nav_buttons)


async def plays_list_button(total_page: int, current_page: int, days: int) -> List[List[Button]]:
    base_callback = f"uranks:{{number}}_{days}"
    nav_buttons = [Button.inline('❌ 关闭', b'closeit')]
    if total_page > 5:
        if current_page - 5 >= 1:
            nav_buttons.append(Button.inline('⏮️ 前进-5', f'uranks:{current_page - 5}_{days}'.encode('utf-8')))
        if current_page + 5 <= total_page:
            nav_buttons.append(Button.inline('⏭️ 后退+5', f'uranks:{current_page + 5}_{days}'.encode('utf-8')))
            
    return await generate_pagination_keyboard(total_page, current_page, base_callback, nav_row_buttons=nav_buttons)


async def store_query_page(total_page: int, current_page: int) -> List[List[Button]]:
    base_callback = "store-query:{number}"
    nav_buttons = [Button.inline('🔙 Back', b'storeall')]
    if total_page > 5:
        if current_page - 5 >= 1:
            nav_buttons.append(Button.inline('⏮️ 前进-5', f'store-query:{current_page - 5}'.encode('utf-8')))
        if current_page + 5 <= total_page:
            nav_buttons.append(Button.inline('⏭️ 后退+5', f'store-query:{current_page + 5}'.encode('utf-8')))
            
    return await generate_pagination_keyboard(total_page, current_page, base_callback, nav_row_buttons=nav_buttons)

async def whitelist_page_ikb(total_page: int, current_page: int) -> List[List[Button]]:
    base_callback = "whitelist:{number}"
    nav_buttons = [Button.inline('🔙 Back', b'manage')]
    if total_page > 5:
        if current_page - 5 >= 1:
            nav_buttons.append(Button.inline('⏮️ 前进-5', f'whitelist:{current_page - 5}'.encode('utf-8')))
        if current_page + 5 <= total_page:
            nav_buttons.append(Button.inline('⏭️ 后退+5', f'whitelist:{current_page + 5}'.encode('utf-8')))
    return await generate_pagination_keyboard(total_page, current_page, base_callback, nav_row_buttons=nav_buttons)

async def normaluser_page_ikb(total_page: int, current_page: int) -> List[List[Button]]:
    base_callback = "normaluser:{number}"
    nav_buttons = [Button.inline('🔙 Back', b'manage')]
    if total_page > 5:
        if current_page - 5 >= 1:
            nav_buttons.append(Button.inline('⏮️ 前进-5', f'normaluser:{current_page - 5}'.encode('utf-8')))
        if current_page + 5 <= total_page:
            nav_buttons.append(Button.inline('⏭️ 后退+5', f'normaluser:{current_page + 5}'.encode('utf-8')))
    return await generate_pagination_keyboard(total_page, current_page, base_callback, nav_row_buttons=nav_buttons)

def devices_page_ikb( has_prev: bool, has_next: bool, page: int) -> List[List[Button]]:
    button_rows: List[List[Button]] = []
    nav_row: List[Button] = []
    if has_prev:
        nav_row.append(Button.inline('⬅️', f'devices:{page-1}'.encode('utf-8')))
    nav_row.append(Button.inline(f'第 {page} 页', b'none')) # 'none' callback data
    if has_next:
        nav_row.append(Button.inline('➡️', f'devices:{page+1}'.encode('utf-8')))
    
    if nav_row: # Only add if there are nav buttons (e.g. not a single page with no prev/next)
        button_rows.append(nav_row)
    
    button_rows.append([Button.inline('🔙 返回', b'manage')])
    return button_rows

async def favorites_page_ikb(total_page: int, current_page: int) -> List[List[Button]]:
    base_callback = "page_my_favorites:{number}"
    nav_buttons = [Button.inline('🔙 Back', b'members')]
    if total_page > 5:
        if current_page - 5 >= 1:
            nav_buttons.append(Button.inline('⏮️ 前进-5', f'page_my_favorites:{current_page - 5}'.encode('utf-8')))
        if current_page + 5 <= total_page:
            nav_buttons.append(Button.inline('⏭️ 后退+5', f'page_my_favorites:{current_page + 5}'.encode('utf-8')))
    return await generate_pagination_keyboard(total_page, current_page, base_callback, nav_row_buttons=nav_buttons)

def cr_renew_ikb() -> List[List[Button]]:
    checkin_status = '✔️' if _open.checkin else '❌'
    exchange_status = '✔️' if _open.exchange else '❌'
    whitelist_status = '✔️' if _open.whitelist else '❌'
    invite_status = '✔️' if _open.invite else '❌'
    invite_lv_text = {
        'a': '白名单', 'b': '普通用户', 'c': '已禁用用户', 'd': '无账号用户'
    }.get(_open.invite_lv, '未知')

    buttons = [
        [
            Button.inline(f'{checkin_status} 每日签到', b'set_renew-checkin'),
            Button.inline(f'{exchange_status} 自动{sakura_b}续期', b'set_renew-exchange')
        ],
        [
            Button.inline(f'{whitelist_status} 兑换白名单', b'set_renew-whitelist'),
            Button.inline(f'{invite_status} 兑换邀请码', b'set_renew-invite')
        ],
        [
            Button.inline(f'邀请等级: {invite_lv_text}', b'set_invite_lv')
        ],
        [
            Button.inline(f'◀ 返回', b'manage')
        ]
    ]
    # The original pykeyboard had row_width=2, which means it would arrange the first 5 buttons
    # into 3 rows (2, 2, 1). The new structure above explicitly does this.
    # If the original intent was truly a fixed width for all, that's harder with List[List[Button]].
    # The provided structure seems to match the visual output of row_width=2 with the given buttons.
    return buttons

def invite_lv_ikb() -> List[List[Button]]:
    return _create_telethon_buttons([
        [('🅰️ 白名单', 'set_invite_lv-a'), ('🅱️ 普通用户', 'set_invite_lv-b')],
        [('©️ 已禁用用户', 'set_invite_lv-c'), ('🅳️ 无账号用户', 'set_invite_lv-d')],
        [('🔙 返回', 'set_renew')]
    ])

""" config_panel ↓"""


def config_preparation() -> List[List[Button]]:
    mp_set_status = '✅' if moviepilot.status else '❎'
    auto_up_status = '✅' if auto_update.status else '❎'
    leave_ban_status = '✅' if _open.leave_ban else '❎'
    uplays_status = '✅' if _open.uplays else '❎'
    fuxx_pt_status = '✅' if fuxx_pitao else '❎'
    red_envelope_status_val = '✅' if red_envelope.status else '❎'
    allow_private_status = '✅' if red_envelope.allow_private else '❎'
    
    button_defs = [
        [('📄 导出日志', 'log_out'), ('📌 设置探针', 'set_tz')],
        [('🎬 显/隐指定库', 'set_block'), (f'{fuxx_pt_status} 皮套人过滤功能', 'set_fuxx_pitao')],
        [('💠 普通用户线路', 'set_line'),('🌟 白名单线路', 'set_whitelist_line')],
        [(f'{leave_ban_status} 退群封禁', 'leave_ban'), (f'{uplays_status} 观影奖励结算', 'set_uplays')],
        [(f'{auto_up_status} 自动更新bot', 'set_update'), (f'{mp_set_status} Moviepilot点播', 'set_mp')],
        [(f'{red_envelope_status_val} 红包', 'set_red_envelope_status'), (f'{allow_private_status} 专属红包', 'set_red_envelope_allow_private')],
        [(f'设置赠送资格天数({kk_gift_days}天)', 'set_kk_gift_days')],
        [('🔙 返回', 'manage')]
    ]
    return _create_telethon_buttons(button_defs)


back_config_p_ikb = _create_telethon_buttons([[("🎮  ️返回主控", "back_config")]])


def back_set_ikb(method) -> List[List[Button]]:
    return _create_telethon_buttons([[("♻️ 重新设置", f"{method}"), ("🔙 返回主页", "back_config")]])


def try_set_buy(ls: list) -> List[List[Button]]:
    # Assuming ls is a single button definition like ['text', 'callback_data']
    # The original structure was d = [[ls], [["✅ 体验结束返回", "back_config"]]]
    # This means ls itself becomes a row.
    button_defs = [ls, [("✅ 体验结束返回", "back_config")]]
    return _create_telethon_buttons(button_defs)


""" other """
register_code_ikb = _create_telethon_buttons([[('🎟️ 注册', 'create'), ('⭕ 取消', 'closeit')]])
dp_g_ikb = _create_telethon_buttons([[("🈺 ╰(￣ω￣ｏ)", "t.me/Aaaaa_su", "url")]])


async def cr_kk_ikb(uid, first) -> tuple[str, Optional[List[List[Button]]]]:
    text_response = ''
    text1 = ''
    keyboard_button_defs_flat = [] 
    
    data = await members_info(uid)
    if data is None:
        text_response += f'**· 🆔 TG** ：[{first}](tg://user?id={uid}) [`{uid}`]\n数据库中没有此ID。ta 还没有私聊过我'
        return text_response, None
    else:
        name, lv, ex, us, embyid, pwd2 = data
        if name != '无账户信息':
            ban_text = "🌟 解除禁用" if lv == "**已禁用**" else '💢 禁用账户'
            keyboard_button_defs_flat.append([ban_text, f'user_ban-{uid}'])
            keyboard_button_defs_flat.append(['⚠️ 删除账户', f'closeemby-{uid}'])
            
            if len(extra_emby_libs) > 0:
                success, rep = emby.user(embyid=embyid)
                if success:
                    try:
                        currentblock = rep["Policy"]["BlockedMediaFolders"]
                    except KeyError:
                        currentblock = []
                    libs_status_text, embyextralib_callback = ['✖️', f'embyextralib_unblock-{uid}'] if set(extra_emby_libs).issubset(
                        set(currentblock)) else ['✔️', f'embyextralib_block-{uid}']
                    keyboard_button_defs_flat.append([f'{libs_status_text} 额外媒体库', embyextralib_callback])
            try:
                rst = await emby.emby_cust_commit(user_id=embyid, days=30)
                last_time = rst[0][0]
                toltime = rst[0][1]
                text1 = f"**· 🔋 上次活动** | {last_time.split('.')[0]}\n" \
                        f"**· 📅 过去30天** | {toltime} min"
            except (TypeError, IndexError, ValueError):
                text1 = f"**· 📅 过去30天未有记录**"
        else:
            keyboard.append(['✨ 赠送资格', f'gift-{uid}'])
        text += f"**· 🍉 TG&名称** | [{first}](tg://user?id={uid})\n" \
                f"**· 🍒 识别のID** | `{uid}`\n" \
                f"**· 🍓 当前状态** | {lv}\n" \
                f"**· 🍥 持有{sakura_b}** | {us}\n" \
                f"**· 💠 账号名称** | {name}\n" \
                f"**· 🚨 到期时间** | **{ex}**\n"
        text += text1
        keyboard.extend([['🚫 踢出并封禁', f'fuckoff-{uid}'], ['❌ 删除消息', f'closeit']])
        lines = array_chunk(keyboard, 2)
        keyboard = ikb(lines)
    return text, keyboard


def cv_user_playback_reporting(user_id):
    return ikb([[('🌏 播放查询', f'userip-{user_id}'), ('❌ 关闭', 'closeit')]])


def gog_rester_ikb(link=None) -> InlineKeyboardMarkup:
    link_ikb = ikb([[('🎁 点击领取', link, 'url')]]) if link else ikb([[('👆🏻 点击注册', f't.me/{bot_name}', 'url')]])
    return link_ikb


""" sched_panel ↓"""


def sched_buttons() -> List[List[Button]]:
    dayrank_s = '✅' if schedall.dayrank else '❎'
    weekrank_s = '✅' if schedall.weekrank else '❎'
    dayplayrank_s = '✅' if schedall.dayplayrank else '❎'
    weekplayrank_s = '✅' if schedall.weekplayrank else '❎'
    check_ex_s = '✅' if schedall.check_ex else '❎'
    low_activity_s = '✅' if schedall.low_activity else '❎'
    backup_db_s = '✅' if schedall.backup_db else '❎'
    
    buttons = [
        [
            Button.inline(f'{dayrank_s} 播放日榜', b'sched-dayrank'),
            Button.inline(f'{weekrank_s} 播放周榜', b'sched-weekrank')
        ],
        [
            Button.inline(f'{dayplayrank_s} 观影日榜', b'sched-dayplayrank'),
            Button.inline(f'{weekplayrank_s} 观影周榜', b'sched-weekplayrank')
        ],
        [
            Button.inline(f'{check_ex_s} 到期保号', b'sched-check_ex'),
            Button.inline(f'{low_activity_s} 活跃保号', b'sched-low_activity')
        ],
        [
            Button.inline(f'{backup_db_s} 自动备份数据库', b'sched-backup_db')
        ],
        [
            Button.inline(f'🫧 返回', b'manage')
        ]
    ]
    # Original was row_width=2, which would arrange the 7 main buttons as 2,2,2,1.
    # The above explicit structure is similar.
    return buttons


""" checkin 按钮↓"""

# def shici_button(ls: list):
#     shici = []
#     for l in ls:
#         l = [l, f'checkin-{l}']
#         shici.append(l)
#     # print(shici)
#     lines = array_chunk(shici, 4)
#     return ikb(lines)


# checkin_button = ikb([[('🔋 重新签到', 'checkin'), ('🎮 返回主页', 'back_start')]])

""" Request_media """

# request_tips_ikb was already None
request_tips_ikb = None


def get_resource_ikb(download_name: str) -> List[List[Button]]:
    button_defs = [
        [(f'下载本片', f'download_{download_name}'), ('激活订阅', f'submit_{download_name}')],
        [('❌ 关闭', 'closeit')]
    ]
    return _create_telethon_buttons(button_defs)

re_download_center_ikb = _create_telethon_buttons([
    [('🍿 点播', 'get_resource'), ('📶 下载进度', 'download_rate')], 
    [('🔙 返回', 'members')]
])

continue_search_ikb = _create_telethon_buttons([
    [('🔄 继续搜索', 'continue_search'), ('❌ 取消搜索', 'cancel_search')],
    [('🔙 返回', 'download_center')]
])

def download_resource_ids_ikb(resource_ids: list) -> List[List[Button]]:
    button_defs_rows = [] 
    current_row: List[Any] = []
    for res_id in resource_ids:
        current_row.append([f"资源编号: {res_id}", f'download_resource_id_{res_id}'])
        if len(current_row) == 2:
            button_defs_rows.append(current_row)
            current_row = []
    if current_row: 
        button_defs_rows.append(current_row)
        
    button_defs_rows.append([('❌ 取消', 'cancel_download')])
    return _create_telethon_buttons(button_defs_rows)

def request_record_page_ikb(has_prev: bool, has_next: bool) -> List[List[Button]]:
    nav_row_defs = []
    if has_prev:
        nav_row_defs.append(('< 上一页', 'request_record_prev'))
    if has_next:
        nav_row_defs.append(('下一页 >', 'request_record_next'))
    
    button_defs = []
    if nav_row_defs: # Only add the nav row if there's something in it
        button_defs.append(nav_row_defs)
    button_defs.append([('🔙 返回', 'download_center')])
    return _create_telethon_buttons(button_defs)

def mp_search_page_ikb(has_prev: bool, has_next: bool, page: int) -> List[List[Button]]: # Added page param (original had it)
    nav_row_defs = []
    if has_prev:
        nav_row_defs.append(('< 上一页', 'mp_search_prev_page'))
    if has_next:
        nav_row_defs.append(('下一页 >', 'mp_search_next_page'))
        
    button_defs = []
    if nav_row_defs:
        button_defs.append(nav_row_defs)
    # Original ikb call implies these buttons are on the same row after pagination buttons
    # but _create_telethon_buttons expects a list of rows.
    # Assuming they should be on a new row or combined if possible.
    # For simplicity, putting them on new rows if nav_row_defs exists, else one row.
    action_buttons = [('💾 选择下载', 'mp_search_select_download'), ('❌ 取消搜索', 'cancel_search')]
    if nav_row_defs:
         button_defs.append(action_buttons)
    else: # if no nav buttons, put them on the first row
         button_defs = [action_buttons]
        
    return _create_telethon_buttons(button_defs)

# 添加 MoviePilot 设置按钮
def mp_config_ikb() -> List[List[Button]]:
    """MoviePilot 设置面板按钮"""
    mp_status_val = '✅' if moviepilot.status else '❎'
    # lv_text was defined but not used in the original ikb structure for this func.
    button_defs = [
        [(f'{mp_status_val} 点播功能', 'set_mp_status')],
        [('💰 设置点播价格', 'set_mp_price'), ('👥 设置用户权限', 'set_mp_lv')],
        [('📝 设置日志频道', 'set_mp_log_channel')],
        [('🔙 返回', 'back_config')]
    ]
    return _create_telethon_buttons(button_defs)