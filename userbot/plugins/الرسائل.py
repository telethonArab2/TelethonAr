import re
import asyncio
import base64
import string
import os
import subprocess
import io
import sys
import traceback
import random
import textwrap
import requests
from datetime import datetime
from asyncio import sleep
from geopy.geocoders import Nominatim
from gtts import gTTS
from telethon import custom, events
from telethon.tl import types, functions, types
from telethon.errors import rpcbaseerrors
from telethon.tl.types import Channel, MessageMediaWebPage, ChatBannedRights
from telethon import Button
from telethon.tl.functions.messages import GetStickerSetRequest
from telethon.tl.functions.messages import ImportChatInviteRequest as Get
from random import choice, randint
from telethon.errors import BadRequestError
from telethon.tl.functions.channels import EditAdminRequest
from telethon.tl.types import ChatAdminRights
from telethon.tl.functions.channels import EditBannedRequest
from telethon.utils import get_display_name
from googletrans import LANGUAGES, Translator
from telethon.tl.types import InputMessagesFilterDocument, InputMessagesFilterEmpty, InputMessagesFilterGeo, InputMessagesFilterGif, InputMessagesFilterMusic, InputMessagesFilterPhotos, InputMessagesFilterRoundVideo, InputMessagesFilterUrl, InputMessagesFilterVideo, InputMessagesFilterVoice, InputMessagesFilterMyMentions, InputMessagesFilterPinned     
from telethon.tl.types import ChannelParticipantsAdmins
from telethon.tl.types import ChannelParticipantAdmin as admin
from telethon.tl.types import ChannelParticipantCreator as owner
from telethon.tl.types import UserStatusOffline as off
from telethon.tl.types import UserStatusOnline as onn
from telethon.tl.types import UserStatusRecently as rec
from userbot import iqthon
from userbot.core.logger import logging
from ..Config import Config
from ..core.managers import edit_delete, edit_or_reply
from ..helpers.tools import media_type
from ..helpers.utils import _catutils, parse_pre, yaml_format
from ..helpers.functions import deEmojify, hide_inlinebot, waifutxt
from PIL import Image, ImageDraw, ImageFont
from ..helpers import reply_id
from ..sql_helper.globals import addgvar, delgvar, gvarstatus
from ..sql_helper.welcome_sql import add_welcome_setting, get_current_welcome_settings, rm_welcome_setting, update_previous_welcome
from ..sql_helper.echo_sql import addecho, get_all_echos, get_echos, is_echo, remove_all_echos, remove_echo, remove_echos
from ..sql_helper.filter_sql import add_filter, get_filters, remove_all_filters, remove_filter
from ..sql_helper import antiflood_sql as sql
from ..sql_helper import blacklist_sql as sql1
from ..utils import is_admin
from . import BOTLOG, BOTLOG_CHATID, get_user_from_event, deEmojify, reply_id
from . import convert_toimage, convert_tosticker
LOGS = logging.getLogger(__name__)
CHAT_FLOOD = sql.__load_flood_settings()
ANTI_FLOOD_WARN_MODE = ChatBannedRights(
until_date=None, view_messages=None, send_messages=True)
BTN_URL_REGEX = re.compile(r"(\[([^\[]+?)\]\<buttonurl:(?:/{0,2})(.+?)(:same)?\>)")
ALLGROUB = gvarstatus("OR_ALLGROUB") or "للكروب"
ALLPRIVATE = gvarstatus("OR_ALLPRIVATE") or "للكروب"
FOTOSECRET = gvarstatus("OR_FOTOSECRET") or "جلب الوقتيه"


def build_keyboard(buttons):
    keyb = []
    for btn in buttons:
        if btn[2] and keyb:
            keyb[-1].append(Button.url(btn[0], btn[1]))
        else:
            keyb.append([Button.url(btn[0], btn[1])])
    return keyb
@iqthon.on(admin_cmd(pattern="وقتيه (\d*) ([\s\S]*)"))    
async def _(event):
    cat = ("".join(event.text.split(maxsplit=1)[1:])).split(" ", 1)
    message = cat[1]
    ttl = int(cat[0])
    await event.delete()
    await sleep(ttl)
    await event.respond(message)
class FPOST:
    def __init__(self) -> None:
        self.GROUPSID = []
        self.MSG_CACHE = {}
FPOST_ = FPOST()
async def all_groups_id(cat):
    catgroups = []
    async for dialog in cat.client.iter_dialogs():
        entity = dialog.entity
        if isinstance(entity, Channel) and entity.megagroup:
            catgroups.append(entity.id)
    return catgroups
@iqthon.on(admin_cmd(pattern="ازاله التوجيه(?: |$)(.*)"))    
async def _(event):
    try:
        await event.delete()
    except Exception as e:
        LOGS.info(str(e))
    m = await event.get_reply_message()
    if not m:
        return
    if m.media and not isinstance(m.media, MessageMediaWebPage):
        return await event.client.send_file(event.chat_id, m.media, caption=m.text)
    await event.client.send_message(event.chat_id, m.text)
@iqthon.on(admin_cmd(pattern=f"{ALLGROUB} ?(.*)$"))    
async def gcast(event):
    if not event.out and not is_fullsudo(event.sender_id):
        return await edit_or_reply(event, "هـذا الامـر مقـيد ")
    xx = event.pattern_match.group(1)
    if not xx:
        return edit_or_reply(event, "**⎈ ⦙   يجـب وضـع نـص مع الامـر للتوجيـه**")
    tt = event.text
    msg = tt[6:]
    event = await edit_or_reply(event, "** ⎈ ⦙   يتـم الـتوجيـة للـمجموعـات انتـظر قليلا**")
    er = 0
    done = 0
    async for x in bot.iter_dialogs():
        if x.is_group:
            chat = x.id
            try:
                done += 1
                await bot.send_message(chat, msg)
            except BaseException:
                er += 1
    await event.edit(f"⎈ ⦙   تـم بنـجـاح فـي {done} من الـدردشـات , خطـأ فـي {er} من الـدردشـات")
async def getTranslate(text, **kwargs):
    translator = Translator()
    result = None
    for _ in range(10):
        try:
            result = translator.translate(text, **kwargs)
        except Exception:
            translator = Translator()
            await sleep(0.1)
    return result
@iqthon.iq_cmd(incoming=True, groups_only=True)
async def _(event):
    if not CHAT_FLOOD:
        return
    catadmin = await is_admin(event.client, event.chat_id, event.client.uid)
    if not catadmin:
        return
    if str(event.chat_id) not in CHAT_FLOOD:
        return
    should_ban = sql.update_flood(event.chat_id, event.message.sender_id)
    if not should_ban:
        return
    try:
        await event.client(EditBannedRequest(event.chat_id, event.message.sender_id, ANTI_FLOOD_WARN_MODE))
    except Exception as e:
        no_admin_privilege_message = await event.client.send_message(entity=event.chat_id, message=f"""**⎈ ⦙   تحذير تكرار فـي المجموعة : لـ** @تاك للادمنيه  : [User](tg://user?id={event.message.sender_id}) لقد قام بتكرار الرسائل . `{str(e)}`""", reply_to=event.message.id)
        await asyncio.sleep(4)
        await no_admin_privilege_message.edit("**⎈ ⦙   هذا الشخص الذي قام بتكرار الرسائل والازعاج **")
    else:
        await event.client.send_message(entity=event.chat_id, message=f"""**⎈ ⦙   تحذير تكرار فـي المجموعة : لـ** [User](tg://user?id={event.message.sender_id}) تم تقيد الشخص بسبب عمل تكرار للرسائل والازعاج.""", reply_to=event.message.id)
@iqthon.on(admin_cmd(pattern=f"{ALLPRIVATE} ?(.*)$"))    
async def gucast(event):
    if not event.out and not is_fullsudo(event.sender_id):
        return await edit_or_reply(event, "هـذا الامـر مقـيد ")
    xx = event.pattern_match.group(1)
    if not xx:
        return edit_or_reply(event, "** ⎈ ⦙   يجـب وضـع نـص مع الامـر للتوجيـه**")
    tt = event.text
    msg = tt[7:]
    await edit_or_reply(event, "** ⎈ ⦙   يتـم الـتوجيـة للخـاص انتـظر قليلا**")
    er = 0
    done = 0
    async for x in bot.iter_dialogs():
        if x.is_user and not x.entity.bot:
            chat = x.id
            try:
                done += 1
                await bot.send_message(chat, msg)
            except BaseException:
                er += 1
    await event.edit(f"⎈ ⦙   تـم بنـجـاح فـي {done} من الـدردشـات , خطـأ فـي {er} من الـدردشـات")
