from asyncio import sleep as asleep

from config import moderator_db
from helpfuncs import VKHandler
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
        if moderator.id == message.from_id or moderator.allowance >= 3:
            continue

        try:
            await VKHandler.send_message(
                user_id=moderator.id,
                message=mail,
            )
            await asleep(5)
        except VKAPIError:
            failed_mails.append(f"@id{moderator.id} ({moderator.full_name})")
    msg = "Рассылка завершена!"
    if failed_mails:
        msg += "\nНе удалось отправить:\n" + "\n".join(failed_mails)
    await message.answer(msg)
