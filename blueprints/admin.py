from config import legal_db, moderator_db
from helpfuncs.vkfunctions import VKHandler
from vkbottle.user import Message, UserLabeler

from .rules import CheckPermissions, Groups, Rights

admin_labeler = UserLabeler()
admin_labeler.vbml_ignore_case = True
admin_labeler.custom_rules["access"] = CheckPermissions


@admin_labeler.private_message(
    access=[Groups.MODERATOR, Rights.ADMIN],
    text="Права <user_id> <group> <value:int>",
)
async def change_rights(message: Message, user_id: str, group: str, value: int) -> None:
    if user_id is None:
        await message.answer("Забыл ссылку на страницу!")
        return

    user_info = await VKHandler.get_user_info(user_id)
    if user_info == None:
        await message.answer("Ссылка на страницу должна быть полной и корректной")
        return
    user_id = user_info["id"]

    match group:
        case "mod":
            code = await moderator_db.edit_user_allowance(user_id, value)
        case "legal":
            code = await legal_db.edit_user_allowance(user_id, value)
        case _:
            await message.answer('use "mod" or "legal" group')
            return

    if code:
        await message.answer("Succeeded")
    else:
        await message.answer("Failed")
