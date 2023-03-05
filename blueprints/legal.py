from vkbottle.user import Message, UserLabeler

from .rules import CheckPermissions, Groups, Rights

lt_labeler = UserLabeler()
lt_labeler.vbml_ignore_case = True
lt_labeler.custom_rules["access"] = CheckPermissions


@lt_labeler.private_message(
    access=[Groups.LEGAL, Rights.LOW],
    text="ЛТ <link> <reason> <post> <game>",
)
async def legal_helper(
    message: Message,
    link: str = None,
    reason: str = None,
    post: str = None,
    game: str = None,
) -> None:
    await message.answer("Пока ничего нет")
