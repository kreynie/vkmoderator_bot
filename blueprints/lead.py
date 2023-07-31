from re import match

from config import moderator_db
from vkbottle import VKAPIError
from vkbottle.user import Message, UserLabeler

from .rules import CheckPermissions, Groups, Rights

lead_labeler = UserLabeler()
lead_labeler.vbml_ignore_case = True
lead_labeler.custom_rules["access"] = CheckPermissions


@lead_labeler.private_message(
    access=[Groups.MODERATOR, Rights.LEAD],
    text="Минус <reason>",
)
async def match_incorrect_ban(message: Message, reason: str = "") -> None:
    if message.attachments is None:
        await message.answer("Не найден пересланный пост")
        return
    if message.attachments[0].wall is None:
        await message.answer("Переслан не пост")
        return

    post_text = message.attachments[0].wall.text
    match_moderator_id = match(r".*[мМM][вВB](\d+).*", post_text)
    if match_moderator_id is None:
        await message.answer("Не удалось найти МВ в тексте поста")
        return
    moderator_id = int(match_moderator_id.group(1))
    if not await moderator_db.has_user(moderator_id):
        await message.answer("Модератора нет в действующем списке")
    try:
        sender_info = await moderator_db.get_user_by_id(message.from_id)
        text = f"⚠️ {sender_info.full_name} нашел ошибку в твоем бане. \nКомментарий: {reason}"
        await message.ctx_api.messages.send(moderator_id, 0, message=text)
    except VKAPIError:
        await message.answer("ВК не дал отправить сообщение модератору")
