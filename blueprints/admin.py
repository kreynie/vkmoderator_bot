from vkbottle.user import Message, UserLabeler

from blueprints import rules
from config import legal_db, moderator_db
from helpfuncs import vkfunctions as vkf
from utils.exceptions import handle_errors_decorator

admin_labeler = UserLabeler()
admin_labeler.vbml_ignore_case = True
admin_labeler.custom_rules["access"] = rules.CheckPermissions


@admin_labeler.private_message(
    access=[rules.Groups.MODERATOR, rules.Rights.ADMIN],
    text=[
        "Права <user> <group> <value:int>",
        "Права <user> <group>",
        "Права <user>",
        "Права",
    ],
)
@handle_errors_decorator
async def change_rights(
    message: Message,
    user: str = "",
    group: str = "",
    value: int = 0,
) -> None:
    if not user or not group or not value:
        return await message.answer("Correct form: Права <user> <group> <value:int>")

    user_info = await vkf.get_user_info(user)

    match group:
        case "mod":
            code = await moderator_db.edit_user_allowance(user_info.id, value)
        case "legal":
            code = await legal_db.edit_user_allowance(user_info.id, value)
        case _:
            return await message.answer('use "mod" or "legal" group')

    if code:
        return await message.answer("Succeeded")
    await message.answer("Failed")
