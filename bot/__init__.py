#! /usr/bin/python3
# -*- coding: utf-8 -*-
import contextlib

from .func_helper.logger_config import logu, Now

LOGGER = logu(__name__)

from .schemas import Config

config = Config.load_config()


def save_config():
    config.save_config()


'''从config对象中获取属性值'''
# bot
bot_name = config.bot_name
bot_token = config.bot_token
owner_api = config.owner_api
owner_hash = config.owner_hash
owner = config.owner
group = config.group
main_group = config.main_group
chanel = config.chanel
bot_photo = config.bot_photo
_open = config.open
admins = config.admins
sakura_b = config.money
ranks = config.ranks
prefixes = ['/', '!', '.', '，', '。']
schedall = config.schedall
# emby设置
emby_api = config.emby_api
emby_url = config.emby_url
emby_line = config.emby_line
emby_whitelist_line = config.emby_whitelist_line
emby_block = config.emby_block
extra_emby_libs = config.extra_emby_libs
# # 数据库
db_host = config.db_host
db_user = config.db_user
db_pwd = config.db_pwd
db_name = config.db_name
db_port = config.db_port
db_is_docker = config.db_is_docker
db_docker_name = config.db_docker_name
db_backup_dir = config.db_backup_dir
db_backup_maxcount = config.db_backup_maxcount
# 探针
tz_ad = config.tz_ad
tz_api = config.tz_api
tz_id = config.tz_id

w_anti_channel_ids = config.w_anti_channel_ids
kk_gift_days = config.kk_gift_days
fuxx_pitao = config.fuxx_pitao
red_envelope = config.red_envelope

moviepilot = config.moviepilot
auto_update = config.auto_update
api = config.api
save_config()

LOGGER.info("配置文件加载完毕")

'''定义不同等级的人使用不同命令'''
user_p = [
    {'command': "start", 'description': "[私聊] 开启用户面板"},
    {'command': "myinfo", 'description': "[用户] 查看状态"},
    {'command': "count", 'description': "[用户] 媒体库数量"},
    {'command': "red", 'description': "[用户/禁言] 发红包"},
    {'command': "srank", 'description': "[用户/禁言] 查看计分"}]

# 取消 BotCommand("exchange", "[私聊] 使用注册码")
admin_p = user_p + [
    {'command': "kk", 'description': "管理用户 [管理]"},
    {'command': "score", 'description': "加/减积分 [管理]"},
    {'command': "coins", 'description': f"加/减{sakura_b} [管理]"},
    {'command': "deleted", 'description': f"清理死号 [管理]"},
    {'command': "kick_not_emby", 'description': f"踢出当前群内无号崽 [管理]"},
    {'command': "renew", 'description': "调整到期时间 [管理]"},
    {'command': "rmemby", 'description': "删除用户[包括非tg] [管理]"},
    {'command': "prouser", 'description': "增加白名单 [管理]"},
    {'command': "revuser", 'description': "减少白名单 [管理]"},
    {'command': "rev_white_channel", 'description': "移除皮套人白名单 [管理]"},
    {'command': "white_channel", 'description': "添加皮套人白名单 [管理]"},
    {'command': "unban_channel", 'description': "解封皮套人 [管理]"},
    {'command': "syncgroupm", 'description': "消灭不在群的人 [管理]"},
    {'command': "syncunbound", 'description': "消灭未绑定bot的emby账户 [管理]"},
    {'command': "scan_embyname", 'description': "扫描同名的用户记录 [管理]"},
    {'command': "low_activity", 'description': "手动运行活跃检测 [管理]"},
    {'command': "check_ex", 'description': "手动到期检测 [管理]"},
    {'command': "uranks", 'description': "召唤观影时长榜，失效时用 [管理]"},
    {'command': "days_ranks", 'description': "召唤播放次数日榜，失效时用 [管理]"},
    {'command': "week_ranks", 'description': "召唤播放次数周榜，失效时用 [管理]"},
    {'command': "sync_favorites", 'description': "同步收藏记录 [管理]"},
    {'command': "embyadmin", 'description': "开启emby控制台权限 [管理]"},
    {'command': "ucr", 'description': "私聊创建非tg的emby用户 [管理]"},
    {'command': "uinfo", 'description': "查询指定用户名 [管理]"},
    {'command': "urm", 'description': "删除指定用户名 [管理]"},
    {'command': "only_rm_emby", 'description': "删除指定的Emby账号 [管理]"},
    {'command': "only_rm_record", 'description': "删除指定的tgid数据库记录 [管理]"},
    {'command': "restart", 'description': "重启bot [管理]"},
    {'command': "update_bot", 'description': "更新bot [管理]"},
]

