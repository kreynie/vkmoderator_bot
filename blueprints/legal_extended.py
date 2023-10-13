from vkbottle.user import Message, UserLabeler

from config import legal_db, users_db
from helpfuncs import VKHandler
from helpfuncs.functions import ReformatHandler
from utils.exceptions import handle_errors_decorator
from .rules import CheckPermissions, Groups, Rights

ltl_labeler = UserLabeler()
ltl_labeler.vbml_ignore_case = True
ltl_labeler.custom_rules["access"] = CheckPermissions


@ltl_labeler.private_message(
    access=[Groups.LEGAL, Rights.MIDDLE],
    text=[
        "ДобЛТ <user> <legal_id:int>",
        "ДобЛТ <user>",
        "ДобЛТ",
    ],
)
@handle_errors_decorator
async def add_legal(message: Message, user: str = "", legal_id: int = 0) -> None:
    if not legal_id:
        await message.answer("Забыл айдишник")
    if not user:
        await message.answer("Забыл ссылку на страницу!")
        return

    user_info = await VKHandler.get_user_info(user)

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
    access=[Groups.LEGAL, Rights.MIDDLE],
    text=["УдалЛТ <user>", "УдалЛТ"],
)
@handle_errors_decorator
async def remove_legal(message: Message, user: str = "") -> None:
    if not user:
        await message.answer("Забыл ссылку на страницу!")
        return

    user_info = await VKHandler.get_user_info(user)

    if not await legal_db.has_user(user_info.id):
        await message.answer("Пользователя нет в списке")
        return

    code = await legal_db.remove_user(user_info.id)
    if code:
        await message.answer("Пользователь исключен из списка")
    else:
        await message.answer("Что-то пошло не так")


@ltl_labeler.private_message(
    access=[Groups.LEGAL, Rights.MIDDLE],
    text="ЛТсписок",
)
async def list_legal(message: Message) -> None:
    legal = await legal_db.get_all()
    reformatted = await ReformatHandler.moderator_list(legal, "legal")
    await message.answer(
        f"LT с правами у бота:\n{reformatted}" if reformatted else "Ни у кого нет прав"
    )
