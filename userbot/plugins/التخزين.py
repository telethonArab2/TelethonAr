import asyncio
import base64
import io
import os
from pathlib import Path
from ShazamAPI import Shazam
from telethon.tl import functions, types
from telethon.errors.rpcerrorlist import YouBlockedUserError
from telethon.tl.functions.messages import GetStickerSetRequest
from telethon.tl.functions.messages import ImportChatInviteRequest as Get
from telethon.utils import get_display_name
from validators.url import url

from userbot import iqthon

from ..core.logger import logging
from ..core.managers import edit_delete, edit_or_reply
from ..helpers.tools import media_type
from ..helpers.functions import name_dl, song_dl, video_dl, yt_search
from ..helpers.utils import _catutils, reply_id
from . import BOTLOG, BOTLOG_CHATID

LOGS = logging.getLogger(__name__)
SONG_SEARCH_STRING = "⌔︙جاري البحث عن الاغنية إنتظر رجاءًا  🎧"
SONG_NOT_FOUND = "⌔︙لم أستطع إيجاد هذه الأغنية  ⚠️"
SONG_SENDING_STRING = "⌔︙قم بإلغاء حظر البوت  🚫"


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
                    await event.client.send_message(BOTLOG_CHATID, "**⎈ ⦙ التڪـرار  ♽**\n" + f"**⌔︙ تم تنفيذ التكرار بنجاح في ▷** [User](tg://user?id={event.chat_id}) **الدردشـة مـع** {counter} **عدد المرات مع الرسالة أدناه**")
                else:
                    await event.client.send_message(BOTLOG_CHATID, "**⎈ ⦙ التڪـرار  ♽**\n" + f"**⌔︙ تم تنفيذ التكرار بنجاح في ▷** {get_display_name(await event.get_chat())}(`{event.chat_id}`) **مـع** {counter} **عدد المرات مع الرسالة أدناه**")
            elif event.is_private:
                await event.client.send_message(BOTLOG_CHATID, "**⎈ ⦙ التكرار الوقتي 💢**\n" + f"**⌔︙ تم تنفيذ التكرار الوقتي  بنجاح في ▷** [User](tg://user?id={event.chat_id}) **الدردشـة مـع** {counter} **عدد المرات مع الرسالة أدناه مع التأخير** {sleeptimet} ** الثوانـي ⏱**")
            else:
                await event.client.send_message(BOTLOG_CHATID, "**⎈ ⦙ التكرار الوقتي 💢**\n" + f"**⌔︙ تم تنفيذ التكرار الوقتي  بنجاح في ▷** {get_display_name(await event.get_chat())}(`{event.chat_id}`) **مـع** {counter} **عدد المرات مع الرسالة أدناه مع التأخير** {sleeptimet} ** الثوانـي ⏱**")

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
                await event.client.send_message(BOTLOG_CHATID, "**⎈ ⦙ التڪـرار  ♽**\n" + f"**⌔︙ تم تنفيذ التكرار بنجاح في ▷** [User](tg://user?id={event.chat_id}) **الدردشـة مـع** {counter} **رسائـل الـ  ✉️ :** \n" + f"⌔︙ `{spam_message}`")
            else:
                await event.client.send_message(
                    BOTLOG_CHATID,
                    "**⎈ ⦙ التڪـرار  ♽**\n"
                    + f"**⎈ ⦙ تم تنفيذ التكرار بنجاح في ▷** {get_display_name(await event.get_chat())}(`{event.chat_id}`) **الدردشـة مـع** {counter} **رسائـل الـ  ✉️ :** \n"
                    + f"⎈ ⦙ `{spam_message}`",
                )
    elif BOTLOG:
        if event.is_private:
            await event.client.send_message(
                BOTLOG_CHATID,
                "**⎈ ⦙ التكرار الوقتي 💢**\n"
                + f"**⎈ ⦙ تم تنفيذ التكرار الوقتي  بنجاح في ▷** [User](tg://user?id={event.chat_id}) **الدردشـة مـع** {sleeptimet} seconds and with {counter} **رسائـل الـ  ✉️ :** \n"
                + f"⎈ ⦙ `{spam_message}`",
            )
        else:
            await event.client.send_message(
                BOTLOG_CHATID,
                "**⎈ ⦙ التكرار الوقتي 💢**\n"
                + f"**⎈ ⦙ تم تنفيذ التكرار الوقتي  بنجاح في ▷** {get_display_name(await event.get_chat())}(`{event.chat_id}`) **الدردشـة مـع** {sleeptimet} **الثوانـي و مـع** {counter} **رسائـل الـ  ✉️ :** \n"
                + f"⎈ ⦙ `{spam_message}`",
            )

