from helpfuncs import DictionaryFuncs, JSONHandler
from vkbottle.user import Message, UserLabeler
from config import project_path

from .rules import CheckPermissions, Groups, PermissionChecker, Rights

help_labeler = UserLabeler()
help_labeler.vbml_ignore_case = True
help_labeler.custom_rules["access"] = CheckPermissions

get_json = JSONHandler(project_path / "formatted.json").get_data


@help_labeler.private_message(
    access=[Groups.MODERATOR, Rights.LOW],
    text="сокращения",
)
async def get_abbreviations(message: Message) -> None:
    abbreviations_dict = get_json().get("abbreviations")
    formatted_abbreviations = await DictionaryFuncs.dict_to_string(
        dictionary=abbreviations_dict,
        prefix="-",
        postfix=">",
        indent=1,
    )
    await message.answer("Список доступных сокращений:\n" + formatted_abbreviations)


@help_labeler.private_message(
    access=[Groups.MODERATOR, Rights.LOW],
    text=["помощь", "команды", "help"],
)
async def moderator_helper(message: Message) -> None:
    raw_help = [
        "Использование бота:",
        "▶️ Сокращения - для просмотра всех доступных сокращений",
        "▶️ Бан <user> <reason> <time>",
        "• <user> - ссылка на страницу либо упоминание через @",
        '• <reason> - "ключ" для комментария бана. Для уточнения введи команду "Сокращения"',
        "• <time> - срок бана",
        "---> Бан https://vk.com/steel_wg оффтоп день",
        "---> Бан vk.com/steel_wg нац пермач",
        "---> Бан @steel_wg оп+ор+оу+оа месяц",
        "⚠️ Для банов от недели и выше требуются скриншоты для публикации в баню",
        "⚠️ Для пермачей используйте один из следующих вариантов:",
        "---> <time> - ничего не указывать / перм / пермач / навсегда",
    ]
    current_permissions = await PermissionChecker.get_user_permissions(
        message.from_id, Groups.MODERATOR
    )
    if current_permissions >= 2:
        raw_help.extend(
            (
                "\n\n",
                "Закрытые модераторские команды: ",
                "▶️ Рассылка <text> - рассылает <text> в исходном виде всем модератором из списка бота",
                "▶️ Добмод <user> <id>, где <user> - ссылка на страницу или упоминание, <id> - НОМЕР модератора",
                "▶️ Удалмод <user>, где <user> - ссылка на страницу или упоминание",
                "--> Пример: Добмод vk.com/steel_wg 69",
                "--> Пример: Удалмод @steel_wg 69",
                "▶️ Модсписок",
                "▶️ Добсокр <abbreviation> <full_text>",
                "▶️ Измсокр <abbreviation> <full_text>",
                "▶️ Удалсокр <abbreviation>",
                "• <abbreviation> - сокращение",
                "• <full_text> - полный текст",
            )
        )

    if current_permissions >= 3:
        raw_help.extend(
            (
                "\n\n",
                "Команды для лидов: ",
                "▶️ Минус <text> - используется вместе с репостом неправильного \
                    бана из Бани в ЛС боту. Текст отправляется модератору в ЛС",
            )
        )

    if current_permissions >= 4:
        raw_help.extend(
            (
                "\n\n",
                "Остальные команды: ",
                "▶️ Права <user> <group> <value>",
            )
        )

    await message.answer("\n".join(raw_help))


@help_labeler.private_message(
    access=[Groups.LEGAL, Rights.LOW],
    text="ЛТсокр",
)
async def legal_abbreviations(message: Message) -> None:
    abbreviations_dict = get_json().get("ltabbreviations")
    games_abbreviations_dict = get_json().get("games")
    abbreviations_dict = await DictionaryFuncs.dict_to_string(abbreviations_dict)
    games_abbreviations_dict = await DictionaryFuncs.dict_to_string(
        games_abbreviations_dict
    )
    result_string = (
        "Список доступных сокращений:\n"
        + abbreviations_dict
        + "\n\nСписок сокращений игр:\n"
        + games_abbreviations_dict
    )
    await message.answer(result_string)


@help_labeler.private_message(
    access=[Groups.LEGAL, Rights.LOW],
    text="ЛТпомощь",
)
async def legal_helper(message: Message) -> None:
    raw_help = [
        "Использование бота (команды без учета регистра букв):",
        "▶️ ЛТСокр - для просмотра всех доступных сокращений Legal Team",
        "▶️ ЛТ <public> <reason> <post> <game> <flea>",
        "--> public - ссылка на группу",
        "--> reason - причина. ‼️ Брать из ЛТСокр",
        "--> post - ссылка на пост",
        "--> game - игра",
        "--> flea - необязательный параметр. Отмечает барахолки. Может быть 1 или 0",
        "▶️ ЛТ <user> <reason> <post> <game> <dialog_time>",
        "--> user - ссылка на пользователя",
        "--> dialog_time - время пересылки диалога Троллю",
        "▶️ Пример:",
        "ЛТ https://vk.com/id302266380 буст https://vk.com/wall302266380_4576 бб",
        "Вместе с командой не забудьте прикрепить к сообщению скриншот (-ы)",
    ]
    current_permissions = await PermissionChecker.get_user_permissions(
        message.from_id, Groups.LEGAL
    )
    if current_permissions >= 2:
        raw_help.extend(
            (
                "\n\n",
                "LT команды для лида: ",
                "▶️ ДобЛТ <user> <LT_id>",
                "--> доблт vk.com/steel_wg 69",
                "--> доблт @steel_wg 69",
                "▶️ УдалЛТ <user>, где <user> - ссылка на страницу или упоминание через @",
                "▶️ ЛТсписок",
            )
        )

    await message.answer("\n".join(raw_help))
