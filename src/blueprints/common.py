from vkbottle.user import Message

from src.blueprints import rules
from src.helpfuncs import vkfunctions as vkf
from src.helpfuncs.functions import split_for_text_for_command
from .base_labeler import labeler
from src.schemas import VKObjectInfo


@labeler.private_message(
    access=[rules.StuffGroups.ANY, rules.Rights.LOW],
    text=split_for_text_for_command("пермлинк <target>"),
)
async def get_permanent_link(message: Message, target: str = "") -> None:
    if not target:
        return await message.answer("Правильное использование: пермлинк <link>")
    object_info: VKObjectInfo = await vkf.get_object_info(target)
    prefix = "club" if object_info.is_group else "id"
    
    reply_object_info_text = "Объект является " + ("группой" if object_info.is_group else "человеком")
    reply_text = f"{reply_object_info_text}\n\nСсылка: https://vk.com/{prefix}{object_info.object.id}"
    return await message.answer(reply_text)
