from vkbottle.user import Message, UserLabeler

from config import legal_db, moderator_db
from helpfuncs import VKHandler
from utils.exceptions import handle_errors_decorator
from .rules import CheckPermissions, Groups, Rights

admin_labeler = UserLabeler()
admin_labeler.vbml_ignore_case = True
admin_labeler.custom_rules["access"] = CheckPermissions


@admin_labeler.private_message(
    access=[Groups.MODERATOR, Rights.ADMIN],
    text=[
        "Права <user> <group> <value:int>",
        "Права <user> <group>",
        "Права <user>",
        "Права",
    ],
)
@handle_errors_decorator
async def change_rights(
    message: Message, user: str = "", group: str = "", value: int = 0
) -> None:
    if not user or not group or not value:
        await message.answer("Correct form: Права <user> <group> <value:int>")
        return

    user_info = await VKHandler.get_user_info(user)

    match group:
        case "mod":
            code = await moderator_db.edit_user_allowance(user_info.id, value)
        case "legal":
            code = await legal_db.edit_user_allowance(user_info.id, value)
        case _:
            await message.answer('use "mod" or "legal" group')
            return

    if code:
        await message.answer("Succeeded")
    else:
        await message.answer("Failed")
