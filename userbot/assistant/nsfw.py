import re

from telethon import Button
from telethon.errors import MessageNotModifiedError
from telethon.events import CallbackQuery

from userbot import iqthon

from ..Config import Config
from ..core.logger import logging

LOGS = logging.getLogger(__name__)


@iqthon.tgbot.on(CallbackQuery(data=re.compile(r"^age_verification_true")))
async def age_verification_true(event: CallbackQuery):
    u_id = event.query.user_id
    if u_id != Config.OWNER_ID and u_id not in Config.SUDO_USERS:
        return await event.answer(
            "Given That It's A Stupid-Ass Decision, I've Elected To Ignore It.",
            alert=True,
        )
    await event.answer("Yes I'm 18+", alert=False)
    buttons = [
        Button.inline(
            text="Unsure / Change of Decision ❔",
            data="chg_of_decision_",
        )
    ]
    try:
        await event.edit(
            text="Set `ALLOW_NSFW` = True in Database Vars to access this plugin",
            file="https://telegra.ph/file/b0fc7897e7e090e8779a2.jpg",
            buttons=buttons,
        )
    except MessageNotModifiedError:
        pass


@iqthon.tgbot.on(CallbackQuery(data=re.compile(r"^age_verification_false")))
async def age_verification_false(event: CallbackQuery):
    u_id = event.query.user_id
    if u_id != Config.OWNER_ID and u_id not in Config.SUDO_USERS:
        return await event.answer(
            "Given That It's A Stupid-Ass Decision, I've Elected To Ignore It.",
            alert=True,
        )
    await event.answer("No I'm Not", alert=False)
    buttons = [
        Button.inline(
            text="Unsure / Change of Decision ❔",
            data="chg_of_decision_",
        )
    ]
    try:
        await event.edit(
            text="GO AWAY KID !",
            file="https://telegra.ph/file/b0fc7897e7e090e8779a2.jpg",
            buttons=buttons,
        )
    except MessageNotModifiedError:
        pass


@iqthon.tgbot.on(CallbackQuery(data=re.compile(r"^chg_of_decision_")))
async def chg_of_decision_(event: CallbackQuery):
    u_id = event.query.user_id
    if u_id != Config.OWNER_ID and u_id not in Config.SUDO_USERS:
        return await event.answer(
            "Given That It's A Stupid-Ass Decision, I've Elected To Ignore It.",
            alert=True,
        )
    await event.answer("Unsure", alert=False)
    buttons = [
        (
            Button.inline(text="Yes I'm 18+", data="age_verification_true"),
            Button.inline(text="No I'm Not", data="age_verification_false"),
        )
    ]
    try:
        await event.edit(
            text="**ARE YOU OLD ENOUGH FOR THIS ?**",
            file="https://telegra.ph/file/c4484ad9265d4491f1c01.jpg",
            buttons=buttons,
        )
    except MessageNotModifiedError:
        pass