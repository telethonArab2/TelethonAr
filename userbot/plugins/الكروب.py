import asyncio
import time
import io
import os
import shutil
import zipfile
import base64
from telethon.tl.functions.messages import EditChatDefaultBannedRightsRequest
from telethon.tl.functions.messages import ImportChatInviteRequest as Get
from datetime import datetime
from asyncio import sleep
from asyncio.exceptions import TimeoutError
from telethon import functions, types
from telethon import events
from telethon.tl.functions.channels import EditBannedRequest, GetFullChannelRequest, GetParticipantsRequest, EditAdminRequest, EditPhotoRequest
from telethon.tl.functions.users import GetFullUserRequest
from telethon.tl.functions.messages import GetFullChatRequest, GetHistoryRequest, ExportChatInviteRequest
from telethon.errors import ChannelInvalidError, ChannelPrivateError, ChannelPublicGroupNaError, BadRequestError, ChatAdminRequiredError, FloodWaitError, MessageNotModifiedError, UserAdminInvalidError
from telethon.errors.rpcerrorlist import YouBlockedUserError, UserAdminInvalidError, UserIdInvalidError
from telethon.tl.functions.channels import GetFullChannelRequest as getchat
from telethon.tl.functions.phone import CreateGroupCallRequest as startvc
from telethon.tl.functions.phone import DiscardGroupCallRequest as stopvc
from telethon.tl.functions.phone import GetGroupCallRequest as getvc
from telethon.tl.functions.phone import InviteToGroupCallRequest as invitetovc
from telethon.errors import ImageProcessFailedError, PhotoCropSizeSmallError
from telethon.tl.types import ChatAdminRights, InputChatPhotoEmpty, MessageMediaPhoto
from telethon.tl.types import ChannelParticipantsKicked, ChannelParticipantAdmin, ChatBannedRights, ChannelParticipantCreator, ChannelParticipantsAdmins, ChannelParticipantsBots, MessageActionChannelMigrateFrom, UserStatusEmpty, UserStatusLastMonth, UserStatusLastWeek, UserStatusOffline, UserStatusOnline, UserStatusRecently
from telethon.utils import get_display_name, get_input_location, get_extension
from os import remove
from math import sqrt
from prettytable import PrettyTable
from emoji import emojize
from pathlib import Path
from userbot import iqthon
from userbot.utils import admin_cmd, sudo_cmd, eor
from ..core.logger import logging
from ..core.managers import edit_delete, edit_or_reply
from . import humanbytes
from . import BOTLOG, BOTLOG_CHATID, admin_groups, get_user_from_event, extract_time
from ..utils.tools import create_supergroup
from ..helpers import reply_id, readable_time
from ..helpers.utils import _format, get_user_from_event, reply_id
from ..helpers import media_type
from ..helpers.google_image_download import googleimagesdownload
from ..helpers.tools import media_type
from ..sql_helper.locks_sql import get_locks, is_locked, update_lock
from ..utils import is_admin
from . import progress
from ..sql_helper import gban_sql_helper as gban_sql
from ..sql_helper.mute_sql import is_muted, mute, unmute
from ..sql_helper.autopost_sql import add_post, get_all_post, is_post, remove_post
from ..sql_helper import no_log_pms_sql
from ..sql_helper.globals import addgvar, gvarstatus
BANNED_RIGHTS = ChatBannedRights(until_date=None, view_messages=True, send_messages=True, send_media=True, send_stickers=True, send_gifs=True, send_games=True, send_inline=True, embed_links=True)
KLANR_RIGHTS = ChatBannedRights(until_date=None, view_messages=True, send_messages=True, send_media=True, send_stickers=True, send_gifs=True, send_games=True, send_inline=True, embed_links=True)
UNBAN_RIGHTS = ChatBannedRights(
    until_date=None,
    send_messages=None,
    send_media=None,
    send_stickers=None,
    send_gifs=None,
    send_games=None,
    send_inline=None,
    embed_links=None,
)
LOGS = logging.getLogger(__name__)
plugin_category = "utils"
MUTE = gvarstatus("OR_MUTE") or "(ميوت|كتم)"
TFLASH = gvarstatus("OR_TFLASH") or "(طرد الكل|تفليش)"
UNMUTE = gvarstatus("OR_UNMUTE") or "(ميوت|كتم)"
addition = gvarstatus("OR_ADD") or "(أضافه|اضافه)"
LEFT = gvarstatus("OR_LEFT") or "(مغادره|غادر)"
REMOVEBAN = gvarstatus("OR_REMOVEBAN") or "مسح المحظورين"
LINKK = gvarstatus("OR_LINK") or "(رابط|الرابط)"
ADMINRAISE = gvarstatus("OR_ADMINRAISE") or "رفع مشرف"
UNADMINRAISE = gvarstatus("OR_UNADMINRAISE") or "تنزيل مشرف"
BANDD = gvarstatus("OR_BAND") or "جظر"
UNBANDD = gvarstatus("OR_UNBAND") or "الغاء الحظر"
TYPES = [
    "Photo",
    "Audio",
    "Video",
    "Document",
    "Sticker",
    "Gif",
    "Voice",
    "Round Video",
]
thumb_image_path = os.path.join(Config.TMP_DOWNLOAD_DIRECTORY, "thumb_image.jpg")
from userbot import iqthon
try:
    import pyminizip
except Exception:
    os.system("pip install pyminizip")
    import pyminizip
err = "قم بالرد على الملف"

async def get_call(event):
    mm = await event.client(getchat(event.chat_id))
    xx = await event.client(getvc(mm.full_chat.call))
    return xx.call

def user_list(l, n):
    for i in range(0, len(l), n):
        yield l[i : i + n]

def zipdir(dirName):
    filePaths = []
    for root, directories, files in os.walk(dirName):
        for filename in files:
            filePath = os.path.join(root, filename)
            filePaths.append(filePath)
    return filePaths

class LOG_CHATS:
    def __init__(self):
        self.RECENT_USER = None
        self.NEWPM = None
        self.COUNT = 0
LOG_CHATS_ = LOG_CHATS()

PP_TOO_SMOL = "**⎈ ⦙  الصورة صغيرة جدًا  📸** ."
PP_ERROR = "**⎈ ⦙  فشل أثناء معالجة الصورة  📵** ."
NO_ADMIN = "**⎈ ⦙  أنا لست مشرف هنا ** ."
NO_PERM = "**⎈ ⦙  ليس لدي أذونات كافية  🚮** ."
CHAT_PP_CHANGED = "**⎈ ⦙  تغيّرت صورة الدردشة  🌅** ."
INVALID_MEDIA = "**⎈ ⦙ ملحق غير صالح  📳** ."
IMOGE_IQTHON = "⎈ ⦙  "
NO_ADMIN = "**⎈ ⦙ عذرا لست ادمن هنا **"
NO_PERM = "**⎈ ⦙ ليس لدي صلاحيات ادمن كافية! **"


@iqthon.on(admin_cmd(pattern=r"المحظورين?(.*)"))
async def gablist(event):
    gbanned_users = gban_sql.get_all_gbanned()
    GBANNED_LIST = "Current Gbanned Users\n"
    if len(gbanned_users) > 0:
        for a_user in gbanned_users:
            if a_user.reason:
                GBANNED_LIST += f"👉 [{a_user.chat_id}](tg://user?id={a_user.chat_id}) for {a_user.reason}\n"
            else:
                GBANNED_LIST += (
                    f"👉 [{a_user.chat_id}](tg://user?id={a_user.chat_id}) Reason None\n"
                )
    else:
        GBANNED_LIST = "لايوجد محضورين "
    await edit_or_reply(event, GBANNED_LIST)
@iqthon.on(admin_cmd(pattern="تشفير الملف ?(.*)"))
async def pyZip(e):
    if e.fwd_from:
        return
    reply = await e.get_reply_message()
    if not (reply and reply.media):
        return await eod(e, err)
    pass_ = e.pattern_match.group(1)
    eris = await edit_or_reply(e, "-->جاري التحميل ..<--")
    dl_ = await e.client.download_media(reply)
    await eris.edit("-->تم الاكتمال ..<--")
    nem_ = reply.file.name
    zip_ = f"{nem_}.zip" if nem_ else "iqthon_Zip.zip"
    password = pass_ if pass_ else "iqthon"
    cap_ = f"**اسم الملف :** - {zip_} \n"\
    f"**الباسبورد لفك الملف :** - `{password}`"
    
    pyminizip.compress(
        dl_, None, zip_, password, 5)
    await eris.edit("-->جاري الرفع ..<--")
    try:
        await e.client.send_file(
            e.chat_id, zip_, caption=cap_)
        await eris.delete()
    except Exception as ex:
        return await eris.edit(f"#هناك خطا : {ex}")
    finally:
        os.remove(zip_)
        os.remove(dl_)
@iqthon.on(admin_cmd(pattern=f"{MUTE}(?:\s|$)([\s\S]*)"))
async def startgmute(event):
    if event.is_private:
        await event.edit("**⎈ ⦙   جاري الكتم**")
        await asyncio.sleep(2)
        userid = event.chat_id
        reason = event.pattern_match.group(1)
    else:
        user, reason = await get_user_from_event(event)
        if not user:
            return
        if user.id == iqthon.uid:
            return await edit_or_reply(
                event, "**⎈ ⦙   لا يـمكنك كتم نـفسك**"
            )
        userid = user.id
    try:
        user = (await event.client(GetFullUserRequest(userid))).user
    except Exception:
        return await edit_or_reply(            event, "**⎈ ⦙   غيـر قـادر عـلى جـلب مـعلومات الـشخص **"        )
    if is_muted(userid, "كتم_مؤقت"):
        return await edit_or_reply(            event,            f"**⎈ ⦙   تـم كـتم الـمستـخدم بـنجاح ✅**",        )
    try:
        mute(userid, "كتم_مؤقت")
    except Exception as e:
        await edit_or_reply(event, f"**خـطأ**\n`{e}`")
    else:
        if reason:
            await edit_or_reply(
                event,
                f"**⎈ ⦙   تـم كـتم الـمستـخدم بـنجاح ✅**",
            )
        else:
            await edit_or_reply(
                event,
                f"**⎈ ⦙   تـم كـتم الـمستـخدم بـنجاح ✅**",
            )
    if BOTLOG:
        reply = await event.get_reply_message()
        if reason:
            await event.client.send_message(
                BOTLOG_CHATID,
                f"**⎈ ⦙   الـمستخدم** {_format.mentionuser(user.first_name ,user.id)}\n **⎈ ⦙   تـم كتمه بنـجاح**\n **⎈ ⦙   الدردشـة** {event.chat.title}\n"
                f"**⎈ ⦙   السـبب:** {reason}",
            )
        else:
            await event.client.send_message(
                BOTLOG_CHATID,
                f"**⎈ ⦙   الـمستخدم** {_format.mentionuser(user.first_name ,user.id)} \n**⎈ ⦙   تـم كتمه بنـجاح**",
            )
        if reply:
            await reply.forward_to(BOTLOG_CHATID)

@iqthon.on(admin_cmd(pattern=f"{UNMUTE}(?:\s|$)([\s\S]*)"))
async def endgmute(event):
    if event.is_private:
        await event.edit("**⎈ ⦙   قـد تـحدث بعـض الأخـطاء**")
        await asyncio.sleep(2)
        userid = event.chat_id
        reason = event.pattern_match.group(1)
    else:
        user, reason = await get_user_from_event(event)
        if not user:
            return
        if user.id == iqthon.uid:
            return await edit_or_reply(event, "**⎈ ⦙   لا يـمكنك كتم نـفسك**")
        userid = user.id
    try:
        user = (await event.client(GetFullUserRequest(userid))).user
    except Exception:
        return await edit_or_reply(
            event, "**⎈ ⦙   غيـࢪ قـادࢪ عـلى جـلب مـعلومات الـشخص **"
        )
    if not is_muted(userid, "كتم_مؤقت"):
        return await edit_or_reply(event, f"**⎈ ⦙   هـذا الـمستخدم لـيس مكـتوم**")
    try:
        unmute(userid, "كتم_مؤقت")
    except Exception as e:
        await edit_or_reply(event, f"**خـطأ **\n`{e}`")
    else:
        if reason:
            await edit_or_reply(
                event,
                f"**⎈ ⦙   تـم الـغاء كـتم الـمستـخدم بـنجاح**",
            )
        else:
            await edit_or_reply(
                event,
                f"**⎈ ⦙   تـم الـغاء كـتم الـمستـخدم بـنجاح**",
            )
    if BOTLOG:
        if reason:
            await event.client.send_message(
                BOTLOG_CHATID,
                "**⎈ ⦙   الـغاء الكـتم**\n"
                f"**⎈ ⦙   الـمستخدم :* {_format.mentionuser(user.first_name ,user.id)} \n"
                f"**⎈ ⦙   السبب :** `{reason}`",
            )
        else:
            await event.client.send_message(
                BOTLOG_CHATID,
                 "**⎈ ⦙   الـغاء الكـتم**\n"
                f"**⎈ ⦙   المستخدم :** {_format.mentionuser(user.first_name ,user.id)} \n",
            )

