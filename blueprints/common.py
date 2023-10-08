from helpfuncs import VKHandler
from vkbottle.user import Message, UserLabeler

from utils.exceptions import InformationReError, InformationRequestError
from .rules import CheckPermissions, Groups, Rights

common_labeler = UserLabeler()
common_labeler.vbml_ignore_case = True
common_labeler.custom_rules["access"] = CheckPermissions


@common_labeler.private_message(access=[Groups.ANY, Rights.LOW], text="пермлинк <user>")
async def get_user_permanent_link(message: Message, user: str) -> None:
    if not user:
        await message.answer("Забыл юзера")

    try:
        user_info = await VKHandler.get_user_info(user)
    except InformationReError:
        await message.answer("Ссылка на страницу должна быть полной и корректной")
        return
    except InformationRequestError:
        await message.answer("Не удалось найти информацию о пользователе по ссылке")
        return
    await message.answer(f"https://vk.com/id{user_info.id}")