async def spam_function(event, sandy, cat, sleeptimem, sleeptimet, DelaySpam=False):
    counter = int(cat[0])
    if len(cat) == 2:
        spam_message = str(cat[1])
        for _ in range(counter):
            if event.reply_to_msg_id:
                await sandy.reply(spam_message)
            else:
                await event.client.send_message(event.chat_id, spam_message)
            await asyncio.sleep(sleeptimet)
    elif event.reply_to_msg_id and sandy.media:
        for _ in range(counter):
            sandy = await event.client.send_file(event.chat_id, sandy, caption=sandy.text)
            await _catutils.unsavegif(event, sandy)
            await asyncio.sleep(sleeptimem)
        if BOTLOG:
            if DelaySpam is not True:
                if event.is_private:
                    await event.client.send_message(BOTLOG_CHATID, "**⎈ ⦙   التڪـرار  ♽**\n" + f"**⎈ ⦙   تم تنفيذ التكرار بنجاح في ▷** [User](tg://user?id={event.chat_id}) **الدردشـة مـع** {counter} **عدد المرات مع الرسالة أدناه**")
                else:
                    await event.client.send_message(BOTLOG_CHATID, "**⎈ ⦙   التڪـرار  ♽**\n" + f"**⎈ ⦙   تم تنفيذ التكرار بنجاح في ▷** {get_display_name(await event.get_chat())}(`{event.chat_id}`) **مـع** {counter} **عدد المرات مع الرسالة أدناه**")
            elif event.is_private:
                await event.client.send_message(BOTLOG_CHATID, "**⎈ ⦙   التكرار الوقتي 💢**\n" + f"**⎈ ⦙   تم تنفيذ التكرار الوقتي  بنجاح في ▷** [User](tg://user?id={event.chat_id}) **الدردشـة مـع** {counter} **عدد المرات مع الرسالة أدناه مع التأخير** {sleeptimet} ** الثوانـي ⏱**")
            else:
                await event.client.send_message(BOTLOG_CHATID, "**⎈ ⦙   التكرار الوقتي 💢**\n" + f"**⎈ ⦙   تم تنفيذ التكرار الوقتي  بنجاح في ▷** {get_display_name(await event.get_chat())}(`{event.chat_id}`) **مـع** {counter} **عدد المرات مع الرسالة أدناه مع التأخير** {sleeptimet} ** الثوانـي ⏱**")

            sandy = await event.client.send_file(BOTLOG_CHATID, sandy)
            await _catutils.unsavegif(event, sandy)
        return
    elif event.reply_to_msg_id and sandy.text:
        spam_message = sandy.text
        for _ in range(counter):
            await event.client.send_message(event.chat_id, spam_message)
            await asyncio.sleep(sleeptimet)
    else:
        return
    if DelaySpam is not True:
        if BOTLOG:
            if event.is_private:
                await event.client.send_message(BOTLOG_CHATID, "**⎈ ⦙   التڪـرار  ♽**\n" + f"**⎈ ⦙   تم تنفيذ التكرار بنجاح في ▷** [User](tg://user?id={event.chat_id}) **الدردشـة مـع** {counter} **رسائـل الـ  ✉️ :** \n" + f"⎈ ⦙   `{spam_message}`")
            else:
                await event.client.send_message(BOTLOG_CHATID, "**⎈ ⦙   التڪـرار  ♽**\n" + f"**⎈ ⦙   تم تنفيذ التكرار بنجاح في ▷** {get_display_name(await event.get_chat())}(`{event.chat_id}`) **الدردشـة مـع** {counter} **رسائـل الـ  ✉️ :** \n" + f"⎈ ⦙   `{spam_message}`")
    elif BOTLOG:
        if event.is_private:
            await event.client.send_message(BOTLOG_CHATID, "**⎈ ⦙   التكرار الوقتي 💢**\n" + f"**⎈ ⦙   تم تنفيذ التكرار الوقتي  بنجاح في ▷** [User](tg://user?id={event.chat_id}) **الدردشـة مـع** {sleeptimet} seconds and with {counter} **رسائـل الـ  ✉️ :** \n" + f"⎈ ⦙   `{spam_message}`")
        else:
            await event.client.send_message(BOTLOG_CHATID, "**⎈ ⦙   التكرار الوقتي 💢**\n" + f"**⎈ ⦙   تم تنفيذ التكرار الوقتي  بنجاح في ▷** {get_display_name(await event.get_chat())}(`{event.chat_id}`) **الدردشـة مـع** {sleeptimet} **الثوانـي و مـع** {counter} **رسائـل الـ  ✉️ :** \n" + f"⎈ ⦙   `{spam_message}`")
@iqthon.on(admin_cmd(pattern="كتابه وهمي(?:\s|$)([\s\S]*)"))
async def _iq(iqthon):
    iq = iqthon.pattern_match.group(1)
    if not (iq or iq.isdigit()):
        iq = 100
    else:
        try:
            iq = int(iq)
        except BaseException:
            try:
                iq = await iqthon.ban_time(iq)
            except BaseException:
                return await event.edit("**اكتب الامر بشكل صحيح**")
    await iqthon.edit(f"**تم بدء وضع الكتابة الوهمية لـ {iq} من الثوانـي**")
    async with iqthon.client.action(iqthon.chat_id, "typing"):
        await asyncio.sleep(iq)
@iqthon.on(admin_cmd(pattern="تكرار (.*)"))    
async def spammer(event):
    sandy = await event.get_reply_message()
    cat = ("".join(event.text.split(maxsplit=1)[1:])).split(" ", 1)
    try:
        counter = int(cat[0])
    except Exception:
        return await edit_delete(event, "⎈ ⦙  إستخـدم بناء الجملة المناسب للإزعاج، صيغة Foe تشير إلىٰ قائمة التعليمات 💡")
    if counter > 50:
        sleeptimet = 0.5
        sleeptimem = 1
    else:
        sleeptimet = 0.1
        sleeptimem = 0.3
    await event.delete()
    await spam_function(event, sandy, cat, sleeptimem, sleeptimet)
@iqthon.on(admin_cmd(pattern="مؤقته (\d*) ([\s\S]*)"))    
async def selfdestruct(destroy):
    cat = ("".join(destroy.text.split(maxsplit=1)[1:])).split(" ", 1)
    message = cat[1]
    ttl = int(cat[0])
    await destroy.delete()
    smsg = await destroy.client.send_message(destroy.chat_id, message)
    await sleep(ttl)
    await smsg.delete()
def iqthonveFile(input_file_name):
    headers = {"X-API-Key": "paMkgkpsm4EYbDi4AKh4Nu9G",}
    files = {"image_file": (input_file_name, open(input_file_name, "rb")),}
    return requests.post("https://api.remove.bg/v1.0/removebg", headers=headers, files=files, allow_redirects=True, stream=True)
def iqthonveURL(input_url):
    headers = {"X-API-Key": "paMkgkpsm4EYbDi4AKh4Nu9G",}
    data = {"image_url": input_url}
    return requests.post("https://api.remove.bg/v1.0/removebg",headers=headers,data=data,allow_redirects=True,stream=True)
@iqthon.on(events.ChatAction)
async def _(event):  # sourcery no-metrics
    cws = get_current_welcome_settings(event.chat_id)
    if (
        cws
        and (event.user_joined or event.user_added)
        and not (await event.get_user()).bot
    ):
        if gvarstatus("clean_welcome") is None:
            try:
                await event.client.delete_messages(event.chat_id, cws.previous_welcome)
            except Exception as e:
                LOGS.warn(str(e))
        a_user = await event.get_user()
        chat = await event.get_chat()
        me = await event.client.get_me()
        title = chat.title or "this chat"
        participants = await event.client.get_participants(chat)
        count = len(participants)
        mention = "<a href='tg://user?id={}'>{}</a>".format(a_user.id, a_user.first_name)
        my_mention = "<a href='tg://user?id={}'>{}</a>".format(me.id, me.first_name)
        first = a_user.first_name
        last = a_user.last_name
        fullname = f"{first} {last}" if last else first
        username = f"@{a_user.username}" if a_user.username else mention
        userid = a_user.id
        my_first = me.first_name
        my_last = me.last_name
        my_fullname = f"{my_first} {my_last}" if my_last else my_first
        my_username = f"@{me.username}" if me.username else my_mention
        file_media = None
        current_saved_welcome_message = None
        if cws:
            if cws.f_mesg_id:
                msg_o = await event.client.get_messages(entity=BOTLOG_CHATID, ids=int(cws.f_mesg_id))
                file_media = msg_o.media
                current_saved_welcome_message = msg_o.message
            elif cws.reply:
                current_saved_welcome_message = cws.reply
        current_message = await event.reply(current_saved_welcome_message.format(mention=mention, title=title, count=count, first=first, last=last, fullname=fullname, username=username, userid=userid, my_first=my_first, my_last=my_last, my_fullname=my_fullname, my_username=my_username,
                my_mention=my_mention,            ),
            file=file_media,
            parse_mode="html")
        update_previous_welcome(event.chat_id, current_message.id)
@iqthon.on(admin_cmd(pattern="ترحيب(?:\s|$)([\s\S]*)"))    
async def save_welcome(event):
    msg = await event.get_reply_message()
    string = "".join(event.text.split(maxsplit=1)[1:])
    msg_id = None
    if msg and msg.media and not string:
        if BOTLOG_CHATID:
            await event.client.send_message(BOTLOG_CHATID, f"⎈ ⦙  رسالة الترحيب 🔖 : \n⎈ ⦙  ايدي الدردشة 🆔 : {event.chat_id}\n⎈ ⦙  يتم حفظ الرسالة التالية كملاحظة ترحيبية لـ 🔖 : {event.chat.title}, ")
            msg_o = await event.client.forward_messages(entity=BOTLOG_CHATID, messages=msg, from_peer=event.chat_id, silent=True)
            msg_id = msg_o.id
        else:
            return await edit_or_reply(event, "⎈ ⦙   حفظ الصورة كرسالة ترحيبية يتطلب وضع الفار لـ  BOTLOG_CHATID ")
    elif event.reply_to_msg_id and not string:
        rep_msg = await event.get_reply_message()
        string = rep_msg.text
    success = "**⎈ ⦙  تم حفظ الترحيب بهذه الدردشة بنجاح ✅**"
    if add_welcome_setting(event.chat_id, 0, string, msg_id) is True:
        return await edit_or_reply(event, success.format("saved"))
    rm_welcome_setting(event.chat_id)
    if add_welcome_setting(event.chat_id, 0, string, msg_id) is True:
        return await edit_or_reply(event, success.format("updated"))
    await edit_or_reply("⎈ ⦙  حدث خطأ أثناء وضع ترحيب في هذه المجموعة ⚠️")
@iqthon.on(admin_cmd(pattern="مسح الترحيبات(?: |$)(.*)"))    
async def del_welcome(event):
    if rm_welcome_setting(event.chat_id) is True:
        await edit_or_reply(event, "**⎈ ⦙  تم مسح جميع الرسائل الترحيبية لهذه الدردشة بنجاح ✅**")
    else:
        await edit_or_reply(event, "**⎈ ⦙  لم يتم حفظ أي رسائل ترحيبية هنا ⚠️**")
