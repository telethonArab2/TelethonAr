import html
from userbot import iqthon
from ..core.managers import edit_or_reply
from ..sql_helper import warns_sql as sql
@iqthon.on(admin_cmd(pattern="تحذير(?:\s|$)([\s\S]*)"))
async def _(event):
    warn_reason = event.pattern_match.group(1)
    if not warn_reason:
        warn_reason = "لايوجد سبب"
    reply_message = await event.get_reply_message()
    limit, soft_warn = sql.get_warn_setting(event.chat_id)
    num_warns, reasons = sql.warn_user(reply_message.sender_id, event.chat_id, warn_reason)
    if num_warns >= limit:
        sql.reset_warns(reply_message.sender_id, event.chat_id)
        if soft_warn:
            logger.info("TODO: kick user")
            reply = "**{} تحذيرات : [user](tg://user?id={}) هذا الشخص مطرود الان**".format(limit, reply_message.sender_id)
        else:
            logger.info("TODO: ban user")
            reply = "**{} تحذيرات : [user](tg://user?id={}) تم طرد الشخص **".format(limit, reply_message.sender_id)
    else:
        reply = "** [user](tg://user?id={}) هذا  {}/{} تحذير ؟ ... سوف تنطرد **".format(reply_message.sender_id, num_warns, limit)
        if warn_reason:
            reply += "\nسبب التحذير :\n{}".format(html.escape(warn_reason))
    await edit_or_reply(event, reply)
@iqthon.on(admin_cmd(pattern="عدد التحذيرات"))
async def _(event):
    reply_message = await event.get_reply_message()
    result = sql.get_warns(reply_message.sender_id, event.chat_id)
    if not result or result[0] == 0:
        return await edit_or_reply(event, "** هذا المستخدم ليس لديه أي تحذيرات **")
    num_warns, reasons = result
    limit, soft_warn = sql.get_warn_setting(event.chat_id)
    if not reasons:
        return await edit_or_reply(event,"** هذا المستخدم لديه : {} / {} تحذير ، ولكن لا توجد أسباب لأي منهم. **".format(num_warns, limit),)

    text = "** هذا المستخدم لديه : {}/{} تحذيرات للأسباب التالية : **".format(num_warns, limit)
    text += "\r\n"
    text += reasons
    await event.edit(text)
@iqthon.on(admin_cmd(pattern="ا(عاده)?التحذيرات$"))
async def _(event):
    reply_message = await event.get_reply_message()
    sql.reset_warns(reply_message.sender_id, event.chat_id)
    await edit_or_reply(event, "** تمت إعادة ضبط التحذيرات**")
#
