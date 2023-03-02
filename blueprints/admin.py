from helpfuncs.jsonfunctions import DictionaryFuncs, JSONHandler
from helpfuncs.vkfunctions import VKHandler
from vkbottle.user import Message, UserLabeler

from .rules import CheckPermissions, Groups, Rights

admin_labeler = UserLabeler()
admin_labeler.vbml_ignore_case = True
admin_labeler.custom_rules["access"] = CheckPermissions
json_handler = JSONHandler()
dict_handler = DictionaryFuncs()


@admin_labeler.private_message(
    access=[Groups.MODERATOR, Rights.ADMIN], text="Права <user_id> <group> <value:int>"
)
async def change_rights(message: Message, user_id: str, group: str, value: int) -> None:
    if user_id is None:
        await message.answer("Забыл ссылку на страницу!")
        return

    user_info = await VKHandler.get_user_info(user_id)
    if user_info == None:
        await message.answer("Ссылка на страницу должна быть полной и корректной")
        return
    user_id = str(user_info["id"])

    data = json_handler.get_data()
    code, result = await dict_handler.edit_value(
        data[user_id],
        f"groups{DictionaryFuncs.separator}{group}",
        value,
    )
    if code == "not_found":
        await message.answer("Не найден ключ")
    if code == "success":
        data[user_id]["groups"] = result
        json_handler.save_data(data)
        await message.answer("Готово")