Tnsmeetst = {}
Tnsmeet = {"ا": InputMessagesFilterVideo, "ل": InputMessagesFilterGif, "و": InputMessagesFilterUrl, "س": InputMessagesFilterPhotos, "ئ": InputMessagesFilterDocument, "ط": InputMessagesFilterVoice}
@iqthon.on(admin_cmd(pattern="ترحيباتي(?: |$)(.*)"))    
async def show_welcome(event):
    cws = get_current_welcome_settings(event.chat_id)
    if not cws:
        return await edit_or_reply(event, "**⎈ ⦙  لم يتم حفظ أي رسائل ترحيبية هنا ⚠️**")
    if cws.f_mesg_id:
        msg_o = await event.client.get_messages(entity=BOTLOG_CHATID, ids=int(cws.f_mesg_id))
        await edit_or_reply(event, "**⎈ ⦙  أنا الآن أقوم بالترحيب بالمستخدمين الجدد مع هذه الرسالة ✅**")
        await event.reply(msg_o.message, file=msg_o.media)
    elif cws.reply:
        await edit_or_reply(event, "**⎈ ⦙  أنا الآن أقوم بالترحيب بالمستخدمين الجدد مع هذه الرسالة ✅**")
        await event.reply(cws.reply, link_preview=False)
@iqthon.on(admin_cmd(pattern="رساله الترحيب السابقه (تشغيل|ايقاف)$"))    
async def del_welcome(event):
    input_str = event.pattern_match.group(1)
    if input_str == "تشغيل":
        if gvarstatus("clean_welcome") is None:
            return await edit_delete(event, "**⎈ ⦙  تم تشغيلها بالفعل ✅**")
        delgvar("clean_welcome")
        return await edit_delete(event, "**⎈ ⦙   من الآن رسالة الترحيب السابقة سيتم حذفها وسيتم إرسال رسالة الترحيب الجديدة ⚠️**")
    if gvarstatus("clean_welcome") is None:
        addgvar("clean_welcome", "false")
        return await edit_delete(event, "**⎈ ⦙  من الآن لن يتم حذف رسالة الترحيب السابقة ⚠️**")
    await edit_delete(event, "**⎈ ⦙  تم إيقافها بالفعل ✅**")
@iqthon.on(admin_cmd(pattern="موقع(?: |$)(.*)"))    
async def gps(event):
    reply_to_id = await reply_id(event)
    input_str = event.pattern_match.group(1)
    catevent = await edit_or_reply(event, "** ⎈ ⦙   جاري العثـور على الموقع  … **")
    geolocator = Nominatim(user_agent="catuserbot")
    geoloc = geolocator.geocode(input_str)
    if geoloc:
        lon = geoloc.longitude
        lat = geoloc.latitude
        await event.client.send_file(
            event.chat_id,
            file=types.InputMediaGeoPoint(types.InputGeoPoint(lat, lon)),
            caption=f"**⎈ ⦙   الموقـع 𖠕  : **`{input_str}`", reply_to=reply_to_id)
        await catevent.delete()
    else:
        await catevent.edit("⎈ ⦙   عـذراً، لـم أستطـع إيجـاده  ⚠️")
async def ocr_iqthon(filename, overlay=False,api_key="160984b1d988957", language="eng"):
    payload = {"isOverlayRequired": overlay,"apikey": api_key,"language": language}
    with open(filename, "rb") as f:
        r = requests.post("https://api.ocr.space/parse/image",files={filename: f},data=payload)
    return r.json()
@iqthon.on(admin_cmd(pattern="فيديو وهمي(?:\s|$)([\s\S]*)"))
async def _iq(iqthon):
    iq = iqthon.pattern_match.group(1)
    if not (iq or iq.isdigit()):
        iq = 100
    else:
        try:
            iq = int(iq)
        except BaseException:
            try:
                iq = await iqthon.ban_time(iq)
            except BaseException:
                return await event.edit("**اكتب الامر بشكل صحيح**")
    await iqthon.edit(f"**تم بدء وضع فيديو وهمي لـ {iq} من الثوانـي**")
    async with iqthon.client.action(iqthon.chat_id, "record-video"):
        await asyncio.sleep(iq)
@iqthon.on(admin_cmd(pattern="ازعاج(?: |$)(.*)"))    
async def echo(event):
    if event.reply_to_msg_id is None:
        return await edit_or_reply(event, "**⎈ ⦙   يرجى الرد على الشخص الذي تـريد ازعاجه ❕**")
    catevent = await edit_or_reply(event, "**⎈ ⦙   يتم تفعيل هذا الامر انتظر قليلا ❕**")
    user, rank = await get_user_from_event(event, catevent, nogroup=True)
    if not user:
        return
    reply_msg = await event.get_reply_message()
    chat_id = event.chat_id
    user_id = reply_msg.sender_id
    if event.is_private:
        chat_name = user.first_name
        chat_type = "Personal"
    else:
        chat_name = event.chat.title
        chat_type = "Group"
    user_name = user.first_name
    user_username = user.username
    if is_echo(chat_id, user_id):
        return await edit_or_reply(event, "**⎈ ⦙   تـم تفـعيل وضـع الازعاج على الشخص بنجاح ✅ **")
    try:
        addecho(chat_id, user_id, chat_name, user_name, user_username, chat_type)
    except Exception as e:
        await edit_delete(catevent, f"⎈ ⦙   Error:\n`{str(e)}`")
    else:
        await edit_or_reply(catevent, "**⎈ ⦙   تـم تفعـيل امـر التقليد علـى هذا الشـخص**\n **⎈ ⦙   سـيتم تقليـد جميع رسائلـه هـنا**")
@iqthon.on(admin_cmd(pattern="الغاء الازعاج( -a)?"))    
async def echo(event):
    input_str = event.pattern_match.group(1)
    if input_str:
        lecho = get_all_echos()
        if len(lecho) == 0:
            return await edit_delete(event, "**⎈ ⦙   لم يتم تفعيل الازعاج بالاصل لاي شخص ⚠️**")
        try:
            remove_all_echos()
        except Exception as e:
            await edit_delete(event, f"**⎈ ⦙   هناك خطا ‼️ :**\n`{str(e)}`", 10)
        else:
            await edit_or_reply(event, "**⎈ ⦙   تـم ايقاف وضـع الازعاج على الجميع بنجاح ✅ .**")
    else:
        lecho = get_echos(event.chat_id)
        if len(lecho) == 0:
            return await edit_delete(event, "**⎈ ⦙   لم يتم تفعيل الازعاج بالاصل لاي شخص ⚠️**")
        try:
            remove_echos(event.chat_id)
        except Exception as e:
            await edit_delete(event, f"**⎈ ⦙   هناك خطا ‼️ :**\n`{str(e)}`", 10)
        else:
            await edit_or_reply(event, "**⎈ ⦙   تـم ايقاف وضـع الازعاج على الجميع بنجاح ✅**")
@iqthon.on(admin_cmd(pattern="المزعجهم( -a)?$"))    
async def echo(event):  
    input_str = event.pattern_match.group(1)
    private_chats = ""
    output_str = "**⎈ ⦙   قائمه الاشخاص الذين تم ازعاجهم :**\n\n"
    if input_str:
        lsts = get_all_echos()
        group_chats = ""
        if len(lsts) > 0:
            for echos in lsts:
                if echos.chat_type == "Personal":
                    if echos.user_username:
                        private_chats += f"☞ [{echos.user_name}](https://t.me/{echos.user_username})\n"
                    else:
                        private_chats += (f"☞ [{echos.user_name}](tg://user?id={echos.user_id})\n")
                else:
                    if echos.user_username:
                        group_chats += f"☞ [{echos.user_name}](https://t.me/{echos.user_username}) in chat {echos.chat_name} of chat id `{echos.chat_id}`\n"
                    else:
                        group_chats += f"☞ [{echos.user_name}](tg://user?id={echos.user_id}) in chat {echos.chat_name} of chat id `{echos.chat_id}`\n"

        else:
            return await edit_or_reply(event, "**⎈ ⦙   لم يتم تفعيل ازعاج  اي شخص  ⚠️**")
        if private_chats != "":
            output_str += "**⎈ ⦙   الـدردشـات الـخاصة **\n" + private_chats + "\n\n"
        if group_chats != "":
            output_str += "**⎈ ⦙   دردشـات الـمجموعات **\n" + group_chats
    else:
        lsts = get_echos(event.chat_id)
        if len(lsts) <= 0:
            return await edit_or_reply(event, "**لم يتم تفعيل الازعاج بالاصل في هذه الدردشه ⚠️**")

        for echos in lsts:
            if echos.user_username:
                private_chats += (f"☞ [{echos.user_name}](https://t.me/{echos.user_username})\n")
            else:
                private_chats += (f"☞ [{echos.user_name}](tg://user?id={echos.user_id})\n")
        output_str = f"**⎈ ⦙   الاشخاص الذي تم تقليدهم في هذه الدردشه :**\n" + private_chats
    await edit_or_reply(event, output_str)
@iqthon.iq_cmd(incoming=True, edited=False)
async def samereply(event):
    if is_echo(event.chat_id, event.sender_id) and (event.message.text or event.message.sticker):
        await event.reply(event.message)
@iqthon.on(admin_cmd(pattern="صوت وهمي(?:\s|$)([\s\S]*)"))
async def _iq(iqthon):
    iq = iqthon.pattern_match.group(1)
    if not (iq or iq.isdigit()):
        iq = 100
    else:
        try:
            iq = int(iq)
        except BaseException:
            try:
                iq = await iqthon.ban_time(iq)
            except BaseException:
                return await event.edit("**اكتب الامر بشكل صحيح**")
    await iqthon.edit(f"**تم بدء وضع صوت وهمي لـ {iq} من الثوانـي**")
    async with iqthon.client.action(iqthon.chat_id, "record-audio"):
        await asyncio.sleep(iq)
