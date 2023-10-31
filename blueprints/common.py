from vkbottle.user import Message, UserLabeler

from helpfuncs import VKHandler
from utils.exceptions import handle_errors_decorator
from .rules import CheckPermissions, Groups, Rights

common_labeler = UserLabeler()
common_labeler.vbml_ignore_case = True
common_labeler.custom_rules["access"] = CheckPermissions


@common_labeler.private_message(
    access=[Groups.ANY, Rights.LOW],
    text=[
        "пермлинк <target>",
        "пермлинк",
    ],
)
@handle_errors_decorator
async def get_permanent_link(message: Message, target: str = "") -> None:
    if not target:
        return await message.answer("Правильное использование: пермлинк <link>")
    object_info = await VKHandler.get_object_info(target)
    prefix = "club" if object_info.is_group else "id"
    await message.answer(f"https://vk.com/{prefix}{object_info.object.id}")
