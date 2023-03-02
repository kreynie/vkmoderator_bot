from helpfuncs.functions import ReformatHandler
from helpfuncs.jsonfunctions import DictionaryFuncs, JSONHandler, ModeratorHandler
from helpfuncs.vkfunctions import VKHandler
from vkbottle.user import Message, UserLabeler

from .rules import CheckPermissions, Groups, Rights

ltl_labeler = UserLabeler()
ltl_labeler.vbml_ignore_case = True
ltl_labeler.custom_rules["access"] = CheckPermissions
dict_handler = DictionaryFuncs()
json_handler = JSONHandler()


@ltl_labeler.private_message(
    access=[Groups.LEGAL, Rights.LEAD],
    text=["ДобЛТ <user_id> <MB_id:int>", "ДобЛТ <user_id>"],
)
async def add_legal(message: Message, user_id: str, MB_id: int = None) -> None:
    if user_id is None:
        await message.answer("Забыл ссылку на страницу!")
        return

    user_info = await VKHandler.get_user_info(user_id)
    if user_info == None:
        await message.answer("Ссылка на страницу должна быть полной и корректной")
        return
    user_id = str(user_info["id"])
    moderator_handler = await ModeratorHandler.create()

    data = json_handler.get_data()
    if not await moderator_handler.is_exists(user_id):
        if not MB_id:
            await message.answer(
                "Модератора нет в списке действующих. Нужно прописать его MB"
            )
            return

        moderator_data = {
            "ID": MB_id,
            "first_name": user_info["first_name"],
            "last_name": user_info["last_name"],
        }
        code = await moderator_handler.add_moderator(
            user_id, moderator_data, Groups.LEGAL
        )
        result = None
    else:
        code, result = await dict_handler.add_value(
            data[user_id], f"groups{DictionaryFuncs.separator}legal", 1
        )
    match code:
        case "not_found":
            await message.answer("Не найден ключ")
        case "success":
            if result:
                data[user_id] = result
                json_handler.save_data(data)
            await message.answer("Готово")
        case "exists":
            await message.answer(f"У модератора уже есть права")
        case _:
            await message.answer(f"Произошла ошибка. Код: {code}")


@ltl_labeler.private_message(
    access=[Groups.LEGAL, Rights.LEAD], text="УдалЛТ <user_id>"
)
async def remove_legal(message: Message, user_id: str) -> None:
    if user_id is None:
        await message.answer("Забыл ссылку на страницу!")
        return

    user_info = await VKHandler.get_user_info(user_id)
    if user_info == None:
        await message.answer("Ссылка на страницу должна быть полной и корректной")
        return

    data = json_handler.get_data()
    code, result = await dict_handler.edit_value(data, "legal", 0)
    if code == "not_found":
        await message.answer("Не найден ключ")
    if code == "success":
        json_handler.save_data(result)
        await message.answer("Готово")


@ltl_labeler.private_message(access=[Groups.LEGAL, Rights.LEAD], text="ЛТсписок")
async def list_legal(message: Message) -> None:
    data = json_handler.get_data()
    reformatted = await ReformatHandler.reformat_moderator_dict(data, "legal")
    await message.answer(f"Модераторы с правами Legal Team:\n{reformatted}")