@iqthon.on(admin_cmd(pattern="تنظيف(?:\s|$)([\s\S]*)"))
async def iq(cloneiq):  
    chat = await cloneiq.get_input_chat()
    msgs = []
    count = 0
    input_str = cloneiq.pattern_match.group(1)
    iqype = re.findall(r"\w+", input_str)
    try:
        p_type = iqype[0].replace("-", "")
        input_str = input_str.replace(iqype[0], "").strip()
    except IndexError:
        p_type = None
    error = ""
    result = ""
    await cloneiq.delete()
    reply = await cloneiq.get_reply_message()
    if reply:
        if input_str and input_str.isnumeric():
            if p_type is not None:
                for ty in p_type:
                    if ty in Tnsmeet:
                        async for msg in cloneiq.client.iter_messages(cloneiq.chat_id, limit=int(input_str), offset_id=reply.id - 1, reverse=True, filter=Tnsmeet[ty]):
                            count += 1
                            msgs.append(msg)
                            if len(msgs) == 50:
                                await cloneiq.client.delete_messages(chat, msgs)
                                msgs = []
                        if msgs:
                            await cloneiq.client.delete_messages(chat, msgs)
                    elif ty == "s":
                        error += f"\n**⎈ ⦙   هنـاك خطـا فـي تركـيب الجمـلة 🔩 :**"
                    else:
                        error += f"\n\n⎈ ⦙   `{ty}`  **هنـاك خطـا فـي تركـيب الجمـلة 🔩 :**"
            else:
                count += 1
                async for msg in cloneiq.client.iter_messages(cloneiq.chat_id, limit=(int(input_str) - 1), offset_id=reply.id, reverse=True):
                    msgs.append(msg)
                    count += 1
                    if len(msgs) == 50:
                        await cloneiq.client.delete_messages(chat, msgs)
                        msgs = []
                if msgs:
                    await cloneiq.client.delete_messages(chat, msgs)
        elif input_str and p_type is not None:
            if p_type == "s":
                try:
                    cont, inputstr = input_str.split(" ")
                except ValueError:
                    cont = "error"
                    inputstr = input_str
                cont = cont.strip()
                inputstr = inputstr.strip()
                if cont.isnumeric():
                    async for msg in cloneiq.client.iter_messages(cloneiq.chat_id, limit=int(cont), offset_id=reply.id - 1, reverse=True, search=inputstr):
                        count += 1
                        msgs.append(msg)
                        if len(msgs) == 50:
                            await cloneiq.client.delete_messages(chat, msgs)
                            msgs = []
                else:
                    async for msg in cloneiq.client.iter_messages(cloneiq.chat_id, offset_id=reply.id - 1, reverse=True, search=input_str):
                        count += 1
                        msgs.append(msg)
                        if len(msgs) == 50:
                            await cloneiq.client.delete_messages(chat, msgs)
                            msgs = []
                if msgs:
                    await cloneiq.client.delete_messages(chat, msgs)
            else:
                error += f"\n⎈ ⦙   `{ty}`  **هنـاك خطـا فـي تركـيب الجمـلة 🔩 :** "
        elif input_str:
            error += f"\n⎈ ⦙   **هنـاك خطـا فـي تركـيب الجمـلة 🔩 :**"
        elif p_type is not None:
            for ty in p_type:
                if ty in Tnsmeet:
                    async for msg in cloneiq.client.iter_messages(cloneiq.chat_id, min_id=cloneiq.reply_to_msg_id - 1, filter=Tnsmeet[ty]):
                        count += 1
                        msgs.append(msg)
                        if len(msgs) == 50:
                            await cloneiq.client.delete_messages(chat, msgs)
                            msgs = []
                    if msgs:
                        await cloneiq.client.delete_messages(chat, msgs)
                else:
                    error += f"\n⎈ ⦙   `{ty}`  **هنـاك خطـا فـي تركـيب الجمـلة 🔩 :**"
        else:
            async for msg in cloneiq.client.iter_messages(chat, min_id=cloneiq.reply_to_msg_id - 1 ):
                count += 1
                msgs.append(msg)
                if len(msgs) == 50:
                    await cloneiq.client.delete_messages(chat, msgs)
                    msgs = []
            if msgs:
                await cloneiq.client.delete_messages(chat, msgs)
    elif p_type is not None and input_str:
        if p_type != "s" and input_str.isnumeric():
            for ty in p_type:
                if ty in Tnsmeet:
                    async for msg in cloneiq.client.iter_messages(cloneiq.chat_id, limit=int(input_str), filter=Tnsmeet[ty]):
                        count += 1
                        msgs.append(msg)
                        if len(msgs) == 50:
                            await cloneiq.client.delete_messages(chat, msgs)
                            msgs = []
                    if msgs:
                        await cloneiq.client.delete_messages(chat, msgs)
                elif ty == "s":
                    error += f"\n**⎈ ⦙   لا تستطـيع استـخدام امر التنظيف عبر البحث مع الاضافه 🔎**"
                else:
                    error += f"\n⎈ ⦙   `{ty}`  **هنـاك خطـا فـي تركـيب الجمـلة 🔩 :**"
        elif p_type == "s":
            try:
                cont, inputstr = input_str.split(" ")
            except ValueError:
                cont = "error"
                inputstr = input_str
            cont = cont.strip()
            inputstr = inputstr.strip()
            if cont.isnumeric():
                async for msg in cloneiq.client.iter_messages(cloneiq.chat_id, limit=int(cont), search=inputstr):
                    count += 1
                    msgs.append(msg)
                    if len(msgs) == 50:
                        await cloneiq.client.delete_messages(chat, msgs)
                        msgs = []
            else:
                async for msg in cloneiq.client.iter_messages(cloneiq.chat_id, search=input_str):
                    count += 1
                    msgs.append(msg)
                    if len(msgs) == 50:
                        await cloneiq.client.delete_messages(chat, msgs)
                        msgs = []
            if msgs:
                await cloneiq.client.delete_messages(chat, msgs)
        else:
            error += f"\n⎈ ⦙   `{ty}`  **هنـاك خطـا فـي تركـيب الجمـلة 🔩 :**"
    elif p_type is not None:
        for ty in p_type:
            if ty in Tnsmeet:
                async for msg in cloneiq.client.iter_messages(cloneiq.chat_id, filter=Tnsmeet[ty]
                ):
                    count += 1
                    msgs.append(msg)
                    if len(msgs) == 50:
                        await cloneiq.client.delete_messages(chat, msgs)
                        msgs = []
                if msgs:
                    await cloneiq.client.delete_messages(chat, msgs)
            elif ty == "s":
                error += f"\n**⎈ ⦙   لا تستطـيع استـخدام امر التنظيف عبر البحث مع الاضافه 🔎**"
            else:
                error += f"\n⎈ ⦙   `{ty}`  **هنـاك خطـا فـي تركـيب الجمـلة 🔩 :**"
    elif input_str.isnumeric():
        async for msg in cloneiq.client.iter_messages(chat, limit=int(input_str) + 1):
            count += 1
            msgs.append(msg)
            if len(msgs) == 50:
                await cloneiq.client.delete_messages(chat, msgs)
                msgs = []
        if msgs:
            await cloneiq.client.delete_messages(chat, msgs)
    else:
        error += "\n**⎈ ⦙   لم يتـم تحـديد الرسـالة أرسل  (.الاوامر ) و رؤية اوامر التنظيف  📌**"
    if msgs:
        await cloneiq.client.delete_messages(chat, msgs)
    if count > 0:
        result += "⎈ ⦙   تـم الأنتـهاء من التـنظيف السـريع  ✅  \n ⎈ ⦙   لقـد  تـم حـذف \n  ⎈ ⦙   عـدد  " + str(count) + " من الـرسائـل 🗑️"
    if error != "":
        result += f"\n\n**⎈ ⦙  عـذرا هنـاك خطـأ ❌:**{error}"
    if result == "":
        result += "**⎈ ⦙   لا تـوجد رسـائل لـتنظيفها ♻️**"
    hi = await cloneiq.client.send_message(cloneiq.chat_id, result)
    if BOTLOG:
        await cloneiq.client.send_message(BOTLOG_CHATID, f"**⎈ ⦙   حـذف الـرسائل 🗳️** \n{result}")
    await sleep(5)
    await hi.delete()
@iqthon.iq_cmd(incoming=True)
async def filter_incoming_handler(handler):  # sourcery no-metrics
    if handler.sender_id == handler.client.uid:
        return
    name = handler.raw_text
    filters = get_filters(handler.chat_id)
    if not filters:
        return
    a_user = await handler.get_sender()
    chat = await handler.get_chat()
    me = await handler.client.get_me()
    title = chat.title or "this chat"
    participants = await handler.client.get_participants(chat)
    count = len(participants)
    mention = f"[{a_user.first_name}](tg://user?id={a_user.id})"
    my_mention = f"[{me.first_name}](tg://user?id={me.id})"
    first = a_user.first_name
    last = a_user.last_name
    fullname = f"{first} {last}" if last else first
    username = f"@{a_user.username}" if a_user.username else mention
    userid = a_user.id
    my_first = me.first_name
    my_last = me.last_name
    my_fullname = f"{my_first} {my_last}" if my_last else my_first
    my_username = f"@{me.username}" if me.username else my_mention
    for trigger in filters:
        pattern = r"( |^|[^\w])" + re.escape(trigger.keyword) + r"( |$|[^\w])"
        if re.search(pattern, name, flags=re.IGNORECASE):
            if trigger.f_mesg_id:
                msg_o = await handler.client.get_messages(entity=BOTLOG_CHATID, ids=int(trigger.f_mesg_id))
                await handler.reply(msg_o.message.format(mention=mention, title=title, count=count, first=first, last=last, fullname=fullname, username=username, userid=userid,  my_first=my_first,  my_last=my_last, my_fullname=my_fullname,
                        my_username=my_username,                        my_mention=my_mention,                    ),
                    file=msg_o.media,)
            elif trigger.reply:
                await handler.reply(trigger.reply.format(mention=mention, title=title, count=count, first=first, last=last, fullname=fullname, username=username,
                        userid=userid, my_first=my_first,
                        my_last=my_last, my_fullname=my_fullname, my_username=my_username, my_mention=my_mention,                    ),                )
