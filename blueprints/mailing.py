from asyncio import sleep as asleep
from random import randint

from config import moderator_db
from helpfuncs.functions import async_list_generator
from vkbottle import VKAPIError
from vkbottle.user import Message, UserLabeler

from .rules import CheckPermissions, Groups, Rights

mailing_labeler = UserLabeler()
mailing_labeler.vbml_ignore_case = True
mailing_labeler.custom_rules["access"] = CheckPermissions


@mailing_labeler.private_message(
    access=[Groups.MODERATOR, Rights.MIDDLE],
    text="Рассылка <mail>",
)
async def mailing(message: Message, mail: str = None) -> None:
    moderators = await moderator_db.get_all()
    failed_mails = []
    await message.answer("Принял, обрабатываю...\nПосле рассылки сообщу результаты")
    await asleep(5)
    async for moderator in async_list_generator(moderators):
        try:
            if moderator["id"] != message.from_id:
                await message.ctx_api.messages.send(
                    moderator, randint(0, 10000), message=mail
                )
                await asleep(5)
        except VKAPIError as e:
            failed_mails.append(f"@id{moderator}\n")
            raise VKAPIError(f"Fail in mailing: {e.error_description}")
    msg = "Рассылка завершена!"
    if failed_mails != []:
        msg += f"\nНе удалось отправить следующим людям:\n" + "\n".join(
            f"@id{(user['id'] for user in failed_mails)}"
        )
    await message.answer(msg)