@iqthon.iq_cmd(incoming=True)
async def watcher(event):
    if is_muted(event.sender_id, "كتم_مؤقت"):
        await event.delete()

@iqthon.on(admin_cmd(pattern=r"المشرفين(?: |$)(.*)"))
async def _(event):
    "لإظهـار قائمـة المشرفيـن  ✪"
    mentions = "**⎈ ⦙   مشرفيـن هـذه المجموعـة  ✪**: \n"
    reply_message = await reply_id(event)
    input_str = event.pattern_match.group(1)
    to_write_chat = await event.get_input_chat()
    chat = None
    if input_str:
        mentions = f"**⎈ ⦙  مشرفيـن فـي → :** {input_str} **مـن المجموعـات ⌂ :** \n"
        try:
            chat = await event.client.get_entity(input_str)
        except Exception as e:
            return await edit_delete(event, str(e))
    else:
        chat = to_write_chat
        if not event.is_group:
            return await edit_or_reply(event, "**⎈ ⦙   هـذه ليسـت مجموعـة ✕**")
    try:
        async for x in event.client.iter_participants(
            chat, filter=ChannelParticipantsAdmins
        ):
            if not x.deleted and isinstance(x.participant, ChannelParticipantCreator):
                mentions += "\n - [{}](tg://user?id={}) `{}`".format(
                    x.first_name, x.id, x.id
                )
        mentions += "\n"
        async for x in event.client.iter_participants(
            chat, filter=ChannelParticipantsAdmins
        ):
            if x.deleted:
                mentions += "\n `{}`".format(x.id)
            else:
                if isinstance(x.participant, ChannelParticipantAdmin):
                    mentions += "\n- [{}](tg://user?id={}) `{}`".format(
                        x.first_name, x.id, x.id
                    )
    except Exception as e:
        mentions += " " + str(e) + "\n"
    await event.client.send_message(event.chat_id, mentions, reply_to=reply_message)
    await event.delete()

@iqthon.on(admin_cmd(pattern=r"البوتات?(.*)"))
async def _(event):
    mentions = "**⎈ ⦙  البـوتات في هذه الـمجموعة 🝰 : ** \n"
    input_str = event.pattern_match.group(1)
    if not input_str:
        chat = await event.get_input_chat()
    else:
        mentions = "**⎈ ⦙  البوتـات في {} من المجموعات 🝰 : ** \n".format(input_str)
        try:
            chat = await event.client.get_entity(input_str)
        except Exception as e:
            return await edit_or_reply(event, str(e))
    try:
        async for x in event.client.iter_participants(
            chat, filter=ChannelParticipantsBots
        ):
            if isinstance(x.participant, ChannelParticipantAdmin):
                mentions += "\n - [{}](tg://user?id={}) `{}`".format(x.first_name, x.id, x.id)
            else:
                mentions += "\n [{}](tg://user?id={}) `{}`".format(
                    x.first_name, x.id, x.id
                )
    except Exception as e:
        mentions += " " + str(e) + "\n"
    await edit_or_reply(event, mentions)


@iqthon.on(admin_cmd(pattern=r"الأعضاء(?: |$)(.*)"))
async def get_users(show):
    mentions = "**مستخدمين هذه المجموعة**: \n"
    await reply_id(show)
    input_str = show.pattern_match.group(1)
    if input_str:
        mentions = "**⎈ ⦙  الأعضاء في {} من المجموعات 𖤍  :** \n".format(input_str)
        try:
            chat = await show.client.get_entity(input_str)
        except Exception as e:
            return await edit_delete(show, f"`{str(e)}`", 10)
    else:
        if not show.is_group:
            return await edit_or_reply(show, "**⎈ ⦙  هـذه ليسـت مجموعـة ✕**")
    catevent = await edit_or_reply(show, "**⎈ ⦙  جـاري سحـب قائمـة معرّفـات الأعضـاء 🝛**")
    try:
        if show.pattern_match.group(1):
            async for user in show.client.iter_participants(chat.id):
                if user.deleted:
                    mentions += f"\n**⎈ ⦙  الحسـابات المحذوفـة ⌦** `{user.id}`"
                else:
                    mentions += (f"\n[{user.first_name}](tg://user?id={user.id}) `{user.id}`")
        else:
            async for user in show.client.iter_participants(show.chat_id):
                if user.deleted:
                    mentions += f"\n**⎈ ⦙  الحسـابات المحذوفـة ⌦** `{user.id}`"
                else:
                    mentions += (f"\n[{user.first_name}](tg://user?id={user.id}) `{user.id}`")
    except Exception as e:
        mentions += " " + str(e) + "\n"
    await edit_or_reply(catevent, mentions)

@iqthon.on(admin_cmd(pattern=r"معلومات(?: |$)(.*)"))
async def info(event):
    catevent = await edit_or_reply(event, "**⎈ ⦙  يتـمّ جلـب معلومـات الدردشـة، إنتظـر ⅏**")
    chat = await get_chatinfo(event, catevent)
    caption = await fetch_info(chat, event)
    try:
        await catevent.edit(caption, parse_mode="html")
    except Exception as e:
        if BOTLOG:
            await event.client.send_message(BOTLOG_CHATID, f"**⎈ ⦙  هنـاك خطـأ في معلومـات الدردشـة ✕ : **\n`{str(e)}`")
        await catevent.edit("**⎈ ⦙   حـدث خـطأ مـا، يرجـى التحقق من الأمـر ⎌**")
async def get_chatinfo(event, catevent):
    chat = event.pattern_match.group(1)
    chat_info = None
    if chat:
        try:
            chat = int(chat)
        except ValueError:
            pass
    if not chat:
        if event.reply_to_msg_id:
            replied_msg = await event.get_reply_message()
            if replied_msg.fwd_from and replied_msg.fwd_from.channel_id is not None:
                chat = replied_msg.fwd_from.channel_id
        else:
            chat = event.chat_id
    try:
        chat_info = await event.client(GetFullChatRequest(chat))
    except BaseException:
        try:
            chat_info = await event.client(GetFullChannelRequest(chat))
        except ChannelInvalidError:
            await catevent.edit("**⎈ ⦙  لـم يتـمّ العثـور على القنـاة/المجموعـة ✕**")
            return None
        except ChannelPrivateError:
            await catevent.edit(
                '**⎈ ⦙   هـذه مجموعـة أو قنـاة خاصـة أو لقد تمّ حظـري منه ⛞**'
            )
            return None
        except ChannelPublicGroupNaError:
            await catevent.edit("**⎈ ⦙  القنـاة أو المجموعـة الخارقـة غيـر موجـودة ✕**")
            return None
        except (TypeError, ValueError) as err:
            await catevent.edit(str(err))
            return None
    return chat_info

async def get_chatinfo(event):
    chat = event.pattern_match.group(1)
    chat_info = None
    if chat:
        try:
            chat = int(chat)
        except ValueError:
            pass
    if not chat:
        if event.reply_to_msg_id:
            replied_msg = await event.get_reply_message()
            if replied_msg.fwd_from and replied_msg.fwd_from.channel_id is not None:
                chat = replied_msg.fwd_from.channel_id
        else:
            chat = event.chat_id
    try:
        chat_info = await event.client(GetFullChatRequest(chat))
    except:
        try:
            chat_info = await event.client(GetFullChannelRequest(chat))
        except ChannelInvalidError:
            await event.reply("**⎈ ⦙   لم يتم العثور على المجموعة او القناة**")
            return None
        except ChannelPrivateError:
            await event.reply(
                "**⎈ ⦙   لا يمكنني استخدام الامر من الكروبات او القنوات الخاصة**"
            )
            return None
        except ChannelPublicGroupNaError:
            await event.reply("**⎈ ⦙   لم يتم العثور على المجموعة او القناة**")
            return None
        except (TypeError, ValueError):
            await event.reply("**⎈ ⦙   رابط الكروب غير صحيح**")
            return None
    return chat_info


def make_mention(user):
    if user.username:
        return f"@{user.username}"
    else:
        return inline_mention(user)


def inline_mention(user):
    full_name = user_full_name(user) or "No Name"
    return f"[{full_name}](tg://user?id={user.id})"


def user_full_name(user):
    names = [user.first_name, user.last_name]
    names = [i for i in list(names) if i]
    full_name = " ".join(names)
    return full_name