@iqthon.on(admin_cmd(pattern="لعب وهمي(?:\s|$)([\s\S]*)"))
async def _iq(iqthon):
    iq = iqthon.pattern_match.group(1)
    if not (iq or iq.isdigit()):
        iq = 100
    else:
        try:
            iq = int(iq)
        except BaseException:
            try:
                iq = await iqthon.ban_time(iq)
            except BaseException:
                return await event.edit("**اكتب الامر بشكل صحيح**")
    await iqthon.edit(f"**تم بدء وضع لعب وهمي لـ {iq} من الثوانـي**")
    async with iqthon.client.action(iqthon.chat_id, "game"):
        await asyncio.sleep(iq)  
@iqthon.iq_cmd(pattern="قرائه(?:\s|$)([\s\S]*)",)
async def ocriq(iqthonevent):
    iqqevent = await edit_or_reply(iqthonevent, "جاري قرائه الصوره ...")
    if not os.path.isdir(Config.TEMP_DIR):
        os.makedirs(Config.TEMP_DIR)
    lang_code = iqthonevent.pattern_match.group(1)
    downloaded_file_name = await iqthonevent.client.download_media(await iqthonevent.get_reply_message(), Config.TEMP_DIR)
    test_file = await ocr_iqthon(filename=downloaded_file_name, language=lang_code)
    try:
        ParsedText = test_file["ParsedResults"][0]["ParsedText"]
    except BaseException:
        await iqqevent.edit("**🆘 عـذرا لايمكنني القرائـة :**\n\nاذا تريد قرائة كلمات انكليزية\nقم بالرد على الصوره\nوأرسل أمر : ( `.قرائه eng` )\n-\nواذا تريد قرائة كلمات عربية\nقم بالرد على الصوره\nوأرسل أمر : ( `.قرائه ara` )\n\n- \n**يمكنك قرائة كلمات بلغات اخرى عبر وضع الكود رمزي للغه دولة**\n")
    else:
        await iqqevent.edit(f"**الموجود في الصوره هوه :** \n\n {ParsedText}")
    os.remove(downloaded_file_name)
@iqthon.on(admin_cmd(pattern="اضف رد ([\s\S]*)")) 
async def add_new_filter(new_handler):
    keyword = new_handler.pattern_match.group(1)
    string = new_handler.text.partition(keyword)[2]
    msg = await new_handler.get_reply_message()
    msg_id = None
    if msg and msg.media and not string:
        if BOTLOG:
            await new_handler.client.send_message(BOTLOG_CHATID, f"**⎈ ⦙   اضـافه ردّ ⎗ :** \n**⎈ ⦙  آيـدي الدردشـة 🆔 :** {new_handler.chat_id} \n**⎈ ⦙  آثـار ⌬ :** {keyword}\n\n**⎈ ⦙  تـم حفظ الرسـالة التاليـة ڪردّ على الكلمـة في الدردشـة، يرجـى عـدم حذفهـا ✻**")
            msg_o = await new_handler.client.forward_messages(entity=BOTLOG_CHATID, messages=msg, from_peer=new_handler.chat_id, silent=True)
            msg_id = msg_o.id
        else:
            await edit_or_reply(new_handler, "**⎈ ⦙   لحفـظ الوسائـط ڪرد يتوجـب تعييـن - PRIVATE_GROUP_BOT_API_ID. 💡**")
            return
    elif new_handler.reply_to_msg_id and not string:
        rep_msg = await new_handler.get_reply_message()
        string = rep_msg.text
    success = "**⎈ ⦙  تـم حفـظ الـرد {} بنجـاح ✓**"
    if add_filter(str(new_handler.chat_id), keyword, string, msg_id) is True:
        return await edit_or_reply(new_handler, success.format(keyword, "added"))
    remove_filter(str(new_handler.chat_id), keyword)
    if add_filter(str(new_handler.chat_id), keyword, string, msg_id) is True:
        return await edit_or_reply(new_handler, success.format(keyword, "Updated"))
    await edit_or_reply(new_handler, f"**⎈ ⦙   حـدث خطـأ عنـد تعييـن الـردّ ✕ :** {keyword}")
@iqthon.on(admin_cmd(pattern="موقع وهمي(?:\s|$)([\s\S]*)"))
async def _iq(iqthon):
    iq = iqthon.pattern_match.group(1)
    if not (iq or iq.isdigit()):
        iq = 100
    else:
        try:
            iq = int(iq)
        except BaseException:
            try:
                iq = await iqthon.ban_time(iq)
            except BaseException:
                return await event.edit("**اكتب الامر بشكل صحيح**")
    await iqthon.edit(f"**تم بدء وضع موقع وهمي لـ {iq} من الثوانـي**")
    async with iqthon.client.action(iqthon.chat_id, "location"):
        await asyncio.sleep(iq)
@iqthon.on(admin_cmd(pattern="جميع الردود(?: |$)(.*)"))    
async def on_snip_list(event):
    OUT_STR = "**⎈ ⦙  لايوجـد أيّ رد في هـذه الدردشـة  ✕**"
    filters = get_filters(event.chat_id)
    for filt in filters:
        if OUT_STR == "**⎈ ⦙   لايوجـد أيّ رد في هـذه الدردشـة  ✕**":
            OUT_STR = "**⎈ ⦙  الـردود المتوفـرة في هـذه الدردشـة ⎙ :** \n"
        OUT_STR += "▷  `{}`\n".format(filt.keyword)
    await edit_or_reply(event, OUT_STR, caption="**⎈ ⦙  الـردود المتاحـة في الدردشـة الحاليـة ⎙ **", file_name="filters.text")
Tnsmeet1 = {}
Tnsmeet1 = {"ا": InputMessagesFilterPhotos, "ل": InputMessagesFilterDocument, "ر": InputMessagesFilterUrl, "س": InputMessagesFilterEmpty, "ئ": InputMessagesFilterGif,"ج": InputMessagesFilterVideo,  "م": InputMessagesFilterMusic, "ي": InputMessagesFilterMyMentions, "ع": InputMessagesFilterGeo}
@iqthon.on(admin_cmd(pattern="مسح رد ([\s\S]*)")) 
async def remove_a_filter(r_handler):
    filt = r_handler.pattern_match.group(1)
    if not remove_filter(r_handler.chat_id, filt):
        await r_handler.edit("**⎈ ⦙   الـرد  {}  غيـر موجـود ❗️**".format(filt))
    else:
        await r_handler.edit("**⎈ ⦙  تـم حـذف الـردّ  {}  بنجـاح ✓**".format(filt))
@iqthon.on(admin_cmd(pattern="مسح جميع الردود(?: |$)(.*)"))    
async def on_all_snip_delete(event):
    filters = get_filters(event.chat_id)
    if filters:
        remove_all_filters(event.chat_id)
        await edit_or_reply(event, f"**⎈ ⦙  تـم حـذف ردود الدردشـة الحاليـة بنجـاح ✓**")
    else:
        await edit_or_reply(event, f"**⎈ ⦙  لايوجـد أيّ رد في هـذه المجموعـة ✕**")
@iqthon.on(admin_cmd(pattern="تكلم(?:\s|$)([\s\S]*)"))    
async def _(event):
    input_str = event.pattern_match.group(1)
    start = datetime.now()
    reply_to_id = await reply_id(event)
    if ";" in input_str:
        lan, text = input_str.split(";")
    elif event.reply_to_msg_id:
        previous_message = await event.get_reply_message()
        text = previous_message.message
        lan = input_str or "en"
    else:
        if not input_str:
            return await edit_or_reply(event, "**⎈ ⦙    عـذرا هـذا النص خـطأ **")
        text = input_str
        lan = "en"
    catevent = await edit_or_reply(event, "**⎈ ⦙   يـتم الـتسجيل أنتـظر **")
    text = deEmojify(text.strip())
    lan = lan.strip()
    if not os.path.isdir("./temp/"):
        os.makedirs("./temp/")
    required_file_name = "./temp/" + "voice.ogg"
    try:
        
        tts = gTTS(text, lang=lan)
        tts.save(required_file_name)
        command_to_execute = [
            "ffmpeg",
            "-i",
            required_file_name,
            "-map",
            "0:a",
            "-codec:a",
            "libopus",
            "-b:a",
            "100k",
            "-vbr",
            "on",
            required_file_name + ".opus",
        ]
        try:
            t_response = subprocess.check_output(command_to_execute, stderr=subprocess.STDOUT)
        except (subprocess.CalledProcessError, NameError, FileNotFoundError) as exc:
            await catevent.edit(str(exc))
        else:
            os.remove(required_file_name)
            required_file_name = required_file_name + ".opus"
        end = datetime.now()
        ms = (end - start).seconds
        await event.client.send_file(event.chat_id, required_file_name, reply_to=reply_to_id, allow_cache=False, voice_note=True)
        os.remove(required_file_name)
        await edit_delete(catevent, "**⎈ ⦙   النـص الـذي اخـترتـة  {} في هـذا البـصمة  خـلال 🔎 {} ثـانيـة 🔩".format(text[0:20], ms),)
    except Exception as e:
        await edit_or_reply(catevent, f"**⎈ ⦙   عـذرا هنـاك خطـأ هـوة 🚫 :**\n`{str(e)}`")
@iqthon.on(admin_cmd(pattern="تحذير تكرار(?:\s|$)([\s\S]*)"))
async def _(event):
    input_str = event.pattern_match.group(1)
    event = await edit_or_reply(event, "⎈ ⦙  جـاري تحديـث إعـدادات الـ كملها ↯")
    await asyncio.sleep(2)
    try:
        sql.set_flood(event.chat_id, input_str)
        sql.__load_flood_settings()
        await event.edit(f"⎈ ⦙  تم تحديـث تحذير تكرار إلى : {input_str} في الدردشـة الحاليـة ⌂")
    except Exception as e:
        await event.edit(str(e))
