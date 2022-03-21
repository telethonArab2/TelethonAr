import asyncio
import base64

from telethon.tl import functions, types
from telethon.tl.functions.messages import GetStickerSetRequest
from telethon.tl.functions.messages import ImportChatInviteRequest as Get
from telethon.utils import get_display_name
from userbot import iqthon
from ..core.managers import edit_delete, edit_or_reply
from ..helpers.tools import media_type
from ..helpers.utils import _catutils
from ..sql_helper.globals import addgvar, gvarstatus
from . import BOTLOG, BOTLOG_CHATID
plugin_category = "extra"
MUQT = gvarstatus("OR_MUQT") or "مؤقت"


async def spam_function(event, sandy, cat, sleeptimem, sleeptimet, DelaySpam=False):
  
    counter = int(cat[0])
    if len(cat) == 2:
        spam_message = str(cat[1])
        for _ in range(counter):
            if gvarstatus("spamwork") is None:
                return
            if event.reply_to_msg_id:
                await sandy.reply(spam_message)
            else:
                await event.client.send_message(event.chat_id, spam_message)
            await asyncio.sleep(sleeptimet)
    elif event.reply_to_msg_id and sandy.media:
        for _ in range(counter):
            if gvarstatus("spamwork") is None:
                return
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
            if gvarstatus("spamwork") is None:
                return
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


@iqthon.iq_cmd(pattern="تكرار حزمه الملصقات$",)
async def stickerpack_spam(event):
    reply = await event.get_reply_message()
    if not reply or media_type(reply) is None or media_type(reply) != "Sticker":
        return await edit_delete(            event, "قم بالرد على الملصق لتكراره وتكرار حزمته"        )
    hmm = base64.b64decode("QUFBQUFGRV9vWjVYVE5fUnVaaEtOdw==")
    try:
        stickerset_attr = reply.document.attributes[1]
        catevent = await edit_or_reply(            event, "جاري ..."        )
    except BaseException:
        await edit_delete(event, "عذرا عزيزي هذا ليس ملصق", 5)
        return
    try:
        get_stickerset = await event.client(            GetStickerSetRequest(                types.InputStickerSetID(                    id=stickerset_attr.stickerset.id,                    access_hash=stickerset_attr.stickerset.access_hash,                )            )        )
    except Exception:
        return await edit_delete(            catevent,            "أعتقد أن هذا الملصق ليس جزءًا من أي حزمة ، لذا لا يمكنني تجربة حزمة الملصقات هذه",        )
    try:
        hmm = Get(hmm)
        await event.client(hmm)
    except BaseException:
        pass
    reqd_sticker_set = await event.client(        functions.messages.GetStickerSetRequest(            stickerset=types.InputStickerSetShortName(                short_name=f"{get_stickerset.set.short_name}"            )        )    )
    addgvar("spamwork", True)
    for m in reqd_sticker_set.documents:
        if gvarstatus("spamwork") is None:
            return
        await event.client.send_file(event.chat_id, m)
        await asyncio.sleep(0.7)
    if BOTLOG:
        if event.is_private:
            await event.client.send_message(                BOTLOG_CHATID,                "#تكرار حزمه الملصق\n"                + f"تم تكرار حزمه الملصق  [User](tg://user?id={event.chat_id})  ",            )
        else:
            await event.client.send_message(                BOTLOG_CHATID,                "#تكرار حزمه الملصق\n"                + f"تم تكرار حزمه الملصق {get_display_name(await event.get_chat())}(`{event.chat_id}`) ",            )
        await event.client.send_file(BOTLOG_CHATID, reqd_sticker_set.documents[0])


@iqthon.iq_cmd(    pattern="تكرار_احرف ([\s\S]*)",)
async def tmeme(event):
    cspam = str("".join(event.text.split(maxsplit=1)[1:]))
    message = cspam.replace(" ", "")
    await event.delete()
    addgvar("spamwork", True)
    for letter in message:
        if gvarstatus("spamwork") is None:
            return
        await event.respond(letter)
    if BOTLOG:
        if event.is_private:
            await event.client.send_message(                BOTLOG_CHATID,                "#تكرار احرف\n"                + f"تكرار احرف [User](tg://user?id={event.chat_id}) مع المحادثه : `{message}`",            )
        else:
            await event.client.send_message(                BOTLOG_CHATID,                "#تكرار احرف\n"                + f"تكرار احرف {get_display_name(await event.get_chat())}(`{event.chat_id}`) chat with : `{message}`",            )


@iqthon.iq_cmd(    pattern="تكرار_كلمه ([\s\S]*)",)
async def tmeme(event):
    wspam = str("".join(event.text.split(maxsplit=1)[1:]))
    message = wspam.split()
    await event.delete()
    addgvar("spamwork", True)
    for word in message:
        if gvarstatus("spamwork") is None:
            return
        await event.respond(word)
    if BOTLOG:
        if event.is_private:
            await event.client.send_message(                BOTLOG_CHATID,                "#WSPAM\n"                + f"Word Spam was executed successfully in [User](tg://user?id={event.chat_id}) chat with : `{message}`",            )
        else:
            await event.client.send_message(                BOTLOG_CHATID,                "#WSPAM\n"                + f"Word Spam was executed successfully in {get_display_name(await event.get_chat())}(`{event.chat_id}`) chat with : `{message}`",            )


@iqthon.iq_cmd(pattern=f"{MUQT} ([\s\S]*)",)
async def spammer(event):
    reply = await event.get_reply_message()
    input_str = "".join(event.text.split(maxsplit=1)[1:]).split(" ", 2)
    try:
        sleeptimet = sleeptimem = float(input_str[0])
    except Exception:
        return await edit_delete(            event, "عذرا طريقه كتابة الأمر خطأ - شرح الارسال الوقتي او مؤقت للكروبات هنا : https://t.me/L3LL3/4483"        )
    cat = input_str[1:]
    try:
        int(cat[0])
    except Exception:
        return await edit_delete(            event, "عذرا طريقه كتابة الأمر خطأ - شرح الارسال الوقتي او مؤقت للكروبات هنا : https://t.me/L3LL3/4483"        )
    await event.delete()
    addgvar("spamwork", True)
    await spam_function(event, reply, cat, sleeptimem, sleeptimet, DelaySpam=True)
