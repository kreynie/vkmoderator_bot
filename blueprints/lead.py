from re import search

from vkbottle import VKAPIError
from vkbottle.user import Message, UserLabeler

from helpfuncs.jsonfunctions import findModeratorByID

from .rules import CheckRights, Rights


lead_labeler = UserLabeler()
lead_labeler.vbml_ignore_case = True
lead_labeler.custom_rules["access"] = CheckRights


@lead_labeler.private_message(access=Rights.unit, text="Минус <reason>")
async def matchIncorrectBan(message: Message, reason: str = ""):
    if message.attachments is None:
        await message.answer("Не найден пересланный пост")
        return
    if message.attachments[0].wall is None:
        await message.answer("Переслан не пост")
        return

    postText = message.attachments[0].wall.text
    matchModeratorID = search(r".*((М|M)(В|B)\d+).*", postText)
    if matchModeratorID is None:
        await message.answer("Не удалось найти МВ в тексте поста")
        return

    try:
        moderatorVKID = await findModeratorByID(matchModeratorID.group(0))
        senderInfo = await message.get_user()
        reason = f"⚠️ {senderInfo.first_name} {senderInfo.last_name} нашел ошибку в твоем бане.\nКомментарий: {reason}"
        await message.ctx_api.messages.send(int(moderatorVKID), 0, message=reason)
    except VKAPIError:
        await message.answer("ВК не дал отправить сообщение модератору")
    except:
        await message.answer(
            "Возникла неизвестная ошибка при попытке отправить сообщение модератору\n"
            "Напиши @volonteersblitz с указанием времени попытки"
        )
        raise