async def fetch_info(chat, event):  # sourcery no-metrics
    # chat.chats is a list so we use get_entity() to avoid IndexError
    chat_obj_info = await event.client.get_entity(chat.full_chat.id)
    broadcast = (
        chat_obj_info.broadcast if hasattr(chat_obj_info, "broadcast") else False
    )
    chat_type = "Channel" if broadcast else "Group"
    chat_title = chat_obj_info.title
    warn_emoji = emojize(":warning:")
    try:
        msg_info = await event.client(
            GetHistoryRequest(
                peer=chat_obj_info.id,
                offset_id=0,
                offset_date=datetime(2010, 1, 1),
                add_offset=-1,
                limit=1,
                max_id=0,
                min_id=0,
                hash=0,
            )
        )
    except Exception as e:
        msg_info = None
        LOGS.error(f"Exception: {str(e)}")
   
    first_msg_valid = bool(
        msg_info and msg_info.messages and msg_info.messages[0].id == 1
    )

    
    creator_valid = bool(first_msg_valid and msg_info.users)
    creator_id = msg_info.users[0].id if creator_valid else None
    creator_firstname = (
        msg_info.users[0].first_name
        if creator_valid and msg_info.users[0].first_name is not None
        else "Deleted Account"
    )
    creator_username = (
        msg_info.users[0].username
        if creator_valid and msg_info.users[0].username is not None
        else None
    )
    created = msg_info.messages[0].date if first_msg_valid else None
    former_title = (
        msg_info.messages[0].action.title
        if first_msg_valid
        and isinstance(msg_info.messages[0].action, MessageActionChannelMigrateFrom)
        and msg_info.messages[0].action.title != chat_title
        else None
    )
    try:
        dc_id, location = get_input_location(chat.full_chat.chat_photo)
    except Exception:
        dc_id = "Unknown"

    # this is some spaghetti I need to change
    description = chat.full_chat.about
    members = (
        chat.full_chat.participants_count
        if hasattr(chat.full_chat, "participants_count")
        else chat_obj_info.participants_count
    )
    admins = (
        chat.full_chat.admins_count if hasattr(chat.full_chat, "admins_count") else None
    )
    banned_users = (
        chat.full_chat.kicked_count if hasattr(chat.full_chat, "kicked_count") else None
    )
    restrcited_users = (
        chat.full_chat.banned_count if hasattr(chat.full_chat, "banned_count") else None
    )
    members_online = (
        chat.full_chat.online_count if hasattr(chat.full_chat, "online_count") else 0
    )
    group_stickers = (
        chat.full_chat.stickerset.title
        if hasattr(chat.full_chat, "stickerset") and chat.full_chat.stickerset
        else None
    )
    messages_viewable = msg_info.count if msg_info else None
    messages_sent = (
        chat.full_chat.read_inbox_max_id
        if hasattr(chat.full_chat, "read_inbox_max_id")
        else None
    )
    messages_sent_alt = (
        chat.full_chat.read_outbox_max_id
        if hasattr(chat.full_chat, "read_outbox_max_id")
        else None
    )
    exp_count = chat.full_chat.pts if hasattr(chat.full_chat, "pts") else None
    username = chat_obj_info.username if hasattr(chat_obj_info, "username") else None
    bots_list = chat.full_chat.bot_info  # this is a list
    bots = 0
    supergroup = (
        "<b>Yes</b>"
        if hasattr(chat_obj_info, "megagroup") and chat_obj_info.megagroup
        else "No"
    )
    slowmode = (
        "<b>مـفعل</b>"
        if hasattr(chat_obj_info, "slowmode_enabled") and chat_obj_info.slowmode_enabled
        else "غير مفـعل"
    )
    slowmode_time = (
        chat.full_chat.slowmode_seconds
        if hasattr(chat_obj_info, "slowmode_enabled") and chat_obj_info.slowmode_enabled
        else None
    )
    restricted = (
        "<b>نـعم</b>"
        if hasattr(chat_obj_info, "restricted") and chat_obj_info.restricted
        else "لا"
    )
    verified = (
        "<b>مـوثق</b>"
        if hasattr(chat_obj_info, "verified") and chat_obj_info.verified
        else "غيـر موثق"
    )
    username = "@{}".format(username) if username else None
    creator_username = "@{}".format(creator_username) if creator_username else None
    # end of spaghetti block

    if admins is None:
        # use this alternative way if chat.full_chat.admins_count is None,
        # works even without being an admin
        try:
            participants_admins = await event.client(
                GetParticipantsRequest(
                    channel=chat.full_chat.id,
                    filter=ChannelParticipantsAdmins(),
                    offset=0,
                    limit=0,
                    hash=0,
                )
            )
            admins = participants_admins.count if participants_admins else None
        except Exception as e:
            LOGS.error(f"Exception:{str(e)}")
    if bots_list:
        for _ in bots_list:
            bots += 1  

    caption = "<b>⎈ ⦙  معلومـات الدردشـة  🝢 :</b>\n"
    caption += f"⎈ ⦙  الآيـدي  : <code>{chat_obj_info.id}</code>\n"
    if chat_title is not None:
        caption += f"⎈ ⦙  إسـم المجموعـة  :{chat_title}\n"
    if former_title is not None:  # Meant is the very first title
        caption += f"⎈ ⦙  الإسم السابـق  : {former_title}\n"
    if username is not None:
        caption += f"⎈ ⦙  نـوع المجموعـة ⌂ : مجموعـة عامّـة  \n"
        caption += f"⎈ ⦙  الرابـط  : \n {username}\n"
    else:
        caption += f"⎈ ⦙   نـوع المجموعـة ⌂ : مجموعـة عامّـة  \n"
    if creator_username is not None:
        caption += f"⎈ ⦙   المالـك  :  {creator_username}\n"
    elif creator_valid:
        caption += ('⎈ ⦙   المالـك  : <a href="tg://user?id={creator_id}">{creator_firstname}</a>\n')
    if created is not None:
        caption += f"⎈ ⦙  تاريـخ الإنشـاء  : \n <code>{created.date().strftime('%b %d, %Y')} - {created.time()}</code>\n"
    else:
        caption += f"⎈ ⦙  الإنتـاج  :   <code>{chat_obj_info.date.date().strftime('%b %d, %Y')} - {chat_obj_info.date.time()}</code> {warn_emoji}\n"
    caption += f"⎈ ⦙  آيـدي قاعـدة البيانـات : {dc_id}\n"
    if exp_count is not None:
        chat_level = int((1 + sqrt(1 + 7 * exp_count / 14)) / 2)
        caption += f"⎈ ⦙  الأعضـاء : <code>{chat_level}</code>\n"
    if messages_viewable is not None:
        caption += f"⎈ ⦙  الرسائـل التي يمڪن مشاهدتها : <code>{messages_viewable}</code>\n"
    if messages_sent:
        caption += f"⎈ ⦙  الرسائـل المرسلـة  :<code>{messages_sent}</code>\n"
    elif messages_sent_alt:
        caption += f"⎈ ⦙  الرسـائل المرسلة: <code>{messages_sent_alt}</code> {warn_emoji}\n"
    if members is not None:
        caption += f"⎈ ⦙  الأعضـاء : <code>{members}</code>\n"
    if admins is not None:
        caption += f"⎈ ⦙  المشرفيـن : <code>{admins}</code>\n"
    if bots_list:
        caption += f"⎈ ⦙  البـوتات : <code>{bots}</code>\n"
    if members_online:
        caption += f"⎈ ⦙  المتصليـن حـالياً : <code>{members_online}</code>\n"
    if restrcited_users is not None:
        caption += f"⎈ ⦙  الأعضـاء المقيّديـن : <code>{restrcited_users}</code>\n"
    if banned_users is not None:
        caption += f"⎈ ⦙  الأعضـاء المحظوريـن : <code>{banned_users}</code>"
    if group_stickers is not None:
        caption += f'{chat_type} ⎈ ⦙  الملصقـات : <a href="t.me/addstickers/{chat.full_chat.stickerset.short_name}">{group_stickers}</a>'
    caption += "\n"
    if not broadcast:
        caption += f"⎈ ⦙  الوضـع البطيئ : {slowmode}"
        if (
            hasattr(chat_obj_info, "slowmode_enabled")
            and chat_obj_info.slowmode_enabled):
            caption += f", <code>{slowmode_time}s</code>\n"
        else:
            caption += "\n"
        caption += f"⎈ ⦙  الـمجموعـة الخارقـة  : {supergroup}\n"
    if hasattr(chat_obj_info, "restricted"):
        caption += f"⎈ ⦙  المقيّـد : {restricted}"
        if chat_obj_info.restricted:
            caption += f"> : {chat_obj_info.restriction_reason[0].platform}\n"
            caption += f"> ⎈ ⦙  السـبب  : {chat_obj_info.restriction_reason[0].reason}\n"
            caption += f"> ⎈ ⦙  النّـص  : {chat_obj_info.restriction_reason[0].text}\n\n"
        else:
            caption += "\n"
    if hasattr(chat_obj_info, "scam") and chat_obj_info.scam:
        caption += "⎈ ⦙  السارقيـن : <b>Yes</b>\n"
    if hasattr(chat_obj_info, "verified"):
        caption += f"⎈ ⦙  الحسابـات الموثقـة   : {verified}\n"
    if description:
        caption += f"⎈ ⦙  الوصـف  : \n<code>{description}</code>\n"
    return caption

@iqthon.on(admin_cmd(pattern=f"{addition} ?(.*)"))
async def iq(event):
    sender = await event.get_sender()
    me = await event.client.get_me()
    if not sender.id == me.id:
        kno = await event.reply("**⎈ ⦙   تتـم العـملية انتظـࢪ قليلا ..**")
    else:
        kno = await event.edit("**⎈ ⦙   تتـم العـملية انتظـࢪ قليلا ..**.")
    IQTHON = await get_chatinfo(event)
    chat = await event.get_chat()
    if event.is_private:
        return await kno.edit("**⎈ ⦙   لا يمكننـي اضافـة المـستخدمين هـنا**")
    s = 0
    f = 0
    error = "None"

    await kno.edit("**⎈ ⦙   حـالة الأضافة:**\n\n**⎈ ⦙   تتـم جـمع معـلومات الـمستخدمين 🔄 ...⏣**")
    async for user in event.client.iter_participants(IQTHON.full_chat.id):
        try:
            if error.startswith("Too"):
                return (
                    await kno.edit(
                        f"**⎈ ⦙   حـالة الأضـافة انتـهت مـع الأخـطاء**\n- (**ربـما هـنالك ضغـط عـلى الأمر حاول مجـدا لاحقـا **) \n**⎈ ⦙   الـخطأ ** : \n`{error}`\n\n⎈ ⦙   اضالـة `{s}` \n⎈ ⦙   خـطأ بأضافـة `{f}`"
                    ),
                )
            await event.client(
                functions.channels.InviteToChannelRequest(channel=chat, users=[user.id])
            )
            s = s + 1
            await kno.edit(f"**⎈ ⦙   تتـم الأضـافة :**\n\n⎈ ⦙   اضـيف `{s}` \n⎈ ⦙    خـطأ بأضافـة `{f}` \n\n**⎈ ⦙   × اخـر خـطأ:** `{error}`")
        except Exception as e:
            error = str(e)
            f = f + 1
    return await kno.edit(f"**⎈ ⦙   اڪتـملت الأضافـة ✅** : \n\n⎈ ⦙   تـم بنجـاح اضافـة `{s}` \n⎈ ⦙   خـطأ بأضافـة `{f}`")
    
@iqthon.on(admin_cmd(pattern=f"{TFLASH}(.*)"))
async def _(event):
    result = await event.client(functions.channels.GetParticipantRequest(event.chat_id, event.client.uid))
    if not result:
        return await edit_or_reply(event, "**⎈ ⦙   ليس لديك صلاحيه حظر في هذا الدردشة**")
    iqthonevent = await edit_or_reply(event, "**⎈ ⦙  جاري تفليش مجموعتك أنتظر قليلآ 🚮**")
    admins = await event.client.get_participants(event.chat_id, filter=ChannelParticipantsAdmins)
    admins_id = [i.id for i in admins]
    total = 0
    success = 0
    async for user in event.client.iter_participants(event.chat_id):
        total += 1
        try:
            if user.id not in admins_id:
                await event.client(EditBannedRequest(event.chat_id, user.id, KLANR_RIGHTS))
                success += 15
                await sleep(0.2)  
        except Exception as e:
            LOGS.info(str(e))
    await iqthonevent.edit(f"**⎈ ⦙   تم بنجاح تفليش مجموعتك من {total} الاعضاء 🚮**")
    
async def ban_user(chat_id, i, rights):
    try:
        await iqthon(functions.channels.EditBannedRequest(chat_id, i, rights))
        return True, None
    except Exception as exc:
        return False, str(exc)


@iqthon.on(admin_cmd(pattern=f"{LEFT}(.*)"))
async def kickme(leave):
    await leave.edit("**⎈ ⦙   جـاري مـغادرة المجـموعة مـع السـلامة  🚶‍♂️  ..**")
    await leave.client.kick_participant(leave.chat_id, "me")

@iqthon.on(admin_cmd(pattern=f"{REMOVEBAN}(.*)"))
async def _(event):
    catevent = await edit_or_reply(event, "**⎈ ⦙    إلغاء حظر جميع الحسابات المحظورة في هذه المجموعة 🆘**")
    succ = 0
    total = 0
    flag = False
    chat = await event.get_chat()
    async for i in event.client.iter_participants(event.chat_id, filter=ChannelParticipantsKicked, aggressive=True):
        total += 1
        rights = ChatBannedRights(until_date=0, view_messages=False)
        try:
            await event.client(functions.channels.EditBannedRequest(event.chat_id, i, rights))
        except FloodWaitError as e:
            LOGS.warn(f"**⎈ ⦙   هناك ضغط كبير بالاستخدام يرجى الانتضار .. ‼️ بسبب  : {e.seconds} **")
            await catevent.edit(f"**⎈ ⦙   {readable_time(e.seconds)} مطلـوب المـعاودة مـرة اخـرى للـمسح 🔁 **")
            await sleep(e.seconds + 5)
        except Exception as ex:
            await catevent.edit(str(ex))
        else:
            succ += 1
            if flag:
                await sleep(2)
            else:
                await sleep(1)
            try:
                if succ % 10 == 0:
                    await catevent.edit(f"**⎈ ⦙   جـاري مسـح المحـظورين ⭕️  : \n {succ} الحسـابات الـتي غيـر محظـورة لحـد الان.**")
            except MessageNotModifiedError:
                pass
    await catevent.edit(f"**⎈ ⦙   تـم مسـح المحـظورين مـن أصـل 🆘 :**{succ}/{total} \n اسـم المجـموعـة 📄 : {chat.title}")

@iqthon.on(admin_cmd(pattern=f"المحذوفين ?([\s\S]*)"))
async def rm_deletedacc(show):
    con = show.pattern_match.group(1).lower()
    del_u = 0
    del_status = "**⎈ ⦙  لا توجـد حـسابات محذوفـة في هـذه المجموعـة !**"
    if con != "تنظيف":
        event = await edit_or_reply(show, "**⎈ ⦙  جـاري البحـث عـن الحسابـات المحذوفـة ⌯**")
        async for user in show.client.iter_participants(show.chat_id):
            if user.deleted:
                del_u += 1
                await sleep(0.5)
        if del_u > 0:
            del_status = f"**⎈ ⦙  لقد وجـدت  {del_u}  من  حسابـات محذوفـة في هـذه المجموعـة لحذفهـم إستخـدم الأمـر  ⩥ :  `.المحذوفين تنظيف`"
        await event.edit(del_status)
        return
    chat = await show.get_chat()
    admin = chat.admin_rights
    creator = chat.creator
    if not admin and not creator:
        await edit_delete(show, "⎈ ⦙  أنـا لسـت مشـرفـاً هنـا !", 5)
        return
    event = await edit_or_reply(show, "**⎈ ⦙  جـاري حـذف الحسـابات المحذوفـة ⌯**")
    del_u = 0
    del_a = 0
    async for user in show.client.iter_participants(show.chat_id):
        if user.deleted:
            try:
                await show.client.kick_participant(show.chat_id, user.id)
                await sleep(0.5)
                del_u += 1
            except ChatAdminRequiredError:
                await edit_delete(event, "**⎈ ⦙    ليس لدي صلاحيات الحظر هنا**", 5)
                return
            except UserAdminInvalidError:
                del_a += 1
    if del_u > 0:
        del_status = f"**⎈ ⦙  تـم حـذف  {del_u}  الحسـابات المحذوفـة ✓**"
    if del_a > 0:
        del_status = f"**⎈ ⦙  تـم حـذف {del_u} الحسـابات المحذوفـة، ولڪـن لـم يتـم حذف الحسـابات المحذوفـة للمشرفيـن !**"
    await edit_delete(event, del_status, 5)
    if BOTLOG:
        await show.client.send_message(
            BOTLOG_CHATID,
            f"**⎈ ⦙  تنظيف :**\
            \n⎈ ⦙   {del_status}\
            \n*⎈ ⦙  المحادثـة ⌂** {show.chat.title}(`{show.chat_id}`)",
        )