@iqthon.on(admin_cmd(pattern="بحث صوت(320)?(?: |$)(.*)"))    
async def _(event):
    reply_to_id = await reply_id(event)
    reply = await event.get_reply_message()
    if event.pattern_match.group(2):
        query = event.pattern_match.group(2)
    elif reply:
        if reply.message:
            query = reply.message
    else:
        return await edit_or_reply(event, "**⎈ ⦙ ما الذي تريد أن أبحث عنه  ⁉️**")
    cat = base64.b64decode("QUFBQUFGRV9vWjVYVE5fUnVaaEtOdw==")
    catevent = await edit_or_reply(event, "**⎈ ⦙ جاري تحميل الأغنية إنتظر قليلا  ⏳**")
    video_link = await yt_search(str(query))
    if not url(video_link):
        return await catevent.edit(f"**⎈ ⦙ عـذرًا لم أستطع إيجاد الأغنية أو الفيديو لـ  ❌** `{query}`")
    cmd = event.pattern_match.group(1)
    q = "320k" if cmd == "320" else "128k"
    song_cmd = song_dl.format(QUALITY=q, video_link=video_link)
    # thumb_cmd = thumb_dl.format(video_link=video_link)
    name_cmd = name_dl.format(video_link=video_link)
    try:
        cat = Get(cat)
        await event.client(cat)
    except BaseException:
        pass
    stderr = (await _catutils.runcmd(song_cmd))[1]
    if stderr:
        return await catevent.edit(f"**⎈ ⦙  خـطأ  ⚠️ :** `{stderr}`")
    catname, stderr = (await _catutils.runcmd(name_cmd))[:2]
    if stderr:
        return await catevent.edit(f"**⎈ ⦙  خـطأ  ⚠️ :** `{stderr}`")
    catname = os.path.splitext(catname)[0]
    song_file = Path(f"{catname}.mp3")
    if not os.path.exists(song_file):
        return await catevent.edit(f"**⎈ ⦙ عـذرًا لم أستطع إيجاد الأغنية أو الفيديو لـ  ❌** `{query}`")
    await catevent.edit("**⎈ ⦙ لقد وجدت الاغنية إنتظر قليلا  ⏱**")
    catthumb = Path(f"{catname}.jpg")
    if not os.path.exists(catthumb):
        catthumb = Path(f"{catname}.webp")
    elif not os.path.exists(catthumb):
        catthumb = None

    await event.client.send_file(event.chat_id,
        song_file,
        force_document=False,
        caption=query,
        thumb=catthumb,
        supports_streaming=True,
        reply_to=reply_to_id,
    )
    await catevent.delete()
    for files in (catthumb, song_file):
        if files and os.path.exists(files):
            os.remove(files)
async def delete_messages(event, chat, from_message):
    itermsg = event.client.iter_messages(chat, min_id=from_message.id)
    msgs = [from_message.id]
    async for i in itermsg:
        msgs.append(i.id)
    await event.client.delete_messages(chat, msgs)
    await event.client.send_read_acknowledge(chat)
@iqthon.on(admin_cmd(pattern="بحث فيديو(?: |$)(.*)"))    
async def _(event):
    reply_to_id = await reply_id(event)
    reply = await event.get_reply_message()
    if event.pattern_match.group(1):
        query = event.pattern_match.group(1)
    elif reply:
        if reply.message:
            query = reply.messag
    else:
        return await edit_or_reply(event, "**⎈ ⦙ قم بوضع الأمر وبجانبه إسم الأغنية  🖇**")
    cat = base64.b64decode("QUFBQUFGRV9vWjVYVE5fUnVaaEtOdw==")
    catevent = await edit_or_reply(event, "**⌔︙لقد وجدت الفيديو المطلوب إنتظر قليلا  ⏱ ...**")
    video_link = await yt_search(str(query))
    if not url(video_link):
        return await catevent.edit(f"**⎈ ⦙  عـذرًا لم أستطع إيجاد أي فيديو او صوت متعلق بـ ❌** `{query}`")
    name_cmd = name_dl.format(video_link=video_link)
    video_cmd = video_dl.format(video_link=video_link)
    stderr = (await _catutils.runcmd(video_cmd))[1]
    if stderr:
        return await catevent.edit(f"**⎈ ⦙  خـطأ  ⚠️ :** `{stderr}`")
    catname, stderr = (await _catutils.runcmd(name_cmd))[:2]
    if stderr:
        return await catevent.edit(f"**⎈ ⦙  خـطأ  ⚠️ :** `{stderr}`")
    try:
        cat = Get(cat)
        await event.client(cat)
    except BaseException:
        pass
    catname = os.path.splitext(catname)[0]
    vsong_file = Path(f"{catname}.mp4")
    if not os.path.exists(vsong_file):
        vsong_file = Path(f"{catname}.mkv")
    elif not os.path.exists(vsong_file):
        return await catevent.edit(f"**⎈ ⦙  عـذرًا لم أستطع إيجاد أي فيديو او صوت متعلق بـ ❌** `{query}`")
    await catevent.edit("**⎈ ⦙ لقد وجدت الفديو المطلوب انتظر قليلا  ⏳**")
    catthumb = Path(f"{catname}.jpg")
    if not os.path.exists(catthumb):
        catthumb = Path(f"{catname}.webp")
    elif not os.path.exists(catthumb):
        catthumb = None
    await event.client.send_file(
        event.chat_id,
        vsong_file,
        force_document=False,
        caption=query,
        thumb=catthumb,
        supports_streaming=True,
        reply_to=reply_to_id,
    )
    await catevent.delete()
    for files in (catthumb, vsong_file):
        if files and os.path.exists(files):
            os.remove(files)

