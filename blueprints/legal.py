from vkbottle.user import Message, UserLabeler

from helpfuncs.jsonfunctions import DictionaryFuncs, JSONHandler

from .rules import CheckPermissions, Groups, Rights

lt_labeler = UserLabeler()
lt_labeler.vbml_ignore_case = True
lt_labeler.custom_rules["access"] = CheckPermissions
json_handler = JSONHandler()
dict_handler = DictionaryFuncs()


@lt_labeler.private_message(
    access=[Groups.LEGAL, Rights.LOW],
    text="ЛТ <public> <user> <reason> <post> <game>",
)
async def legal_helper(message: Message) -> None:
    await message.answer("Пока ничего нет")