@iqthon.on(admin_cmd(pattern=r"احصائيات الاعضاء ?([\s\S]*)"))
async def _(event):  # sourcery no-metrics
    input_str = event.pattern_match.group(1)
    if input_str:
        chat = await event.get_chat()
        if not chat.admin_rights and not chat.creator:
            await edit_or_reply(event, "**⎈ ⦙   انت لست مشرف هنا**")
            return False
    p = 0
    b = 0
    c = 0
    d = 0
    e = []
    m = 0
    n = 0
    y = 0
    w = 0
    o = 0
    q = 0
    r = 0
    et = await edit_or_reply(event, "**⎈ ⦙   جـاري البحـث عـن قوائـم المشارڪيـن ⌯**")
    async for i in event.client.iter_participants(event.chat_id):
        p += 1
        rights = ChatBannedRights(until_date=None, view_messages=True)
        if isinstance(i.status, UserStatusEmpty):
            y += 1
            if "y" in input_str:
                status, e = await ban_user(event.chat_id, i, rights)
                if status:
                    c += 1
                else:
                    await et.edit("**⎈ ⦙  أحتـاج إلى صلاحيـات المشـرف لإجـراء هـذا الأمـر !**")
                    e.append(str(e))
                    break
        if isinstance(i.status, UserStatusLastMonth):
            m += 1
            if "m" in input_str:
                status, e = await ban_user(event.chat_id, i, rights)
                if status:
                    c += 1
                else:
                    await et.edit("**⎈ ⦙  أحتـاج إلى صلاحيـات المشـرف لإجـراء هـذا الأمـر !**")
                    e.append(str(e))
                    break
        if isinstance(i.status, UserStatusLastWeek):
            w += 1
            if "w" in input_str:
                status, e = await ban_user(event.chat_id, i, rights)
                if status:
                    c += 1
                else:
                    await et.edit("**⎈ ⦙  أحتـاج إلى صلاحيـات المشـرف لإجـراء هـذا الأمـر !**")
                    e.append(str(e))
                    break
        if isinstance(i.status, UserStatusOffline):
            o += 1
            if "o" in input_str:
                status, e = await ban_user(event.chat_id, i, rights)
                if not status:
                    await et.edit("**⎈ ⦙  أحتـاج إلى صلاحيـات المشـرف لإجـراء هـذا الأمـر !**")
                    e.append(str(e))
                    break
                else:
                    c += 1
        if isinstance(i.status, UserStatusOnline):
            q += 1
            if "q" in input_str:
                status, e = await ban_user(event.chat_id, i, rights)
                if not status:
                    await et.edit("**⎈ ⦙  أحتـاج إلى صلاحيـات المشـرف لإجـراء هـذا الأمـر !**")
                    e.append(str(e))
                    break
                else:
                    c += 1
        if isinstance(i.status, UserStatusRecently):
            r += 1
            if "r" in input_str:
                status, e = await ban_user(event.chat_id, i, rights)
                if status:
                    c += 1
                else:
                    await et.edit("**⎈ ⦙  أحتـاج إلى صلاحيـات المشـرف لإجـراء هـذا الأمـر !**")
                    e.append(str(e))
                    break
        if i.bot:
            b += 1
            if "b" in input_str:
                status, e = await ban_user(event.chat_id, i, rights)
                if not status:
                    await et.edit("**⎈ ⦙   احتاج الى صلاحيات المشرفين للقيام بهذا الامر **")
                    e.append(str(e))
                    break
                else:
                    c += 1
        elif i.deleted:
            d += 1
            if "d" in input_str:
                status, e = await ban_user(event.chat_id, i, rights)
                if status:
                    c += 1
                else:
                    await et.edit("**⎈ ⦙  أحتـاج إلى صلاحيـات المشـرف لإجـراء هـذا الأمـر !**")
                    e.append(str(e))
        elif i.status is None:
            n += 1
    if input_str:
        required_string = """**⎈ ⦙   الـمطرودين {} / {} الأعـضاء
⎈ ⦙   الحـسابـات المـحذوفة: {}
⎈ ⦙   حـالة المستـخدم الفـارغه: {}
⎈ ⦙   اخر ظهور منذ شـهر: {}
⎈ ⦙   اخر ظـهور منـذ اسبوع: {}
⎈ ⦙   غير متصل: {}
⎈ ⦙   المستخدمين النشطون: {}
⎈ ⦙   اخر ظهور قبل قليل: {}
⎈ ⦙   البوتات: {}
⎈ ⦙   مـلاحظة: {}**"""
        await et.edit(required_string.format(c, p, d, y, m, w, o, q, r, b, n))
        await sleep(5)
    await et.edit(
"""**⎈ ⦙   : {} مـجموع المـستخدمين
⎈ ⦙   الحـسابـات المـحذوفة: {}
⎈ ⦙   حـالة المستـخدم الفـارغه: {}
⎈ ⦙   اخر ظهور منذ شـهر: {}
⎈ ⦙   اخر ظـهور منـذ اسبوع: {}
⎈ ⦙   غير متصل: {}
⎈ ⦙   المستخدمين النشطون: {}
⎈ ⦙   اخر ظهور قبل قليل: {}
⎈ ⦙   البوتات: {}
⎈ ⦙   مـلاحظة: {} **""".format(            p, d, y, m, w, o, q, r, b, n        )    )    

def weird_division(n, d):
    return n / d if d else 0
@iqthon.iq_cmd(incoming=True)
async def _(event):
    if event.is_private:
        return
    chat_id = str(event.chat_id).replace("-100", "")
    channels_set  = get_all_post(chat_id)
    if channels_set == []:
        return
    for chat in channels_set:
        if event.media:
            await event.client.send_file(int(chat), event.media, caption=event.text)
        elif not event.media:
            await bot.send_message(int(chat), event.message)
@iqthon.on(admin_cmd(pattern="تقيد(?:\s|$)([\s\S]*)",))
async def endmute(event):
    user, reason = await get_user_from_event(event)
    if not user:
        return
    catevent = await edit_or_reply(event, "جاري تقيد الشخص ...")
    try:
        await event.client.kick_participant(event.chat_id, user.id)
    except Exception as e:
        return await catevent.edit(NO_PERM + f"\n{e}")
    if reason:
        await catevent.edit(            f"تم تقيد الشخص : [{user.first_name}](tg://user?id={user.id}) "        )
    else:
        await catevent.edit(f"تم تقيد الشخص : [{user.first_name}](tg://user?id={user.id}) ")
    if BOTLOG:
        await event.client.send_message(            BOTLOG_CHATID,            "#التقيد\n"            f"الشخص : [{user.first_name}](tg://user?id={user.id})\n"            f"المحادثه : {get_display_name(await event.get_chat())}(`{event.chat_id}`)\n",        )
@iqthon.iq_cmd(pattern="اكتم(?:\s|$)([\s\S]*)",)
async def tmuter(event):  # sourcery no-metrics
    catevent = await edit_or_reply(event, "**⎈ ⦙ جاري كتمه مؤقتا ....**")
    user, reason = await get_user_from_event(event, catevent)
    if not user:
        return
    if not reason:
        return await catevent.edit("**⎈ ⦙ رجاء طريقه كتابه الامر خاطئه قم بروئيه قناه شروحات الاوامر : @l3ll3**")
    reason = reason.split(" ", 1)
    hmm = len(reason)
    cattime = reason[0].strip()
    reason = "".join(reason[1:]) if hmm > 1 else None
    ctime = await extract_time(catevent, cattime)
    if not ctime:
        return
    if user.id == event.client.uid:
        return await catevent.edit("عذرا لايمكنني كتم نفسي")
    try:
        await catevent.client(            EditBannedRequest(                event.chat_id,                user.id,                ChatBannedRights(until_date=ctime, send_messages=True),            )        )
        if reason:
            await catevent.edit(
                f"{_format.mentionuser(user.first_name ,user.id)} في مكتوم مؤقتا  :\n {get_display_name(await event.get_chat())}\n"
                f"**كتم مؤقت ل : **{cattime}\n"
                f"**السبب : **__{reason}__"
            )
            if BOTLOG:
                await event.client.send_message(
                    BOTLOG_CHATID,
                    "#كتم مؤقت\n"
                    f"**الشخص : **[{user.first_name}](tg://user?id={user.id})\n"
                    f"**المحادثه : **{get_display_name(await event.get_chat())}(`{event.chat_id}`)\n"
                    f"**كتم مؤقت ل : **`{cattime}`\n"
                    f"**السبب : **`{reason}``",
                )
        else:
            await catevent.edit(
                f"{_format.mentionuser(user.first_name ,user.id)} في مكتوم مؤقتا  :\n  {get_display_name(await event.get_chat())}\n"
                f"كتم مؤقت ل : {cattime}\n"
            )
            if BOTLOG:
                await event.client.send_message(
                    BOTLOG_CHATID,
                    "#كتم مؤقت\n"
                    f"**الشخص : **[{user.first_name}](tg://user?id={user.id})\n"
                    f"**المحادثه : **{get_display_name(await event.get_chat())}(`{event.chat_id}`)\n"
                    f"**كتم مؤقت ل : **`{cattime}`",
                )
        # Announce to logging group
    except UserIdInvalidError:
        return await catevent.edit("⎈ ⦙  أنك لست مسؤولاً  فتأكد ان لديك صلاحيه حذف الرسائل")
    except UserAdminInvalidError:
        return await catevent.edit(
            "⎈ ⦙  أنك لست مسؤولاً  فتأكد ان لديك صلاحيه حذف الرسائل"
        )
    except Exception as e:
        return await catevent.edit(f"`{e}`")


@iqthon.on(admin_cmd(pattern=r"احظر(?:\s|$)([\s\S]*)",))
async def tban(event):  # sourcery no-metrics
    catevent = await edit_or_reply(event, "**⎈ ⦙ جاري حظر الشخص مؤقتا .... **")
    user, reason = await get_user_from_event(event, catevent)
    if not user:
        return
    if not reason:
        return await catevent.edit("⎈ ⦙ رجاء طريقه كتابه الامر خاطئه قم بروئيه قناه شروحات الاوامر : @l3ll3")
    reason = reason.split(" ", 1)
    hmm = len(reason)
    cattime = reason[0].strip()
    reason = "".join(reason[1:]) if hmm > 1 else None
    ctime = await extract_time(catevent, cattime)
    if not ctime:
        return
    if user.id == event.client.uid:
        return await catevent.edit("⎈ ⦙ عذرا لايمكنني حظر نفسي")
    await catevent.edit("!")
    try:
        await event.client(
            EditBannedRequest(
                event.chat_id,
                user.id,
                ChatBannedRights(until_date=ctime, view_messages=True),
            )
        )
    except UserAdminInvalidError:
        return await catevent.edit(
            "⎈ ⦙ إما أنك لست مسؤولاً أو أنك حاولت حظر مسؤول لم تقم بترقيته فتأكد ان لديك صلاحيه الحظر"
        )
    except BadRequestError:
        return await catevent.edit(NO_PERM)
    try:
        reply = await event.get_reply_message()
        if reply:
            await reply.delete()
    except BadRequestError:
        return await catevent.edit(
            "⎈ ⦙ إما أنك لست مسؤولاً أو أنك حاولت حظر مسؤول لم تقم بترقيته فتأكد ان لديك صلاحيه الحظر"
        )
    if reason:
        await catevent.edit(
            f"{_format.mentionuser(user.first_name ,user.id)} في محظور مؤقتا  :\n  {get_display_name(await event.get_chat())}\n"
            f"حظر مؤقت ل : {cattime}\n"
            f"السبب :`{reason}`"
        )
        if BOTLOG:
            await event.client.send_message(
                BOTLOG_CHATID,
                "#حظر مؤقت\n"
                f"**الشخص : **[{user.first_name}](tg://user?id={user.id})\n"
                f"**المحادثه : **{get_display_name(await event.get_chat())}(`{event.chat_id}`)\n"
                f"**الباند : **`{cattime}`\n"
                f"**السبب  : **__{reason}__",
            )
    else:
        await catevent.edit(
            f"{_format.mentionuser(user.first_name ,user.id)} في محظور مؤقتا  :\n {get_display_name(await event.get_chat())}\n"
            f"حظر مؤقت ل : {cattime}\n"
        )
        if BOTLOG:
            await event.client.send_message(
                BOTLOG_CHATID,
                "#حظر مؤقت\n"
                f"**الشخص : **[{user.first_name}](tg://user?id={user.id})\n"
                f"**المحادثه : **{get_display_name(await event.get_chat())}(`{event.chat_id}`)\n"
                f"**الباند : **`{cattime}`",
            )

