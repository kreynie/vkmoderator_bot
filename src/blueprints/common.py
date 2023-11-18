from vkbottle.user import Message

from src.blueprints import rules
from src.helpfuncs import vkfunctions as vkf
from src.helpfuncs.functions import split_for_text_for_command
from src.utils.exceptions import handle_errors_decorator
from .base_labeler import labeler


@labeler.private_message(
    access=[rules.StuffGroups.ANY, rules.Rights.LOW],
    text=split_for_text_for_command("пермлинк <target>"),
)
@handle_errors_decorator()
async def get_permanent_link(message: Message, target: str = "") -> None:
    if not target:
        return await message.answer("Правильное использование: пермлинк <link>")
    object_info = await vkf.get_object_info(target)
    prefix = "club" if object_info.is_group else "id"
    await message.answer(f"https://vk.com/{prefix}{object_info.object.id}")
