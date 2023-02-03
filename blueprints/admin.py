from vkbottle.user import Message, UserLabeler

from helpfuncs.jsonfunctions import editValues
from helpfuncs.vkfunctions import getUserInfo

from .rules import CheckRights, Rights

admin_labeler = UserLabeler()
admin_labeler.vbml_ignore_case = True
admin_labeler.custom_rules["access"] = CheckRights


@admin_labeler.private_message(access=Rights.admin, text="Права <user_id> <rights:int>")
async def change_rights(message: Message, user_id: str = None, rights: int = 1):
    if user_id is None:
        await message.answer("Забыл ссылку на страницу!")
        return

    user_info = await getUserInfo(user_id)
    if user_info == None:
        await message.answer("Ссылка на страницу должна быть полной и корректной")
        return

    result = await editValues(str(user_info["id"]), "rights", rights)
    if result == "notExists":
        await message.answer("Не найден ключ")
    if result == "success":
        await message.answer("Готово")