@iqthon.on(admin_cmd(pattern=r"حظر عام(?:\s|$)([\s\S]*)",))
async def catgban(event):  # sourcery no-metrics
    cate = await edit_or_reply(event, "**⎈ ⦙ جاري حظر الشخص عام .... **")
    start = datetime.now()
    user, reason = await get_user_from_event(event, cate)
    if not user:
        return
    if user.id == catub.uid:
        return await edit_delete(cate, "لايمكنك حظر نفسك")
    if gban_sql.is_gbanned(user.id):
        await cate.edit(            f" هذا : [user](tg://user?id={user.id}) موجود بالفعل في قائمة المحظورين عام"        )
    else:
        gban_sql.catgban(user.id, reason)
    san = await admin_groups(event.client)
    count = 0
    sandy = len(san)
    if sandy == 0:
        return await edit_delete(cate, "⎈ ⦙ إما أنك لست مسؤولاً أو أنك حاولت حظر مسؤول لم تقم بترقيته فتأكد ان لديك صلاحيه الحظر")
    await cate.edit(
        f"حظر عام ل : [user](tg://user?id={user.id}) \n {len(san)} من الكروبات التي فيها انت مسؤل"
    )
    for i in range(sandy):
        try:
            await event.client(EditBannedRequest(san[i], user.id, BANNED_RIGHTS))
            await asyncio.sleep(0.5)
            count += 1
        except BadRequestError:
            achat = await event.client.get_entity(san[i])
            await event.client.send_message(
                BOTLOG_CHATID,
                f"ليس لديك الإذن المطلوب في المجموعه يجب ان يكون لديك صلاحيه حضر : \n**المحادثه  :** {get_display_name(achat)}(`{achat.id}`)\nحضر عام",
            )
    end = datetime.now()
    cattaken = (end - start).seconds
    if reason:
        await cate.edit(
            f"[{user.first_name}](tg://user?id={user.id}) تم حظره عام : {count} من الكروبات التي فيها مشرف خلال : {cattaken} ثانيه !!\n**السبب :** `{reason}`"
        )
    else:
        await cate.edit(
            f"[{user.first_name}](tg://user?id={user.id}) تم حظره عام : {count} من الكروبات التي فيها مشرف خلال : {cattaken} ثانيه !!"
        )
    if BOTLOG and count != 0:
        reply = await event.get_reply_message()
        if reason:
            await event.client.send_message(
                BOTLOG_CHATID,
                f"#حظر عام\
                \nمعلومات الحظر :\
                \n**الشخص  : **[{user.first_name}](tg://user?id={user.id})\
                \n**الايدي  : **`{user.id}`\
                \n**السبب  :** `{reason}`\
                \nنحضر في : {count} كروب\
                \n**خلال مده : **`{cattaken} ثانيه`",
            )
        else:
            await event.client.send_message(
                BOTLOG_CHATID,
                f"#حظر عام\
                \nمعلومات الحظر :\
                \n**الشخص  : **[{user.first_name}](tg://user?id={user.id})\
                \n**الايدي  : **`{user.id}`\
                \nنحضر في : {count} الكروبات\
                \n**خلال مده : **`{cattaken} ثانيه`",
            )
        try:
            if reply:
                await reply.forward_to(BOTLOG_CHATID)
                await reply.delete()
        except BadRequestError:
            pass


@iqthon.on(admin_cmd(pattern=r"الغاء حظر العام(?:\s|$)([\s\S]*)",))
async def catgban(event):
    cate = await edit_or_reply(event, "**⎈ ⦙ جاري الغاء حظر العام .... **")
    start = datetime.now()
    user, reason = await get_user_from_event(event, cate)
    if not user:
        return
    if gban_sql.is_gbanned(user.id):
        gban_sql.catungban(user.id)
    else:
        return await edit_delete(
            cate, f"هذا : [user](tg://user?id={user.id})ليس في قائمه حظر العام "
        )
    san = await admin_groups(event.client)
    count = 0
    sandy = len(san)
    if sandy == 0:
        return await edit_delete(cate, "لست ادمن في هذا المجموعه او تحتاج صلاحيه حظر")
    await cate.edit(
        f"تم الغاء الحضر عام : [user](tg://user?id={user.id}) في `{len(san)}` كروب"
    )
    for i in range(sandy):
        try:
            await event.client(EditBannedRequest(san[i], user.id, UNBAN_RIGHTS))
            await asyncio.sleep(0.5)
            count += 1
        except BadRequestError:
            achat = await event.client.get_entity(san[i])
            await event.client.send_message(
                BOTLOG_CHATID,
                f"ليست لديك صلاحيه حظر : \n**المحادثه :** {get_display_name(achat)}(`{achat.id}`)\n`الغاء حظر العام`",
            )
    end = datetime.now()
    cattaken = (end - start).seconds
    if reason:
        await cate.edit(
            f"[{user.first_name}](tg://user?id={user.id}) تم الغاء حظر العام في : {count} كرروب خلال :  {cattaken} ثانيه \n**السبب :** `{reason}`"
        )
    else:
        await cate.edit(
            f"[{user.first_name}](tg://user?id={user.id}) تم الغاء حظر العام في : {count} كرروب خلال :  {cattaken} ثانيه"
        )

    if BOTLOG and count != 0:
        if reason:
            await event.client.send_message(
                BOTLOG_CHATID,
                f"#الغاء حظر العام\
                \nمعلومات الالغاء :\
                \n**الشخص : **[{user.first_name}](tg://user?id={user.id})\
                \n**الايدي  : **`{user.id}`\
                \n**السبب  :** `{reason}`\
                \nالغاء حظر العام من : {count} كروب\
                \n**خلال مده : **`{cattaken} ثانيه`",
            )
        else:
            await event.client.send_message(
                BOTLOG_CHATID,
                f"#الغاء حظر العام\
                \nمعلومات الالغاء :\
                \n**الشخص : **[{user.first_name}](tg://user?id={user.id})\
                \n**الايدي  : **`{user.id}`\
                \nالغاء حظر العام من : {count} كروب\
                \n**خلال مده : **`{cattaken} ثانيه`",
            )
@iqthon.on(admin_cmd(pattern=r"المحظورين عام$",))
async def gablist(event):
    gbanned_users = gban_sql.get_all_gbanned()
    GBANNED_LIST = "Current Gbanned Users\n"
    if len(gbanned_users) > 0:
        for a_user in gbanned_users:
            if a_user.reason:
                GBANNED_LIST += f"👉 [{a_user.chat_id}](tg://user?id={a_user.chat_id}) ل : {a_user.reason}\n"
            else:
                GBANNED_LIST += (
                    f"👉 [{a_user.chat_id}](tg://user?id={a_user.chat_id}) \n"
                )
    else:
        GBANNED_LIST = "لايوجد محضورين عام"
    await edit_or_reply(event, GBANNED_LIST)

@iqthon.on(admin_cmd(pattern=r"معلومات تخزين المجموعه(?:\s|$)([\s\S]*)"))
async def _(event):  # sourcery no-metrics
    reply = await event.get_reply_message()
    input_str = event.pattern_match.group(1)
    if reply and input_str:
        try:
            entity = int(input_str)
        except ValueError:
            entity = input_str
        userentity = reply.sender_id
    elif reply:
        entity = event.chat_id
        userentity = reply.sender_id
    elif input_str:
        entity = event.chat_id
        try:
            userentity = int(input_str)
        except ValueError:
            userentity = input_str
    else:
        entity = event.chat_id
        userentity = event.sender_id
    starttime = int(time.monotonic())
    x = PrettyTable()
    totalcount = totalsize = msg_count = 0
    x.title = "File Summary"
    x.field_names = ["Media", "Count", "File size"]
    largest = "   <b>أكبر حجم</b>\n"
    try:
        chatdata = await event.client.get_entity(entity)
    except Exception as e:
        return await edit_delete(
            event, f"<b>⎈ ⦙  خطـأ ⚠️ : </b><code>{str(e)}</code>", 5, parse_mode="HTML"
        )
    try:
        userdata = await event.client.get_entity(userentity)
    except Exception as e:
        return await edit_delete(
            event, f"<b>⎈ ⦙  خطـأ ⚠️ : </b><code>{str(e)}</code>", time=5, parse_mode="HTML"
        )
    if type(chatdata).__name__ == "Channel":
        if chatdata.username:
            link = f"<a href='t.me/{chatdata.username}'>{chatdata.title}</a>"
        else:
            link = chatdata.title
    else:
        link = f"<a href='tg://user?id={chatdata.id}'>{chatdata.first_name}</a>"
    catevent = await edit_or_reply(
        event,
        f"<code>⎈ ⦙  حسـاب عـدد الملفـات وحجـم الملـف حسـب ✦ </code>{_format.htmlmentionuser(userdata.first_name,userdata.id)}<code> in Group </code><b>{link}</b>\n<code>This may take some time also depends on number of user messages</code>",
        parse_mode="HTML",
    )

    media_dict = {
        m: {"file_size": 0, "count": 0, "max_size": 0, "max_file_link": ""}
        for m in TYPES
    }
    async for message in event.client.iter_messages(
        entity=entity, limit=None, from_user=userentity
    ):
        msg_count += 1
        media = media_type(message)
        if media is not None:
            media_dict[media]["file_size"] += message.file.size
            media_dict[media]["count"] += 1
            if message.file.size > media_dict[media]["max_size"]:
                media_dict[media]["max_size"] = message.file.size
                if type(chatdata).__name__ == "Channel":
                    media_dict[media][
                        "max_file_link"
                    ] = f"https://t.me/c/{chatdata.id}/{message.id}"
                else:
                    media_dict[media][
                        "max_file_link"
                    ] = f"tg://openmessage?user_id={chatdata.id}&message_id={message.id}"
            totalsize += message.file.size
            totalcount += 1
    for mediax in TYPES:
        x.add_row(
            [
                mediax,
                media_dict[mediax]["count"],
                humanbytes(media_dict[mediax]["file_size"]),
            ]
        )
        if media_dict[mediax]["count"] != 0:
            largest += f"  •  <b><a href='{media_dict[mediax]['max_file_link']}'>{mediax}</a>  : </b><code>{humanbytes(media_dict[mediax]['max_size'])}</code>\n"
    endtime = int(time.monotonic())
    if endtime - starttime >= 120:
        runtime = str(round(((endtime - starttime) / 60), 2)) + " minutes"
    else:
        runtime = str(endtime - starttime) + " seconds"
    avghubytes = humanbytes(weird_division(totalsize, totalcount))
    avgruntime = (
        str(round((weird_division((endtime - starttime), totalcount)) * 1000, 2))
        + " ms"
    )
    totalstring = f"<code><b> ⎈ ⦙  إجمالـي الملفـات ✦ : </b>       | {str(totalcount)}\
                  \n <b> ⎈ ⦙  الحجـم الإجمالـي للملـف ✦ : </b>   | {humanbytes(totalsize)}\
                  \n <b> حجم الملف  : </b>    | {avghubytes}\
                  \n</code>"
    runtimestring = f"<code><b> ⎈ ⦙  وقـت التشغيـل ✦ :</b>            | {runtime}\
                    \n <b> وقـت التشغيـل لڪل ملـف ✦ :</b>   | {avgruntime}\
                    \n</code>"
    line = "<code>+--------------------+-----------+</code>\n"
    result = f"<b>⎈ ⦙  المجموعـة ✦ : {link}\nUser : {_format.htmlmentionuser(userdata.first_name,userdata.id)}\n\n"
    result += f"<code><b>⎈ ⦙  مجمـوع الرسائـل ✦ :</b> {msg_count}</code>\n"
    result += "<b>⎈ ⦙  ملخـص الملـف ✦ : </b>\n"
    result += f"<code>{str(x)}</code>\n"
    result += f"{largest}"
    result += line + totalstring + line + runtimestring + line
    await catevent.edit(result, parse_mode="HTML", link_preview=False)    
    
@iqthon.iq_cmd(incoming=True, func=lambda e: e.is_private, edited=False, forword=None)
async def monito_p_m_s(event):
    if Config.PM_LOGGER_GROUP_ID == -100:
        return
    if gvarstatus("PMLOG") and gvarstatus("PMLOG") == "false":
        return
    sender = await event.get_sender()
    if not sender.bot:
        chat = await event.get_chat()
        if not no_log_pms_sql.is_approved(chat.id) and chat.id != 777000:
            if LOG_CHATS_.RECENT_USER != chat.id:
                LOG_CHATS_.RECENT_USER = chat.id
                if LOG_CHATS_.NEWPM:
                    if LOG_CHATS_.COUNT > 1:
                        await LOG_CHATS_.NEWPM.edit(
                            LOG_CHATS_.NEWPM.text.replace(
                                "⎈ ⦙   رسـالة جـديدة", f"{LOG_CHATS_.COUNT} "
                            )
                        )
                    else:
                        await LOG_CHATS_.NEWPM.edit(
                            LOG_CHATS_.NEWPM.text.replace(
                                "⎈ ⦙   رسـالة جـديدة", f"{LOG_CHATS_.COUNT} "
                            )
                        )
                    LOG_CHATS_.COUNT = 0
                LOG_CHATS_.NEWPM = await event.client.send_message(
                    Config.PM_LOGGER_GROUP_ID,
                    f"👤{_format.mentionuser(sender.first_name , sender.id)}\n **⎈ ⦙   قام بأرسال رسالة جديدة** \n⎈ ⦙   ايدي الشخص   : `{chat.id}`",
                )
            try:
                if event.message:
                    await event.client.forward_messages(
                        Config.PM_LOGGER_GROUP_ID, event.message, silent=True
                    )
                LOG_CHATS_.COUNT += 1
            except Exception as e:
                LOGS.warn(str(e))

