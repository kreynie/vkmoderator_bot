from vkbottle.user import Message, UserLabeler

from helpfuncs.jsonfunctions import JSONHandler, DictionaryFuncs
from helpfuncs.vkfunctions import VKHandler

from .rules import Rights, Groups, CheckPermissions

ltl_labeler = UserLabeler()
ltl_labeler.vbml_ignore_case = True
ltl_labeler.custom_rules["access"] = CheckPermissions
json_handler = JSONHandler()
dict_handler = DictionaryFuncs()


@ltl_labeler.private_message(access=[Groups.LEGAL, Rights.LEAD], text="доблт <user_id>")
async def change_rights(message: Message, user_id: str, group: str, value: str) -> None:
    if user_id is None:
        await message.answer("Забыл ссылку на страницу!")
        return

    user_info = await VKHandler.get_user_info(user_id)
    if user_info == None:
        await message.answer("Ссылка на страницу должна быть полной и корректной")
        return

    data = json_handler.get_data()
    code, result = await dict_handler.edit_value(data, group, value)
    if code == "not_found":
        await message.answer("Не найден ключ")
    if code == "success":
        json_handler.save_data(result)
        await message.answer("Готово")
