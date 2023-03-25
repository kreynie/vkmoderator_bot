from helpfuncs import VKHandler
from vkbottle.user import Message, UserLabeler

from .rules import CheckPermissions, Groups, Rights

common_labeler = UserLabeler()
common_labeler.vbml_ignore_case = True
common_labeler.custom_rules["access"] = CheckPermissions


@common_labeler.private_message(access=[Groups.ANY, Rights.LOW], text="пермлинк <user>")
async def get_user_permlink(message: Message, user: str) -> None:
    if not user:
        await message.answer("Забыл юзера")

    _, object_info = await VKHandler.get_object_info(user)
    if object_info is None:
        await message.answer("Невозможно получить информацию по ссылке")
        return
    await message.answer(f"https://vk.com/id{object_info.id}")