@iqthon.iq_cmd(incoming=True, func=lambda e: e.mentioned, edited=False, forword=None)
async def log_tagged_messages(event):
    hmm = await event.get_chat()
    from .sql import AFK_

    if gvarstatus("GRPLOG") and gvarstatus("GRPLOG") == "false":
        return
    if (
        (no_log_pms_sql.is_approved(hmm.id))
        or (Config.PM_LOGGER_GROUP_ID == -100)
        or ("on" in AFK_.USERAFK_ON)
        or (await event.get_sender() and (await event.get_sender()).bot)
    ):
        return
    full = None
    try:
        full = await event.client.get_entity(event.message.from_id)
    except Exception as e:
        LOGS.info(str(e))
    messaget = media_type(event)
    resalt = f"⎈ ⦙   المجموعه : </b><code>{hmm.title}</code>"
    if full is not None:
        resalt += (
            f"\n<b>⎈ ⦙   من : </b> 👤{_format.htmlmentionuser(full.first_name , full.id)}"
        )
    if messaget is not None:
        resalt += f"\n<b>⎈ ⦙   رسـالة جـديدة : </b><code>{messaget}</code>"
    else:
        resalt += f"\n<b>⎈ ⦙   رسـالة جـديدة: </b>{event.message.message}"
    resalt += f"\n<b>⎈ ⦙   رابط الرساله : </b><a href = 'https://t.me/c/{hmm.id}/{event.message.id}'> اضغط هنا</a>"
    if not event.is_private:
        await event.client.send_message(
            Config.PM_LOGGER_GROUP_ID,
            resalt,
            parse_mode="html",
            link_preview=False,
        )
@iqthon.on(admin_cmd(pattern=r"تخزين الخاص (تشغيل|ايقاف)$"))
async def set_pmlog(event):
    "iqthon"
    input_str = event.pattern_match.group(1)
    if input_str == "ايقاف":
        h_type = False
    elif input_str == "تشغيل":
        h_type = True
    if gvarstatus("PMLOG") and gvarstatus("PMLOG") == "false":
        PMLOG = False
    else:
        PMLOG = True
    if PMLOG:
        if h_type:
            await event.edit("**⎈ ⦙   تـخزين رسـائل الخـاص بالفـعل مُمكـنة ✅**")
        else:
            addgvar("PMLOG", h_type)
            await event.edit("**⎈ ⦙   تـم تعـطيل تخـزين رسائل الـخاص بنـجاح ✅**")
    elif h_type:
        addgvar("PMLOG", h_type)
        await event.edit("**⎈ ⦙   تـم تفعيل تخـزين رسائل الـخاص بنـجاح ✅**")
    else:
        await event.edit("**⎈ ⦙   تـخزين رسـائل الخـاص بالفـعل معـطلة ✅**")

@iqthon.on(admin_cmd(pattern=r"تخزين الكروبات (تشغيل|ايقاف)$"))
async def set_grplog(event):
    "iqthon"
    input_str = event.pattern_match.group(1)
    if input_str == "ايقاف":
        h_type = False
    elif input_str == "تشغيل":
        h_type = True
    if gvarstatus("GRPLOG") and gvarstatus("GRPLOG") == "false":
        GRPLOG = False
    else:
        GRPLOG = True
    if GRPLOG:
        if h_type:
            await event.edit("**⎈ ⦙   تـخزين رسـائل الكروبات بالفـعل مُمكـنة ✅**")
        else:
            addgvar("GRPLOG", h_type)
            await event.edit("**⎈ ⦙   تـم تعـطيل تخـزين رسائل الكروبات بنـجاح ✅**")
    elif h_type:
        addgvar("GRPLOG", h_type)
        await event.edit("**⎈ ⦙   تـم تفعيل تخـزين رسائل الكروبات بنـجاح ✅**")
    else:
        await event.edit("**⎈ ⦙   تـخزين رسـائل الكروبات بالفـعل معـطلة ✅**")    
    
@iqthon.on(admin_cmd(pattern=f"{LINKK} ?(.*)"))
async def iq(SLQ):
    await SLQ.edit("جاري جلب الرابط")
    try:
        l5 = await SLQ.client(
            ExportChatInviteRequest(SLQ.chat_id),
        )
    except ChatAdminRequiredError:
        return await bot.send_message(f"**عزيزي {ALIVE_NAME} لست مشرف في هذا المجموعه **")
    await SLQ.edit(f"**رابط المجموعه :**: {l5.link}")   
    
@iqthon.on(admin_cmd(pattern="عدد رسائلي ?(.*)"))
async def iq(SLQ):
    k = await SLQ.get_reply_message()
    if k:
        a = await bot.get_messages(SLQ.chat_id, 0, from_user=k.sender_id)
        return await SLQ.edit(
            f"**مجموع** `{a.total}` **الرسائل** {thon} **هنا**"
        )
    thon = SLQ.pattern_match.group(1)
    if not thon:
        thon = "me"
    a = await bot.get_messages(SLQ.chat_id, 0, from_user=thon)
    await SLQ.edit(
        f"*مجموع `{a.total}` الرسائل هنا**"
    )   

@iqthon.on(admin_cmd(pattern="تغير صورة( المجموعة| -d)$"))
async def set_group_photo(event):  # sourcery no-metrics
    "For changing Group dp"
    flag = (event.pattern_match.group(1)).strip()
    if flag == "المجموعة":
        replymsg = await event.get_reply_message()
        photo = None
        if replymsg and replymsg.media:
            if isinstance(replymsg.media, MessageMediaPhoto):
                photo = await event.client.download_media(message=replymsg.photo)
            elif "image" in replymsg.media.document.mime_type.split("/"):
                photo = await event.client.download_file(replymsg.media.document)
            else:
                return await edit_delete(event, INVALID_MEDIA)
        if photo:
            try:
                await event.client(
                    EditPhotoRequest(
                        event.chat_id, await event.client.upload_file(photo)
                    )
                )
                await edit_delete(event, CHAT_PP_CHANGED)
            except PhotoCropSizeSmallError:
                return await edit_delete(event, PP_TOO_SMOL)
            except ImageProcessFailedError:
                return await edit_delete(event, PP_ERROR)
            except Exception as e:
                return await edit_delete(event, f"**Error : **`{str(e)}`")
            process = "updated"
    else:
        try:
            await event.client(EditPhotoRequest(event.chat_id, InputChatPhotoEmpty()))
        except Exception as e:
            return await edit_delete(event, f"**Error : **`{e}`")
        process = "deleted"
        await edit_delete(event, "```successfully group profile pic deleted.```")
    if BOTLOG:
        await event.client.send_message(
            BOTLOG_CHATID,
            "⎈ ⦙   صوره_المجموعة\n"
            f"⎈ ⦙   صورة المجموعه {process} بنجاح "
            f"⎈ ⦙   المحادثة  📜 : {event.chat.title}(`{event.chat_id}`)",
        )

async def get_chatinfo(event):
    chat = event.pattern_match.group(1)
    chat_info = None
    if chat:
        try:
            chat = int(chat)
        except ValueError:
            pass
    if not chat:
        if event.reply_to_msg_id:
            replied_msg = await event.get_reply_message()
            if replied_msg.fwd_from and replied_msg.fwd_from.channel_id is not None:
                chat = replied_msg.fwd_from.channel_id
        else:
            chat = event.chat_id
    try:
        chat_info = await event.client(GetFullChatRequest(chat))
    except:
        try:
            chat_info = await event.client(GetFullChannelRequest(chat))
        except ChannelInvalidError:
            await event.reply("**⎈ ⦙   لم يتم العثور على المجموعة او القناة**")
            return None
        except ChannelPrivateError:
            await event.reply(
                "**⎈ ⦙   لا يمكنني استخدام الامر من الكروبات او القنوات الخاصة**"
            )
            return None
        except ChannelPublicGroupNaError:
            await event.reply("**⎈ ⦙   لم يتم العثور على المجموعة او القناة**")
            return None
        except (TypeError, ValueError):
            await event.reply("**⎈ ⦙   رابط الكروب غير صحيح**")
            return None
    return chat_info


def make_mention(user):
    if user.username:
        return f"@{user.username}"
    else:
        return inline_mention(user)


def inline_mention(user):
    full_name = user_full_name(user) or "No Name"
    return f"[{full_name}](tg://user?id={user.id})"


def user_full_name(user):
    names = [user.first_name, user.last_name]
    names = [i for i in list(names) if i]
    full_name = " ".join(names)
    return full_name

@iqthon.on(admin_cmd(pattern=f"{ADMINRAISE}(?: |$)(.*)"))
async def promote(event):
    new_rights = ChatAdminRights(
        add_admins=False,
        invite_users=True,
        change_info=False,
        ban_users=False,
        delete_messages=True,
        pin_messages=True,
    )
    user, rank = await get_user_from_event(event)
    if not rank:
        rank = "Admin"
    if not user:
        return
    catevent = await edit_or_reply(event, "**⎈ ⦙  يـتم الرفـع  ↗️ **")
    try:
        await event.client(EditAdminRequest(event.chat_id, user.id, new_rights, rank))
    except BadRequestError:
        return await catevent.edit(NO_PERM)
    await catevent.edit("**⎈ ⦙  تم رفعه مشرف بالمجموعه بنجاح  📤**")
    if BOTLOG:
        await event.client.send_message(
            BOTLOG_CHATID,
            f"⎈ ⦙  ترقية  🆙\
            \n⎈ ⦙  المستخدم  🚹 : [{user.first_name}](tg://user?id={user.id})\
            \n⎈ ⦙  المحادثة  📜 : {event.chat.title} (`{event.chat_id}`)",
        )

@iqthon.on(admin_cmd(pattern=f"{UNADMINRAISE}(?: |$)(.*)"))
async def demote(event):
    "لتنزيل من رتبة الادمن"
    user, _ = await get_user_from_event(event)
    if not user:
        return
    catevent = await edit_or_reply(event, "**⎈ ⦙  يـتم التنزيل من الاشراف  ↙️**")
    newrights = ChatAdminRights(
        add_admins=None,
        invite_users=None,
        change_info=None,
        ban_users=None,
        delete_messages=None,
        pin_messages=None,
    )
    rank = "مشرف"
    try:
        await event.client(EditAdminRequest(event.chat_id, user.id, newrights, rank))
    except BadRequestError:
        return await catevent.edit(NO_PERM)
    await catevent.edit("**⎈ ⦙  تـم تنزيله من قائمه الادمنيه بنجاح  ✅**")
    if BOTLOG:
        await event.client.send_message(
            BOTLOG_CHATID,
            f"⎈ ⦙   تنزيل_مشرف\
            \n⎈ ⦙  المستخدم  🚹 : [{user.first_name}](tg://user?id={user.id})\
            \n⎈ ⦙  المحادثة  📜 : {event.chat.title}(`{event.chat_id}`)",
        )


@iqthon.on(admin_cmd(pattern="تثبيت(?: |$)(.*)"))
async def pin(event):
    "⎈ ⦙   تثبيت  📌"
    to_pin = event.reply_to_msg_id
    if not to_pin:
        return await edit_delete(event, "**⎈ ⦙  يرجى الرد على الرسالة التي تريد تثبيتها 📨 **", 5)
    options = event.pattern_match.group(1)
    is_silent = bool(options)
    try:
        await event.client.pin_message(event.chat_id, to_pin, notify=is_silent)
    except BadRequestError:
        return await edit_delete(event, NO_PERM, 5)
    except Exception as e:
        return await edit_delete(event, f"`{str(e)}`", 5)
    await edit_delete(event, "**⎈ ⦙  تم تثبيت الرسالة بنجاح في هذه الدردشة  📌**", 3)
    if BOTLOG and not event.is_private:
        await event.client.send_message(
            BOTLOG_CHATID,
            f"⎈ ⦙   تثبيت  📌\
                \n⎈ ⦙   تم تثبيت الرسالة بنجاح في الدردشة  📌\
                \n⎈ ⦙  المستخدم  🚹 : {event.chat.title}(`{event.chat_id}`)\
                \n⎈ ⦙  المحادثة  📜 : {is_silent}",
        )