@iqthon.on(admin_cmd(pattern="ترجمه ([\s\S]*)"))
async def _(event):
    input_str = event.pattern_match.group(1)
    if event.reply_to_msg_id:
        previous_message = await event.get_reply_message()
        text = previous_message.message
        lan = input_str or "en"
    elif ";" in input_str:
        lan, text = input_str.split(";")
    else:
        return await edit_delete(event, "**⎈ ⦙   للترجمه يجـب الـرد على الرساله واكتب .ترجمه ar**", time=5)
    text = deEmojify(text.strip())
    lan = lan.strip()
    Translator()
    try:
        translated = await getTranslate(text, dest=lan)
        after_tr_text = translated.text
        output_str = f"**⎈ ⦙   تمت الترجمه مـن  :** {LANGUAGES[translated.src].title()}\n **⎈ ⦙   الـى ** {LANGUAGES[lan].title()} \n\n{after_tr_text}"
        await edit_or_reply(event, output_str)
    except Exception as exc:
        await edit_delete(event, f"**خـطأ:**\n`{str(exc)}`", time=5)
@iqthon.on(admin_cmd(pattern=f"{FOTOSECRET}(?: |$)(.*)"))    
async def iq(event):
  if not event.is_reply:
    return await event.edit('**يجـب عـليك الـرد عـلى صـورة ذاتيـة الـتدمير**')
  ogtah = await event.get_reply_message()
  pic = await ogtah.download_media()
  await bot.send_file('me', pic, caption=f"""**الصـورة الوقتيه ✅**\- So : @iqthon""")
  await event.delete()
@iqthon.on(admin_cmd(pattern="تاريخ الرساله(?: |$)(.*)"))    
async def _(event):
    reply = await event.get_reply_message()
    if reply:
        try:
            result = reply.fwd_from.date
        except Exception:
            result = reply.date
    else:
        result = event.date
    await edit_or_reply(event, f"**هذا تاريخ الرساله والوقت  👁‍🗨 :** `{yaml_format(result)}`")
@iqthon.on(admin_cmd(pattern="جهه اتصال وهمي(?:\s|$)([\s\S]*)"))
async def _iq(iqthon):
    iq = iqthon.pattern_match.group(1)
    if not (iq or iq.isdigit()):
        iq = 100
    else:
        try:
            iq = int(iq)
        except BaseException:
            try:
                iq = await iqthon.ban_time(iq)
            except BaseException:
                return await event.edit("**اكتب الامر بشكل صحيح**")
    await iqthon.edit(f"**تم بدء وضع جهه اتصال وهمي لـ {iq} من الثوانـي**")
    async with iqthon.client.action(iqthon.chat_id, "contact"):
        await asyncio.sleep(iq)  
@iqthon.on(admin_cmd(pattern="ماركدون(?:\s|$)([\s\S]*)"))    
async def _(event):
    reply_to_id = await reply_id(event)
    # soon will try to add media support
    reply_message = await event.get_reply_message()
    if reply_message:
        markdown_note = reply_message.text
    else:
        markdown_note = "".join(event.text.split(maxsplit=1)[1:])
    if not markdown_note:
        return await edit_delete(event, "**⎈ ⦙  مـا هـو النـص الـذي يجـب أن أستخدمـه ␦** : \n⎈ ⦙   أولا قـم بكتابه الامر وبجانبه الكلمه ورابط\n⎈ ⦙   كمثال 👇 :\n⎈ ⦙   `.ماركدون شفافية اهلا بك في كوكل [google]<buttonurl:https://www.google.com>`")
    catinput = "Inline buttons " + markdown_note
    results = await event.client.inline_query(Config.TG_BOT_USERNAME, catinput)
    await results[0].click(event.chat_id, reply_to=reply_to_id, hide_via=True)
    await event.delete()
@iqthon.on(admin_cmd(pattern="حذف(?:\s|$)([\s\S]*)"))
async def iq(cloneiq):  
    chat = await cloneiq.get_input_chat()
    msgs = []
    count = 0
    input_str = cloneiq.pattern_match.group(1)
    iqype = re.findall(r"\w+", input_str)
    try:
        p_type = iqype[0].replace("-", "")
        input_str = input_str.replace(iqype[0], "").strip()
    except IndexError:
        p_type = None
    error = ""
    result = ""
    await cloneiq.delete()
    reply = await cloneiq.get_reply_message()
    if reply:
        if input_str and input_str.isnumeric():
            if p_type is not None:
                for ty in p_type:
                    if ty in Tnsmeet1:
                        async for msg in cloneiq.client.iter_messages(cloneiq.chat_id, limit=int(input_str), offset_id=reply.id - 1, reverse=True, filter=Tnsmeet1[ty]):
                            count += 1
                            msgs.append(msg)
                            if len(msgs) == 50:
                                await cloneiq.client.delete_messages(chat, msgs)
                                msgs = []
                        if msgs:
                            await cloneiq.client.delete_messages(chat, msgs)
                    elif ty == "s":
                        error += f"\n**⎈ ⦙   هنـاك خطـا فـي تركـيب الجمـلة 🔩 :**"
                    else:
                        error += f"\n\n⎈ ⦙   `{ty}`  **هنـاك خطـا فـي تركـيب الجمـلة 🔩 :**"
            else:
                count += 1
                async for msg in cloneiq.client.iter_messages(cloneiq.chat_id, limit=(int(input_str) - 1), offset_id=reply.id, reverse=True):
                    msgs.append(msg)
                    count += 1
                    if len(msgs) == 50:
                        await cloneiq.client.delete_messages(chat, msgs)
                        msgs = []
                if msgs:
                    await cloneiq.client.delete_messages(chat, msgs)
        elif input_str and p_type is not None:
            if p_type == "s":
                try:
                    cont, inputstr = input_str.split(" ")
                except ValueError:
                    cont = "error"
                    inputstr = input_str
                cont = cont.strip()
                inputstr = inputstr.strip()
                if cont.isnumeric():
                    async for msg in cloneiq.client.iter_messages(cloneiq.chat_id, limit=int(cont), offset_id=reply.id - 1, reverse=True, search=inputstr):
                        count += 1
                        msgs.append(msg)
                        if len(msgs) == 50:
                            await cloneiq.client.delete_messages(chat, msgs)
                            msgs = []
                else:
                    async for msg in cloneiq.client.iter_messages(cloneiq.chat_id, offset_id=reply.id - 1, reverse=True, search=input_str):
                        count += 1
                        msgs.append(msg)
                        if len(msgs) == 50:
                            await cloneiq.client.delete_messages(chat, msgs)
                            msgs = []
                if msgs:
                    await cloneiq.client.delete_messages(chat, msgs)
            else:
                error += f"\n⎈ ⦙   `{ty}`  **هنـاك خطـا فـي تركـيب الجمـلة 🔩 :** "
        elif input_str:
            error += f"\n⎈ ⦙   **هنـاك خطـا فـي تركـيب الجمـلة 🔩 :**"
        elif p_type is not None:
            for ty in p_type:
                if ty in Tnsmeet1:
                    async for msg in cloneiq.client.iter_messages(cloneiq.chat_id, min_id=cloneiq.reply_to_msg_id - 1, filter=Tnsmeet1[ty]):
                        count += 1
                        msgs.append(msg)
                        if len(msgs) == 50:
                            await cloneiq.client.delete_messages(chat, msgs)
                            msgs = []
                    if msgs:
                        await cloneiq.client.delete_messages(chat, msgs)
                else:
                    error += f"\n⎈ ⦙   `{ty}`  **هنـاك خطـا فـي تركـيب الجمـلة 🔩 :**"
        else:
            async for msg in cloneiq.client.iter_messages(chat, min_id=cloneiq.reply_to_msg_id - 1 ):
                count += 1
                msgs.append(msg)
                if len(msgs) == 50:
                    await cloneiq.client.delete_messages(chat, msgs)
                    msgs = []
            if msgs:
                await cloneiq.client.delete_messages(chat, msgs)
    elif p_type is not None and input_str:
        if p_type != "s" and input_str.isnumeric():
            for ty in p_type:
                if ty in Tnsmeet1:
                    async for msg in cloneiq.client.iter_messages(cloneiq.chat_id, limit=int(input_str), filter=Tnsmeet1[ty]):
                        count += 1
                        msgs.append(msg)
                        if len(msgs) == 50:
                            await cloneiq.client.delete_messages(chat, msgs)
                            msgs = []
                    if msgs:
                        await cloneiq.client.delete_messages(chat, msgs)
                elif ty == "s":
                    error += f"\n**⎈ ⦙   لا تستطـيع استـخدام امر التنظيف عبر البحث مع الاضافه 🔎**"
                else:
                    error += f"\n⎈ ⦙   `{ty}`  **هنـاك خطـا فـي تركـيب الجمـلة 🔩 :**"
        elif p_type == "s":
            try:
                cont, inputstr = input_str.split(" ")
            except ValueError:
                cont = "error"
                inputstr = input_str
            cont = cont.strip()
            inputstr = inputstr.strip()
            if cont.isnumeric():
                async for msg in cloneiq.client.iter_messages(cloneiq.chat_id, limit=int(cont), search=inputstr):
                    count += 1
                    msgs.append(msg)
                    if len(msgs) == 50:
                        await cloneiq.client.delete_messages(chat, msgs)
                        msgs = []
            else:
                async for msg in cloneiq.client.iter_messages(cloneiq.chat_id, search=input_str):
                    count += 1
                    msgs.append(msg)
                    if len(msgs) == 50:
                        await cloneiq.client.delete_messages(chat, msgs)
                        msgs = []
            if msgs:
                await cloneiq.client.delete_messages(chat, msgs)
        else:
            error += f"\n⎈ ⦙   `{ty}`  **هنـاك خطـا فـي تركـيب الجمـلة 🔩 :**"
    elif p_type is not None:
        for ty in p_type:
            if ty in Tnsmeet1:
                async for msg in cloneiq.client.iter_messages(cloneiq.chat_id, filter=Tnsmeet1[ty]
                ):
                    count += 1
                    msgs.append(msg)
                    if len(msgs) == 50:
                        await cloneiq.client.delete_messages(chat, msgs)
                        msgs = []
                if msgs:
                    await cloneiq.client.delete_messages(chat, msgs)
            elif ty == "s":
                error += f"\n**⎈ ⦙   لا تستطـيع استـخدام امر التنظيف عبر البحث مع الاضافه 🔎**"
            else:
                error += f"\n⎈ ⦙   `{ty}`  **هنـاك خطـا فـي تركـيب الجمـلة 🔩 :**"
    elif input_str.isnumeric():
        async for msg in cloneiq.client.iter_messages(chat, limit=int(input_str) + 1):
            count += 1
            msgs.append(msg)
            if len(msgs) == 50:
                await cloneiq.client.delete_messages(chat, msgs)
                msgs = []
        if msgs:
            await cloneiq.client.delete_messages(chat, msgs)
    else:
        error += "\n**⎈ ⦙   لم يتـم تحـديد الرسـالة أرسل  (.الاوامر ) و رؤية اوامر التنظيف  📌**"
    if msgs:
        await cloneiq.client.delete_messages(chat, msgs)
    if count > 0:
        result += "⎈ ⦙   تـم الأنتـهاء من التـنظيف السـريع  ✅  \n ⎈ ⦙   لقـد  تـم حـذف \n  ⎈ ⦙   عـدد  " + str(count) + " من الـرسائـل 🗑️"
    if error != "":
        result += f"\n\n**⎈ ⦙  عـذرا هنـاك خطـأ ❌:**{error}"
    if result == "":
        result += "**⎈ ⦙   لا تـوجد رسـائل لـتنظيفها ♻️**"
    hi = await cloneiq.client.send_message(cloneiq.chat_id, result)
    if BOTLOG:
        await cloneiq.client.send_message(BOTLOG_CHATID, f"**⎈ ⦙   حـذف الـرسائل 🗳️** \n{result}")
    await sleep(5)
    await hi.delete()
