from re import search

from vkbottle import VKAPIError
from vkbottle.user import Message, UserLabeler

from helpfuncs.jsonfunctions import JSONHandler

from .rules import CheckRights, Rights


lead_labeler = UserLabeler()
lead_labeler.vbml_ignore_case = True
lead_labeler.custom_rules["access"] = CheckRights
json_handler = JSONHandler()


@lead_labeler.private_message(access=Rights.lead, text="Минус <reason>")
async def match_incorrect_ban(message: Message, reason: str = ""):
    if message.attachments is None:
        await message.answer("Не найден пересланный пост")
        return
    if message.attachments[0].wall is None:
        await message.answer("Переслан не пост")
        return

    post_text = message.attachments[0].wall.text
    match_moderator_id = search(r".*((М|M)(В|B)\d+).*", post_text)
    if match_moderator_id is None:
        await message.answer("Не удалось найти МВ в тексте поста")
        return

    try:
        moderator_vk_id = json_handler.find_moderator_by_id(match_moderator_id.group(0))
        sender_info = await message.get_user()
        reason = f"⚠️ {sender_info.first_name} {sender_info.last_name} нашел ошибку в твоем бане.\nКомментарий: {reason}"
        await message.ctx_api.messages.send(int(moderator_vk_id), 0, message=reason)
    except VKAPIError:
        await message.answer("ВК не дал отправить сообщение модератору")
    except:
        await message.answer(
            "Возникла неизвестная ошибка при попытке отправить сообщение модератору\n"
            "Напиши @volonteersblitz с указанием времени попытки"
        )
        raise