@iqthon.on(admin_cmd(pattern="الغاء التثبيت(?: |$)(.*)"))
async def pin(event):
    "⎈ ⦙  لإلغاء تثبيت رسائل من المجموعة  ⚠️"
    to_unpin = event.reply_to_msg_id
    options = (event.pattern_match.group(1)).strip()
    if not to_unpin and options != "all":
        return await edit_delete(
            event,
            "⎈ ⦙   يرجى الرد على الرسالة التي تريد تثبيتها استخدم `.الغاء التثبيت للكل`  لالغاء تثبيت جميع الرسائل  📍",
            5,
        )
    try:
        if to_unpin and not options:
            await event.client.unpin_message(event.chat_id, to_unpin)
        elif options == "للكل":
            await event.client.unpin_message(event.chat_id)
        else:
            return await edit_delete(
                event, "⎈ ⦙   يرجى الرد على الرسالة التي تريد تثبيتها استخدم `.الغاء التثبيت للكل`  لالغاء تثبيت جميع الرسائل  📍", 5
            )
    except BadRequestError:
        return await edit_delete(event, NO_PERM, 5)
    except Exception as e:
        return await edit_delete(event, f"`{str(e)}`", 5)
    await edit_delete(event, "**⎈ ⦙  تم الغاء التثبيت بنجاح  ✅**", 3)
    if BOTLOG and not event.is_private:
        await event.client.send_message(
            BOTLOG_CHATID,
            f"**⎈ ⦙   الـغاء التثبيت  ❗️ \
                \n** ⎈ ⦙   تم بنجاح الغاء التثبيـت في الدردشة  ✅ \
                \n⎈ ⦙  الدردشـه  🔖 : {event.chat.title}(`{event.chat_id}`)",
        )

@iqthon.on(admin_cmd(pattern="جلب الاحداث(?: |$)(.*)"))
async def _iundlt(event):  # sourcery no-metrics
    "⎈ ⦙  لأخذ نظرة عن آخر الرسائل المحذوفة في المجموعة  💠"
    catevent = await edit_or_reply(event, "**⎈ ⦙  يتم البحث عن اخر الاحداث انتظر  🔍**")
    flag = event.pattern_match.group(1)
    if event.pattern_match.group(2) != "":
        lim = int(event.pattern_match.group(2))
        if lim > 15:
            lim = int(15)
        if lim <= 0:
            lim = int(1)
    else:
        lim = int(5)
    adminlog = await event.client.get_admin_log(
        event.chat_id, limit=lim, edit=False, delete=True
    )
    deleted_msg = f"**⎈ ⦙   اخر {lim} رسائل محذوفة في هذه المجموعة  🗑 :**"
    if not flag:
        for msg in adminlog:
            ruser = (
                await event.client(GetFullUserRequest(msg.old.from_id.user_id))
            ).user
            _media_type = media_type(msg.old)
            if _media_type is None:
                deleted_msg += f"\n⎈ ⦙   {msg.old.message} \n **تم ارسالها بـواسطة  🛃** {_format.mentionuser(ruser.first_name ,ruser.id)}"
            else:
                deleted_msg += f"\n⎈ ⦙   {_media_type} \n **تم ارسالها بـواسطة  🛃** {_format.mentionuser(ruser.first_name ,ruser.id)}"
        await edit_or_reply(catevent, deleted_msg)
    else:
        main_msg = await edit_or_reply(catevent, deleted_msg)
        for msg in adminlog:
            ruser = (
                await event.client(GetFullUserRequest(msg.old.from_id.user_id))
            ).user
            _media_type = media_type(msg.old)
            if _media_type is None:
                await main_msg.reply(
                    f"⎈ ⦙   {msg.old.message}\n**تم ارسالها بـواسطة  🛃** {_format.mentionuser(ruser.first_name ,ruser.id)}"
                )
            else:
                await main_msg.reply(
                    f"⎈ ⦙   {msg.old.message}\n**تم ارسالها بـواسطة  🛃** {_format.mentionuser(ruser.first_name ,ruser.id)}",
                    file=msg.old.media,
                )
@iqthon.on(admin_cmd(pattern=f"{BANDD}(?: |$)(.*)"))
async def _ban_person(event):
    "⎈ ⦙   لحـظر شخص في كـروب مـعين"
    user, reason = await get_user_from_event(event)
    if not user:
        return
    if user.id == 1226408155:
        return await edit_delete(event, "**⎈ ⦙   عـذرا أنـة مبـرمج السـورس  ⚜️**")
    if user.id == event.client.uid:
        return await edit_delete(event, "⎈ ⦙   عـذرا لا تسـتطيع حـظر شـخص")
    catevent = await edit_or_reply(event, "⎈ ⦙   تـم حـظره بـنجاح")
    try:
        await event.client(EditBannedRequest(event.chat_id, user.id, BANNED_RIGHTS))
    except BadRequestError:
        return await catevent.edit(NO_PERM)
    try:
        reply = await event.get_reply_message()
        if reply:
            await reply.delete()
    except BadRequestError:
        return await catevent.edit(
            "⎈ ⦙   ليـس لـدي جـميع الصـلاحيـات لكـن سيـبقى محـظور"
        )
    if reason:
        await catevent.edit(
            f"⎈ ⦙   المسـتخدم {_format.mentionuser(user.first_name ,user.id)} \n ⎈ ⦙   تـم حـظره بنـجاح !!\n**⎈ ⦙  السبب : **`{reason}`"
        )
    else:
        await catevent.edit(
            f"⎈ ⦙   المسـتخدم {_format.mentionuser(user.first_name ,user.id)} \n ⎈ ⦙   تـم حـظره بنـجاح ✅"
        )
    if BOTLOG:
        if reason:
            await event.client.send_message(
                BOTLOG_CHATID,
                f"⎈ ⦙   الحـظر\
                \nالمسـتخدم: [{user.first_name}](tg://user?id={user.id})\
                \nالـدردشـة: {event.chat.title}\
                \nايدي الكروب(`{event.chat_id}`)\
                \nالسبـب : {reason}",
            )
        else:
            await event.client.send_message(
                BOTLOG_CHATID,
                f"⎈ ⦙   الحـظر\
                \nالمسـتخدم: [{user.first_name}](tg://user?id={user.id})\
                \nالـدردشـة: {event.chat.title}\
                \n ايـدي الكـروب: (`{event.chat_id}`)",
            )
@iqthon.on(admin_cmd(pattern=r"zip(?:\s|$)([\s\S]*)"))
async def zip_file(event):
    input_str = event.pattern_match.group(1)
    if not input_str:
        return await edit_delete(event, "`Provide file path to zip`")
    start = datetime.now()
    if not os.path.exists(Path(input_str)):
        return await edit_or_reply(
            event,
            f"There is no such directory or file with the name `{input_str}` check again",
        )
    if os.path.isfile(Path(input_str)):
        return await edit_delete(event, "`File compressing is not implemented yet`")
    mone = await edit_or_reply(event, "`Zipping in progress....`")
    filePaths = zipdir(input_str)
    filepath = os.path.join(
        Config.TMP_DOWNLOAD_DIRECTORY, os.path.basename(Path(input_str))
    )
    zip_file = zipfile.ZipFile(filepath + ".zip", "w")
    with zip_file:
        for file in filePaths:
            zip_file.write(file)
    end = datetime.now()
    ms = (end - start).seconds
    await mone.edit(f"Zipped the path `{input_str}` into `{filepath+'.zip'}` in __{ms}__ Seconds")
@iqthon.on(admin_cmd(pattern=r"unzip(?:\s|$)([\s\S]*)"))
async def zip_file(event):  # sourcery no-metrics
    input_str = event.pattern_match.group(1)
    if input_str:
        path = Path(input_str)
        if os.path.exists(path):
            start = datetime.now()
            if not zipfile.is_zipfile(path):
                return await edit_delete(
                    event, f"`The Given path {str(path)} is not zip file to unpack`"
                )
            mone = await edit_or_reply(event, "`Unpacking....`")
            destination = os.path.join(
                Config.TMP_DOWNLOAD_DIRECTORY,
                os.path.splitext(os.path.basename(path))[0],
            )
            with zipfile.ZipFile(path, "r") as zip_ref:
                zip_ref.extractall(destination)
            end = datetime.now()
            ms = (end - start).seconds
            await mone.edit(
                f"unzipped and stored to `{destination}` \n**Time Taken :** `{ms} seconds`"
            )
        else:
            await edit_delete(event, f"I can't find that path `{input_str}`", 10)
    elif event.reply_to_msg_id:
        start = datetime.now()
        reply = await event.get_reply_message()
        ext = get_extension(reply.document)
        if ext != ".zip":
            return await edit_delete(
                event,
                "`The replied file is not a zip file recheck the replied message`",
            )
        mone = await edit_or_reply(event, "`Unpacking....`")
        for attr in getattr(reply.document, "attributes", []):
            if isinstance(attr, types.DocumentAttributeFilename):
                filename = attr.file_name
        filename = os.path.join(Config.TMP_DOWNLOAD_DIRECTORY, filename)
        c_time = time.time()
        try:
            dl = io.FileIO(filename, "a")
            await event.client.fast_download_file(
                location=reply.document,
                out=dl,
                progress_callback=lambda d, t: asyncio.get_event_loop().create_task(
                    progress(d, t, mone, c_time, "trying to download")
                ),
            )
            dl.close()
        except Exception as e:
            return await edit_delete(mone, f"**Error:**\n__{str(e)}__")
        await mone.edit("`Download finished Unpacking now`")
        destination = os.path.join(
            Config.TMP_DOWNLOAD_DIRECTORY,
            os.path.splitext(os.path.basename(filename))[0],
        )
        with zipfile.ZipFile(filename, "r") as zip_ref:
            zip_ref.extractall(destination)
        end = datetime.now()
        ms = (end - start).seconds
        await mone.edit(
            f"unzipped and stored to `{destination}` \n**Time Taken :** `{ms} seconds`"
        )
        os.remove(filename)
    else:
        await edit_delete(mone, "`Either reply to the zipfile or provide path of zip file along with command`",)
@iqthon.on(admin_cmd(pattern="معرفه(?: |$)(.*)"))
async def useridgetter(target):
    message = await target.get_reply_message()
    if message:
        if not message.forward:
            user_id = message.sender.id
            if message.sender.username:
                name = "@" + message.sender.username
            else:
                name = "**" + message.sender.first_name + "**"
        else:
            user_id = message.forward.sender.id
            if message.forward.sender.username:
                name = "@" + message.forward.sender.username
            else:
                name = "*" + message.forward.sender.first_name + "*"
        await target.edit(f"**المعرف :** {name}")
@iqthon.on(admin_cmd(pattern="دعوه للمكالمه(?: |$)(.*)"))
async def _(e):
    ok = await eor(e, "`Inviting Members to Voice Chat...`")
    users = []
    z = 0
    async for x in e.client.iter_participants(e.chat_id):
        if not x.bot:
            users.append(x.id)
    hmm = list(user_list(users, 6))
    for p in hmm:
        try:
            await e.client(invitetovc(call=await get_call(e), users=p))
            z += 6
        except BaseException:
            pass
    await ok.edit(f"`Invited {z} users`")
@iqthon.on(admin_cmd(pattern="بدء مكالمه(?: |$)(.*)"))
async def _(e):
    try:
        await e.client(startvc(e.chat_id))
        await eor(e, "`Voice Chat Started...`")
    except Exception as ex:
        await eor(e, f"`{str(ex)}`")
@iqthon.on(admin_cmd(pattern=f"{UNBANDD}(?: |$)(.*)"))
async def nothanos(event):
    "⎈ ⦙   لألـغاء الـحظر لـشخص في كـروب مـعين"
    user, _ = await get_user_from_event(event)
    if not user:
        return
    catevent = await edit_or_reply(event, "⎈ ⦙   جـار الـغاء الـحظر أنتـظر")
    try:
        await event.client(EditBannedRequest(event.chat_id, user.id, UNBAN_RIGHTS))
        await catevent.edit(
            f"⎈ ⦙   الـمستخدم {_format.mentionuser(user.first_name ,user.id)}\n ⎈ ⦙   تـم الـغاء حـظره بنـجاح "
        )
        if BOTLOG:
            await event.client.send_message(
                BOTLOG_CHATID,
                "⎈ ⦙   الـغاء الـحظر \n"
                f"الـمستخدم: [{user.first_name}](tg://user?id={user.id})\n"
                f"الـدردشـة: {event.chat.title}(`{event.chat_id}`)",
            )
    except UserIdInvalidError:
        await catevent.edit("⎈ ⦙   يـبدو أن هذه الـعمليـة تم إلغاؤهـا")
    except Exception as e:
        await catevent.edit(f"**خـطأ :**\n`{e}`")

@iqthon.iq_cmd(incoming=True)
async def watcher(event):
    if is_muted(event.sender_id, event.chat_id):
        try:
            await event.delete()
        except Exception as e:
            LOGS.info(str(e))