@iqthon.on(admin_cmd(pattern="معرفات 100(?: |$)(.*)"))
async def iq(iqthon):
    mentions = iqthon.text[8:]
    chat = await iqthon.get_input_chat()
    async for x in iqthon.client.iter_participants(chat, 100):
        mentions += f" - @{x.username} ⦙ "
    await iqthon.client.send_message(iqthon.chat_id, mentions)
    await iqthon.delete()
@iqthon.on(admin_cmd(pattern="معرفات 200(?: |$)(.*)"))
async def iq(iqthon):
    mentions = iqthon.text[8:]
    chat = await iqthon.get_input_chat()
    async for x in iqthon.client.iter_participants(chat, 200):
        mentions += f" - @{x.username} ⦙ "
    await iqthon.client.send_message(iqthon.chat_id, mentions)
    await iqthon.delete()
@iqthon.on(admin_cmd(pattern="تاك 200(?: |$)(.*)"))
async def iq(iqthon):
    mentions = iqthon.text[8:]
    chat = await iqthon.get_input_chat()
    async for x in iqthon.client.iter_participants(chat, 200):
        mentions += f" \n⎈ ⦙ ⵧ〈[{x.first_name}](tg://user?id={x.id})〉"
    await iqthon.client.send_message(iqthon.chat_id, mentions)
    await iqthon.delete()
@iqthon.on(admin_cmd(pattern="تاك 150(?: |$)(.*)"))
async def iq(iqthon):
    mentions = iqthon.text[8:]
    chat = await iqthon.get_input_chat()
    async for x in iqthon.client.iter_participants(chat, 150):
        mentions += f" \n⎈ ⦙ ⵧ〈[{x.first_name}](tg://user?id={x.id})〉 \n"
    await iqthon.client.send_message(iqthon.chat_id, mentions)
    await iqthon.delete()
@iqthon.on(admin_cmd(pattern="تاك 100(?: |$)(.*)"))
async def iq(iqthon):
    mentions = iqthon.text[8:]
    chat = await iqthon.get_input_chat()
    async for x in iqthon.client.iter_participants(chat, 100):
        mentions += f" \n⎈ ⦙ ⵧ〈[{x.first_name}](tg://user?id={x.id})〉 \n"
    await iqthon.client.send_message(iqthon.chat_id, mentions)
    await iqthon.delete()
@iqthon.on(admin_cmd(pattern="تاك 50(?: |$)(.*)"))
async def iq(iqthon):
    mentions = iqthon.text[8:]
    chat = await iqthon.get_input_chat()
    async for x in iqthon.client.iter_participants(chat, 50):
        mentions += f" \n⎈ ⦙ ⵧ〈[{x.first_name}](tg://user?id={x.id})〉 \n"
    await iqthon.client.send_message(iqthon.chat_id, mentions)
    await iqthon.delete()
@iqthon.on(admin_cmd(pattern="تاك 10(?: |$)(.*)"))
async def iq(iqthon):
    mentions = iqthon.text[8:]
    chat = await iqthon.get_input_chat()
    async for x in iqthon.client.iter_participants(chat, 10):
        mentions += f" \n ⎈ ⦙ ⵧ〈[{x.first_name}](tg://user?id={x.id})〉 \n"
    await iqthon.client.send_message(iqthon.chat_id, mentions)
    await iqthon.delete()
@iqthon.on(admin_cmd(pattern="احسب ([\s\S]*)"))    
async def calculator(event):
    cmd = event.text.split(" ", maxsplit=1)[1]
    event = await edit_or_reply(event, "**⎈ ⦙   جـاري حسـاب المسـئلـة 📐**")
    old_stderr = sys.stderr
    old_stdout = sys.stdout
    redirected_output = sys.stdout = io.StringIO()
    redirected_error = sys.stderr = io.StringIO()
    stdout, stderr, exc = None, None, None
    san = f"print({cmd})"
    try:
        await aexec(san, event)
    except Exception:
        exc = traceback.format_exc()
    stdout = redirected_output.getvalue()
    stderr = redirected_error.getvalue()
    sys.stdout = old_stdout
    sys.stderr = old_stderr
    evaluation = ""
    if exc:
        evaluation = exc
    elif stderr:
        evaluation = stderr
    elif stdout:
        evaluation = stdout
    else:
        evaluation = "**⎈ ⦙   عـذار المسـئلة لااقـدر حلـها أو هنـاك خطـأ بتـرتيـب السـؤال 🆘**"
    final_output = "**⎈ ⦙   المسئلة **: `{}` \n **⎈ ⦙   الجواب **: `{}` \n".format(cmd, evaluation)
    await event.edit(final_output)

async def aexec(code, event):
    exec(f"async def __aexec(event): " + "".join(f"\n {l}" for l in code.split("\n")))
    return await locals()["__aexec"](event)
@iqthon.iq_cmd(pattern="(ازاله الخلفيه بالملصق|ازاله الخلفيه)(?:\s|$)([\s\S]*)",)
async def remove_iq(event):
    cmd = event.pattern_match.group(1)
    input_str = event.pattern_match.group(2)
    message_id = await reply_id(event)
    if event.reply_to_msg_id and not input_str:
        reply_message = await event.get_reply_message()
        catevent = await edit_or_reply(event, "`تحليل هذه الصورة / الملصق...`")
        file_name = os.path.join(Config.TEMP_DIR, "rmbg.png")
        try:
            await event.client.download_media(reply_message, file_name)
        except Exception as e:
            await edit_delete(catevent, f"`{str(e)}`", 5)
            return
        else:
            await catevent.edit("إزالة خلفية هذه الوسائط")
            file_name = convert_toimage(file_name)
            response = iqthonveFile(file_name)
            os.remove(file_name)
    elif input_str:
        catevent = await edit_or_reply(event, "إزالة خلفية هذه الوسائط")
        response = iqthonveURL(input_str)
    else:
        await edit_delete(event, "قم بالرد على أي صورة أو ملصق باستخدام rmbg / srmbg للحصول على خلفية أقل من ملف png أو تنسيق webp أو توفير رابط الصورة مع الأمر", 5)
        return
    contentType = response.headers.get("content-type")
    remove_bg_image = "iqthon.png"
    if "image" in contentType:
        with open("iqthon.png", "wb") as removed_bg_file:
            removed_bg_file.write(response.content)
    else:
        await edit_delete(catevent, f"`{response.content.decode('UTF-8')}`", 5)
        return
    if cmd == "ازاله الخلفيه بالملصق":
        file = convert_tosticker(remove_bg_image, filename="iqthon.webp")
        await event.client.send_file(event.chat_id,file,reply_to=message_id)
    else:
        file = remove_bg_image
        await event.client.send_file(event.chat_id,file,force_document=True,reply_to=message_id)
    await catevent.delete()
@iqthon.on(admin_cmd(pattern="ابلاغ الادمنيه(?: |$)(.*)"))    
async def iq(event):
    mentions = "@تاك للادمنيه : **⎈ ⦙  تم رصـد إزعـاج ⚠️**"
    chat = await event.get_input_chat()
    reply_to_id = await reply_id(event)
    async for x in event.client.iter_participants(chat, filter=ChannelParticipantsAdmins):
        if not x.bot:
            mentions += f"[\u2063](tg://user?id={x.id})"
    await event.client.send_message(event.chat_id, mentions, reply_to=reply_to_id)
    await event.delete()