owner_p = admin_p + [
    {'command': "proadmin", 'description': "添加bot管理 [owner]"},
    {'command': "revadmin", 'description': "移除bot管理 [owner]"},
    {'command': "renewall", 'description': "一键派送天数给所有未封禁的用户 [owner]"},
    {'command': "coinsall", 'description': "一键派送币币给所有未封禁的用户 [owner]"},
    {'command': "callall", 'description': "群发消息给每个人 [owner]"},
    {'command': "bindall_id", 'description': "一键更新用户们Embyid [owner]"},
    {'command': "backup_db", 'description': "手动备份数据库[owner]"},
    {'command': 'restore_from_db', 'description': '恢复Emby账户[owner]'},
    {'command': "config", 'description': "开启bot高级控制面板 [owner]"},
    {'command': "embylibs_unblockall", 'description': "一键开启所有用户的媒体库 [owner]"},
    {'command': "embylibs_blockall", 'description': "一键关闭所有用户的媒体库 [owner]"}]
if len(extra_emby_libs) > 0:
    owner_p += [{'command': "extraembylibs_blockall", 'description': "一键关闭所有用户的额外媒体库 [owner]"},
                {'command': "extraembylibs_unblockall", 'description': "一键开启所有用户的额外媒体库 [owner]"}]

with contextlib.suppress(ImportError):
    import uvloop

    uvloop.install()
from telethon import TelegramClient

# Prepare Telethon proxy configuration
telethon_proxy = None
if config.proxy.scheme and config.proxy.hostname and config.proxy.port:
    proxy_username = config.proxy.username if hasattr(config.proxy, 'username') and config.proxy.username else None
    proxy_password = config.proxy.password if hasattr(config.proxy, 'password') and config.proxy.password else None
    
    scheme_lower = config.proxy.scheme.lower()
    if scheme_lower == 'socks5':
        telethon_proxy = {
            'proxy_type': 'socks5',
            'addr': config.proxy.hostname,
            'port': config.proxy.port,
            'username': proxy_username,
            'password': proxy_password,
            'rdns': True
        }
    elif scheme_lower in ['http', 'https']:
        # For HTTP proxies, Telethon typically expects a dictionary like SOCKS
        # or relies on environment variables. The tuple format is less common for TelegramClient constructor.
        # A common dict format for HTTP:
        telethon_proxy = {
            'proxy_type': 'http', # Explicitly 'http' often needed if scheme is 'http' or 'https'
            'addr': config.proxy.hostname,
            'port': config.proxy.port,
            'username': proxy_username,
            'password': proxy_password,
            'rdns': True 
        }
        # If the scheme was 'https', some libraries expect 'https' as proxy_type or handle it via 'http' type.
        # Sticking to 'http' type for `telethon_proxy` dictionary structure as it's more common.
    # Add more proxy schemes here if necessary, e.g., MTProto

client_args = {
    'api_id': owner_api,
    'api_hash': owner_hash
}
if telethon_proxy:
    client_args['proxy'] = telethon_proxy

# Note: bot_token is not passed here. It will be used in bot.start(bot_token=bot_token) in main.py
# Parameters like workers, max_concurrent_transmissions are not directly applicable.
# Telethon uses asyncio for concurrency. ParseMode defaults to Markdown.
bot = TelegramClient(
    bot_name,  # session file name
    **client_args
)

LOGGER.info("Telethon Client 客户端准备")
