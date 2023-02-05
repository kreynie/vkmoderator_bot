from asyncio import sleep as asleep
from random import randint

from vkbottle import VKAPIError
from vkbottle.user import Message, UserLabeler

from helpfuncs.functions import asyncListGenerator
from helpfuncs.jsonfunctions import getData

from .rules import CheckRights, Rights

mailing_labeler = UserLabeler()
mailing_labeler.vbml_ignore_case = True
mailing_labeler.custom_rules["access"] = CheckRights


@mailing_labeler.private_message(access=Rights.supermoderator, text="Рассылка <mail>")
async def mailing(message: Message, mail: str = None):
    moderators = await getData()
    failedList = []
    async for moderator in asyncListGenerator(moderators["moderators"]):
        try:
            await message.ctx_api.messages.send(
                int(moderator), randint(0, 10000), message=mail
            )
            await asleep(5)
        except VKAPIError as e:
            failedList.append(f"@id{moderator}\n")
            raise VKAPIError(f"Fail in mailing: {e.error_description}")
    msg = "Рассылка завершена!"
    if failedList != []:
        msg += f"\nНе удалось отправить следующим людям:\n" + "".join(failedList)
    await message.answer(msg)