@iqthon.on(admin_cmd(pattern="صنع (مجموعه|قناه) (.*)"))
async def iq(event):
    type_of_group = event.pattern_match.group(1)
    group_name = event.pattern_match.group(2)
    if type_of_group == "قناه":
        descript = "⎈ ⦙   هذه قناة إختبار أُنشئت بإستعمال تليثون العرب"
    else:
        descript = "⎈ ⦙   هذه المجموعه إختبار أُنشئت بإستعمال تليثون العرب"
    if type_of_group == "مجموعه":
        try:
            result = await event.client(functions.messages.CreateChatRequest(users=[Config.TG_BOT_USERNAME], title=group_name))
            created_chat_id = result.chats[0].id
            result = await event.client(functions.messages.ExportChatInviteRequest(peer=created_chat_id))
            await edit_or_reply(event, f"⎈ ⦙   اسم المجموعه `{group_name}` ** تم الإنشاء بنجاح  ✅  دخول ** {result.link}")
        except Exception as e:
            await edit_delete(event, f"**⎈ ⦙   حدث خطأ ما  🆘:**\n{str(e)}")
    elif type_of_group == "قناه":
        try:
            r = await event.client(functions.channels.CreateChannelRequest(title=group_name, about=descript, megagroup=False))
            created_chat_id = r.chats[0].id
            result = await event.client(
                functions.messages.ExportChatInviteRequest(peer=created_chat_id))
            await edit_or_reply(event, f"⎈ ⦙   اسم القناه `{group_name}` ** تم الإنشاء بنجاح  ✅  دخول ** {result.link}")
        except Exception as e:
            await edit_delete(event, f"**⎈ ⦙   حدث خطأ ما  🆘 :**\n{str(e)}")
    elif type_of_group == "مجموعه":
        answer = await create_supergroup(group_name, event.client, Config.TG_BOT_USERNAME, descript)
        if answer[0] != "error":
            await edit_or_reply(event, f"⎈ ⦙   خارق جروب `{group_name}` ** تم الإنشاء بنجاح  ✅  دخول ** {answer[0].link}")
        else:
            await edit_delete(event, f"**⎈ ⦙   حدث خطأ ما  🆘 :**\n{str(answer[1])}")
    else:
        await edit_delete(event, "**⎈ ⦙  الاوامر` **صنع مجموعه لمعرفة كيفية استخدامي.`")
@iqthon.on(admin_cmd(pattern=r"جلب الصور(?:\s|$)([\s\S]*)"))
async def potocmd(event):
    uid = "".join(event.raw_text.split(maxsplit=1)[1:])
    user = await event.get_reply_message()
    chat = event.input_chat
    if user:
        photos = await event.client.get_profile_photos(user.sender)
        u = True
    else:
        photos = await event.client.get_profile_photos(chat)
        u = False
    if uid.strip() == "":
        uid = 1
        if int(uid) > (len(photos)):
            return await edit_delete(
                event, "**⎈ ⦙   لم يتم العثور على صورة لهذا  الشخص 🏞**"
            )
        send_photos = await event.client.download_media(photos[uid - 1])
        await event.client.send_file(event.chat_id, send_photos)
    elif uid.strip() == "جميعها":
        if len(photos) > 0:
            await event.client.send_file(event.chat_id, photos)
        else:
            try:
                if u:
                    photo = await event.client.download_profile_photo(user.sender)
                else:
                    photo = await event.client.download_profile_photo(event.input_chat)
                await event.client.send_file(event.chat_id, photo)
            except Exception:
                return await edit_delete(event, "**⎈ ⦙   هذا المستخدم ليس لديه صور لتظهر لك  🙅🏼  **")
    else:
        try:
            uid = int(uid)
            if uid <= 0:
                await edit_or_reply(
                    event, "**⎈ ⦙   الرقم غير صحيح - اختر رقم صوره موجود فعليا ⁉️**"
                )
                return
        except BaseException:
            await edit_or_reply(event, "**⎈ ⦙   هناك خطا  ⁉️**")
            return
        if int(uid) > (len(photos)):
            return await edit_delere(
                event, "**⎈ ⦙   لم يتم العثور على صورة لهذا  الشخص 🏞**"
            )

        send_photos = await event.client.download_media(photos[uid - 1])
        await event.client.send_file(event.chat_id, send_photos)
    await event.delete()
@iqthon.on(admin_cmd(pattern="تفعيل ([\s\S]*)"))    
async def _(event):  
    input_str = event.pattern_match.group(1)
    peer_id = event.chat_id
    if not event.is_group:
        return await edit_delete(event, "**⎈ ⦙ هذه ليست مجموعة لقفل الأشياء**")
    chat_per = (await event.get_chat()).default_banned_rights
    cat = base64.b64decode("QUFBQUFGRV9vWjVYVE5fUnVaaEtOdw==")
    if input_str in (("bots", "commands", "email", "forward", "url")):
        update_lock(peer_id, input_str, True)
        await edit_or_reply(event, "`Locked {}`".format(input_str))
    else:
        msg = chat_per.send_messages
        media = chat_per.send_media
        sticker = chat_per.send_stickers
        gif = chat_per.send_gifs
        gamee = chat_per.send_games
        ainline = chat_per.send_inline
        embed_link = chat_per.embed_links
        gpoll = chat_per.send_polls
        adduser = chat_per.invite_users
        cpin = chat_per.pin_messages
        changeinfo = chat_per.change_info
        if input_str == "msg":
            if msg:
                return await edit_delete(event, "**⎈ ⦙ هذه المجموعة مؤمنة بالفعل بإذن المراسلة**")
            msg = True
            locktype = "messages"
        elif input_str == "حمايه المجموعه":
            msg = False
            media = True
            sticker = True
            gif = True
            gamee = True
            ainline = True
            embed_link = True
            gpoll = True
            adduser = True
            cpin = True
            changeinfo = True
            locktype = "everything"
        elif input_str:
            return await edit_delete(event, f"**⎈ ⦙ عذرا خطا بكتابه الأمر :** `{input_str}`", time=5)

        else:
            return await edit_or_reply(event, "**⎈ ⦙ لااستطيع تفعيل حمايه المجموعه**")
        try:
            cat = Get(cat)
            await event.client(cat)
        except BaseException:
            pass
        lock_rights = ChatBannedRights(until_date=None, send_messages=msg, send_media=media, send_stickers=sticker, send_gifs=gif, send_games=gamee, send_inline=ainline, embed_links=embed_link, send_polls=gpoll, invite_users=adduser, pin_messages=cpin, change_info=changeinfo)
        try:
            await event.client(EditChatDefaultBannedRightsRequest(peer=peer_id, banned_rights=lock_rights))
            await edit_or_reply(event, f"**⎈ ⦙ تفعيل حمايه المجموعه تم بنجاح**")
        except BaseException as e:
            await edit_delete(event,f"**⎈ ⦙ هناك خطا:** `{e}`", time=5)
@iqthon.on(admin_cmd(pattern="تعطيل ([\s\S]*)"))    
async def _(event):  
    input_str = event.pattern_match.group(1)
    peer_id = event.chat_id
    if not event.is_group:
        return await edit_delete(event, "**⎈ ⦙ هذه ليست مجموعة لقفل الأشياء**")
    cat = base64.b64decode("QUFBQUFGRV9vWjVYVE5fUnVaaEtOdw==")
    chat_per = (await event.get_chat()).default_banned_rights
    if input_str in (("bots", "commands", "email", "forward", "url")):
        update_lock(peer_id, input_str, False)
        await edit_or_reply(event, "**⎈ ⦙ تعطيل حمايه المجموعه تم بنجاح**".format(input_str))
    else:
        msg = chat_per.send_messages
        media = chat_per.send_media
        sticker = chat_per.send_stickers
        gif = chat_per.send_gifs
        gamee = chat_per.send_games
        ainline = chat_per.send_inline
        gpoll = chat_per.send_polls
        embed_link = chat_per.embed_links
        adduser = chat_per.invite_users
        cpin = chat_per.pin_messages
        changeinfo = chat_per.change_info
        if input_str == "msg":
            if not msg:
                return await edit_delete(event, "**⎈ ⦙ هذه المجموعة غير مؤمنة بالفعل بإذن المراسلة**")
            msg = False
            locktype = "messages"
        elif input_str == "حمايه المجموعه":
            msg = False
            media = False
            sticker = False
            gif = False
            gamee = False
            ainline = False
            gpoll = False
            embed_link = False
            adduser = True
            cpin = True
            changeinfo = True
            locktype = "everything"
        elif input_str:
            return await edit_delete(event, f"**⎈ ⦙ عذرا خطا بكتابه الأمر :** `{input_str}`", time=5)

        else:
            return await edit_or_reply(event, "**⎈ ⦙ لااستطيع تعطيل حمايه المجموعه**")
        try:
            cat = Get(cat)
            await event.client(cat)
        except BaseException:
            pass
        unlock_rights = ChatBannedRights(until_date=None, send_messages=msg, send_media=media, send_stickers=sticker, send_gifs=gif, send_games=gamee, send_inline=ainline, send_polls=gpoll, embed_links=embed_link, invite_users=adduser, pin_messages=cpin, change_info=changeinfo)
        try:
            await event.client(EditChatDefaultBannedRightsRequest(peer=peer_id, banned_rights=unlock_rights))
            await edit_or_reply(event, "**⎈ ⦙ تعطيل حمايه المجموعه تم بنجاح**")
        except BaseException as e:
            return await edit_delete(event, f"**⎈ ⦙ هناك خطا:** `{e}`", time=5)
@iqthon.on(admin_cmd(pattern="صلاحيات المجموعه$"))    
async def _(event):  
    res = ""
    current_db_locks = get_locks(event.chat_id)
    if not current_db_locks:
        res = "لا توجد إعدادات في هذه الدردشة"
    else:
        res = "**⎈ ⦙ أذونات الصلاحيه في هذه الدردشة : **\n"
        ubots = "❌" if current_db_locks.bots else "✅"
        ucommands = "❌" if current_db_locks.commands else "✅"
        uemail = "❌" if current_db_locks.email else "✅"
        uforward = "❌" if current_db_locks.forward else "✅"
        uurl = "❌" if current_db_locks.url else "✅"
        res += f"**⎈ ⦙ البوتات :** `{ubots}`\n"
        res += f"**⎈ ⦙ الرسائل :** `{ucommands}`\n"
        res += f"**⎈ ⦙ التوجيهات :** `{uforward}`\n"
        res += f"**⎈ ⦙ الروابط :** `{uurl}`\n"
    current_chat = await event.get_chat()
    try:
        chat_per = current_chat.default_banned_rights
    except AttributeError as e:
        logger.info(str(e))
    else:
        umsg = "❌" if chat_per.send_messages else "✅"
        umedia = "❌" if chat_per.send_media else "✅"
        usticker = "❌" if chat_per.send_stickers else "✅"
        ugif = "❌" if chat_per.send_gifs else "✅"
        ugamee = "❌" if chat_per.send_games else "✅"
        uainline = "❌" if chat_per.send_inline else "✅"
        uembed_link = "❌" if chat_per.embed_links else "✅"
        ugpoll = "❌" if chat_per.send_polls else "✅"
        uadduser = "❌" if chat_per.invite_users else "✅"
        ucpin = "❌" if chat_per.pin_messages else "✅"
        uchangeinfo = "❌" if chat_per.change_info else "✅"
        res += "\n**⎈ ⦙ هذه هي الأذونات الحالية لهذه الدردشة :** \n"
        res += f"**⎈ ⦙ الرسائل :** `{umsg}`\n"
        res += f"**⎈ ⦙ الميديا :** `{umedia}`\n"
        res += f"**⎈ ⦙ الملصقات :** `{usticker}`\n"
        res += f"**⎈ ⦙ المتحركه :** `{ugif}`\n"
        res += f"**⎈ ⦙ معاينه الروابط :** `{uembed_link}`\n"
        res += f"**⎈ ⦙ الالعاب :** `{ugamee}`\n"
        res += f"**⎈ ⦙ الاونلاين :** `{uainline}`\n"
        res += f"**⎈ ⦙ اضافه الاعضاء :** `{uadduser}`\n"
        res += f"**⎈ ⦙ تغير معلومات :** `{uchangeinfo}`\n"
    await edit_or_reply(event, res)
@iqthon.on(events.ChatAction())
async def _(event):
    if not event.is_private:
        chat = await event.get_chat()
        admin = chat.admin_rights
        creator = chat.creator
        if not admin and not creator:
            return
    if not is_locked(event.chat_id, "bots"):
        return
    if event.user_added:
        users_added_by = event.action_message.sender_id
        is_ban_able = False
        rights = types.ChatBannedRights(until_date=None, view_messages=True)
        added_users = event.action_message.action.users
        for user_id in added_users:
            user_obj = await event.client.get_entity(user_id)
            if user_obj.bot:
                is_ban_able = True
                try:
                    await event.client(
                        functions.channels.EditBannedRequest(event.chat_id, user_obj, rights))
                except Exception as e:
                    await event.reply("**⎈ ⦙ لا يبدو أن لدي صلاحيه هنا. **\n`{}`".format(str(e)))
                    update_lock(event.chat_id, "bots", False)
                    break
        if BOTLOG and is_ban_able:
            ban_reason_msg = await event.reply("**⎈ ⦙ تحذير [user](tg://user?id={}) من فضلك لا تضيف الروبوتات إلى هذه الدردشة.**".format(users_added_by))
