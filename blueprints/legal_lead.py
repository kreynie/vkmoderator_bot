from config import legal_db, users_db
from helpfuncs.functions import ReformatHandler
from helpfuncs.vkfunctions import VKHandler
from vkbottle.user import Message, UserLabeler

from .rules import CheckPermissions, Groups, Rights

ltl_labeler = UserLabeler()
ltl_labeler.vbml_ignore_case = True
ltl_labeler.custom_rules["access"] = CheckPermissions


@ltl_labeler.private_message(
    access=[Groups.LEGAL, Rights.LEAD],
    text="ДобЛТ <user> <legal_id:int>",
)
async def add_legal(message: Message, user: str, legal_id: int) -> None:
    if user is None:
        await message.answer("Забыл ссылку на страницу!")
        return
    if legal_id is None:
        await message.answer("Забыл айдишник")

    user_info = await VKHandler.get_user_info(user)
    if user_info is None:
        await message.answer("Ссылка на страницу должна быть полной и корректной")
        return

    if await legal_db.has_user(user_info.id):
        await message.answer("Уже есть в списке")
        return

    if not await users_db.has_user(user_info.id):
        await users_db.add_user(
            user_info.id,
            user_info.first_name,
            user_info.last_name,
        )

    code = await legal_db.add_user(user_info.id, legal_id, 1)
    if code:
        await message.answer("Добавлен")
    else:
        await message.answer("Что-то пошло не так")


@ltl_labeler.private_message(
    access=[Groups.LEGAL, Rights.LEAD],
    text="УдалЛТ <user>",
)
async def remove_legal(message: Message, user: str) -> None:
    if user is None:
        await message.answer("Забыл ссылку на страницу!")
        return

    user_info = await VKHandler.get_user_info(user)
    if user_info is None:
        await message.answer("Ссылка на страницу должна быть полной и корректной")
        return

    if not await legal_db.has_user(user_info.id):
        await message.answer("Пользователя нет в списке")
        return

    code = await legal_db.remove_user(user_info.id)
    if code:
        await message.answer("Пользователь исключен из списка")
    else:
        await message.answer("Что-то пошло не так")


@ltl_labeler.private_message(
    access=[Groups.LEGAL, Rights.LEAD],
    text="ЛТсписок",
)
async def list_legal(message: Message) -> None:
    users = await users_db.get_all("legal")
    reformatted = await ReformatHandler.reformat_moderator_list(users, "legal")
    await message.answer(
        f"LT с правами у бота:\n{reformatted}" if reformatted else "Ни у кого нет прав"
    )