@iqthon.iq_cmd(incoming=True, groups_only=True)
async def on_new_message(event):
    name = event.raw_text
    snips = sql1.get_chat_blacklist(event.chat_id)
    catadmin = await is_admin(event.client, event.chat_id, event.client.uid)
    if not catadmin:
        return
    for snip in snips:
        pattern = r"( |^|[^\w])" + re.escape(snip) + r"( |$|[^\w])"
        if re.search(pattern, name, flags=re.IGNORECASE):
            try:
                await event.delete()
            except Exception:
                await event.client.send_message(BOTLOG_CHATID, f"  ليس لدي إذن حذف\n {get_display_name(await event.get_chat())}.لأزاله الكلمات الممنوعه ")
                for word in snips:
                    sql1.rm_from_blacklist(event.chat_id, word.lower())
            break
@iqthon.on(admin_cmd(pattern="خط ملصق ?(?:(.*?) ?; )?([\s\S]*)"))    
async def sticklet(event):
    "your text as sticker"
    R = random.randint(0, 256)
    G = random.randint(0, 256)
    B = random.randint(0, 256)
    reply_to_id = await reply_id(event)
    font_file_name = event.pattern_match.group(1)
    if not font_file_name:
        font_file_name = ""
    sticktext = event.pattern_match.group(2)
    reply_message = await event.get_reply_message()
    if not sticktext:
        if event.reply_to_msg_id:
            sticktext = reply_message.message
        else:
            return await edit_or_reply(event, "need something, hmm")
    await event.delete()
    sticktext = deEmojify(sticktext)
    sticktext = textwrap.wrap(sticktext, width=10)
    sticktext = "\n".join(sticktext)
    image = Image.new("RGBA", (512, 512), (255, 255, 255, 0))
    draw = ImageDraw.Draw(image)
    fontsize = 230
    FONT_FILE = await get_font_file(event.client, "@catfonts", font_file_name)
    font = ImageFont.truetype(FONT_FILE, size=fontsize)
    while draw.multiline_textsize(sticktext, font=font) > (512, 512):
        fontsize -= 3
        font = ImageFont.truetype(FONT_FILE, size=fontsize)
    width, height = draw.multiline_textsize(sticktext, font=font)
    draw.multiline_text(        ((512 - width) / 2, (512 - height) / 2), sticktext, font=font, fill=(R, G, B)    )
    image_stream = io.BytesIO()
    image_stream.name = "iqthon.webp"
    image.save(image_stream, "WebP")
    image_stream.seek(0)
    await event.client.send_file(        event.chat_id,        image_stream,        caption="iqthon's Sticklet",        reply_to=reply_to_id,    )
    try:
        os.remove(FONT_FILE)
    except BaseException:
        pass
@iqthon.on(admin_cmd(pattern="ضفدع(?:\s|$)([\s\S]*)"))    
async def honk(event):
    "Make honk say anything."
    text = event.pattern_match.group(1)
    reply_to_id = await reply_id(event)
    bot_name = "@honka_says_bot"
    if not text:
        if event.is_reply:
            text = (await event.get_reply_message()).message
        else:
            return await edit_delete(                event, "__What is honk supposed to say? Give some text.__"            )
    text = deEmojify(text)
    await event.delete()
    await hide_inlinebot(event.client, bot_name, text, event.chat_id, reply_to_id)
@iqthon.on(admin_cmd(pattern="منع(?:\s|$)([\s\S]*)"))    
async def _(event):
    text = event.pattern_match.group(1)
    to_blacklist = list({trigger.strip() for trigger in text.split("\n") if trigger.strip()})

    for trigger in to_blacklist:
        sql1.add_to_blacklist(event.chat_id, trigger.lower())
    await edit_or_reply(event, "**⌔︙ تم اضافة {} الكلمة في قائمة المنع بنجاح ✅**".format(len(to_blacklist)),)
@iqthon.on(admin_cmd(pattern="الغاء منع(?:\s|$)([\s\S]*)"))    
async def _(event):
    text = event.pattern_match.group(1)
    to_unblacklist = list({trigger.strip() for trigger in text.split("\n") if trigger.strip()})
    successful = sum(
        bool(sql1.rm_from_blacklist(event.chat_id, trigger.lower()))
        for trigger in to_unblacklist)
    await edit_or_reply(event, f"تم حذف   {successful} / {len(to_unblacklist)} من قائمه المنع")
@iqthon.on(admin_cmd(pattern="قائمه المنع$"))    
async def _(event):
    all_blacklisted = sql1.get_chat_blacklist(event.chat_id)
    OUT_STR = "الكلمات الممنوعه هنا :\n"
    if len(all_blacklisted) > 0:
        for trigger in all_blacklisted:
            OUT_STR += f"👉 {trigger} \n"
    else:
        OUT_STR = "لم يتم العثور على كلمات ممنوعه . ابدأ في منع كلمات باستخدام `.منع + الكلمه`"
    await edit_or_reply(event, OUT_STR)
@iqthon.on(admin_cmd(pattern="مسح(\s*| \d+)$"))
async def iq(msg1):
    input_str = msg1.pattern_match.group(1).strip()
    iq_src = await msg1.get_reply_message()
    if iq_src:
        if input_str and input_str.isnumeric():
            await msg1.delete()
            await sleep(int(input_str))
            try:
                await iq_src.delete()
                if BOTLOG:
                    await msg1.client.send_message(BOTLOG_CHATID, "**⎈ ⦙   حـذف الـرسائل 🗳️  \n ⎈ ⦙   تـم حـذف الـرسالة بـنجاح ✅**")
            except rpcbaseerrors.BadRequestError:
                if BOTLOG:
                    await msg1.client.send_message(BOTLOG_CHATID, "**⎈ ⦙  عـذرا لايـمكن الـحذف بـدون  صلاحيـات ألاشـراف ⚜️**")
        elif input_str:
            if not input_str.startswith("var"):
                await edit_or_reply(msg1, "**⎈ ⦙   عـذرا الـرسالة غيـر موجـودة ❌**")
        else:
            try:
                await iq_src.delete()
                await msg1.delete()
                if BOTLOG:
                    await msg1.client.send_message(BOTLOG_CHATID, "**⎈ ⦙   حـذف الـرسائل 🗳️  \n ⎈ ⦙   تـم حـذف الـرسالة بـنجاح ✅**")
            except rpcbaseerrors.BadRequestError:
                await edit_or_reply(msg1, "**⎈ ⦙   عـذرا  لا استـطيع حـذف الرسـالة. ⁉️**")
    elif not input_str:
        await msg1.delete()
@iqthon.on(admin_cmd(pattern="تاك بالكلام ([\s\S]*)"))    
async def iq(event):
    user, input_str = await get_user_from_event(event)
    if not user:
        return
    reply_to_id = await reply_id(event)
    await event.delete()
    await event.client.send_message(event.chat_id, f"<a href='tg://user?id={user.id}'>{input_str}</a>", parse_mode="HTML", reply_to=reply_to_id)
async def get_font_file(client, channel_id, search_kw=""):
    font_file_message_s = await client.get_messages(        entity=channel_id,        filter=InputMessagesFilterDocument,                limit=None,        search=search_kw,    )
    font_file_message = random.choice(font_file_message_s)
    return await client.download_media(font_file_message)
@iqthon.on(admin_cmd(pattern="لافته(?:\s|$)([\s\S]*)"))    
async def waifu(animu):
    text = animu.pattern_match.group(1)
    reply_to_id = await reply_id(animu)
    if not text:
        if animu.is_reply:
            text = (await animu.get_reply_message()).message
        else:
            return await edit_or_reply(                animu, "`You haven't written any article, Waifu is going away.`"            )
    text = deEmojify(text)
    await animu.delete()
    await waifutxt(text, animu.chat_id, reply_to_id, animu.client)
@iqthon.on(admin_cmd(pattern="نسخ(?: |$)(.*)"))
async def iq(nshkh):
    if nshkh.fwd_from:
        return
    if nshkh.reply_to_msg_id:
        previous_message = await nshkh.get_reply_message()
        the_real_message = previous_message.text
        reply_to_id = nshkh.reply_to_msg_id
        the_real_message = the_real_message.replace("*", "*")
        the_real_message = the_real_message.replace("_", "_")
        await nshkh.edit(the_real_message)
    else:
        await nshkh.edit("**⎈ ⦙   قم  برد على الرساله ** ")
@iqthon.on(admin_cmd(pattern="غمق(?: |$)(.*)"))
async def iq(nshkh):
    if nshkh.fwd_from:
        return
    if nshkh.reply_to_msg_id:
        previous_message = await nshkh.get_reply_message()
        the_real_message = previous_message.text
        reply_to_id = nshkh.reply_to_msg_id
        the_real_message = the_real_message.replace("*", "*")
        the_real_message = the_real_message.replace("_", "_")
        await nshkh.edit(f"** {the_real_message} **")
    else:
        await nshkh.edit("**⎈ ⦙   قم  برد على الرساله ** ")
@iqthon.on(admin_cmd(pattern="ينسخ(?: |$)(.*)"))
async def iq(nshkh):
    if nshkh.fwd_from:
        return
    if nshkh.reply_to_msg_id:
        previous_message = await nshkh.get_reply_message()
        the_real_message = previous_message.text
        reply_to_id = nshkh.reply_to_msg_id
        the_real_message = the_real_message.replace("*", "*")
        the_real_message = the_real_message.replace("_", "_")
        await nshkh.edit(f"`{the_real_message}`")
    else:
        await nshkh.edit("**⎈ ⦙   قم  برد على الرساله ** ")
@iqthon.on(admin_cmd(pattern="خط سفلي(?: |$)(.*)"))
async def iq(nshkh):
    if nshkh.fwd_from:
        return
    if nshkh.reply_to_msg_id:
        previous_message = await nshkh.get_reply_message()
        the_real_message = previous_message.text
        reply_to_id = nshkh.reply_to_msg_id
        the_real_message = the_real_message.replace("*", "*")
        the_real_message = the_real_message.replace("_", "_")
        await nshkh.edit(f"-- --{the_real_message}-- --")
    else:
        await nshkh.edit("**⎈ ⦙   قم  برد على الرساله ** ")
