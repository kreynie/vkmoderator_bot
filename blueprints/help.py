from vkbottle.user import Message, UserLabeler

from helpfuncs.jsonfunctions import DictionaryFuncs, JSONHandler

from .rules import CheckPermissions, Groups, PermissionChecker, Rights

help_labeler = UserLabeler()
help_labeler.vbml_ignore_case = True
help_labeler.custom_rules["access"] = CheckPermissions


@help_labeler.private_message(access=[Groups.MODERATOR, Rights.LOW], text="сокращения")
async def get_abbreviations(message: Message) -> None:
    abbreviations_dict = JSONHandler("formatted.json").get_data().get("abbreviations")
    formatted_abbreviations = await DictionaryFuncs.dict_to_string(
        dictionary=abbreviations_dict, prefix="-", postfix=">", indent=1
    )
    await message.answer(
        message="Список доступных сокращений:\n" + formatted_abbreviations,
    )


@help_labeler.private_message(access=[Groups.MODERATOR, Rights.LOW], text="помощь")
async def moderator_helper(message: Message) -> None:
    raw_help = [
        "Использование бота:",
        "▶️ Бан <userID> <comment> <time>",
        "• <userID> - ссылка на страницу",
        '• <comment> - "ключ" для комментария бана. Для уточнения введи команду "Сокращения"',
        "• <time> - срок бана",
        "---> Бан https://vk.com/steel_wg оффтоп день",
        "⚠️ Для банов от недели и выше требуются скриншоты для публикации в баню",
        "⚠️ Для пермачей используйте один из следующих вариантов:",
        "---> <time> - ничего не указывать / перм / пермач / навсегда",
        "▶️ Сокращения - для просмотра всех доступных сокращений",
    ]
    current_permissions = await PermissionChecker.get_user_permissions(
        str(message.from_id), Groups.MODERATOR
    )
    if current_permissions >= 2:
        raw_help.extend(
            (
                "\n\n",
                "Закрытые модераторские команды: ",
                "▶️ Рассылка <text> - рассылает <text> в исходном виде всем модератором из списка бота",
                "▶️ Добмод <vkID> <MBid>, где <vkID> - ссылка на страницу, <MBid> - НОМЕР модератора",
                "--> Пример: Добмод vk.com/steel_wg 69",
                "▶️ Удалмод <vkID>, где <vkID> - ссылка на страницу",
                "▶️ Модсписок",
                "▶️ Добсокр <abbreviation> <full_text>",
                "▶️ Измсокр <abbreviation> <full_text>",
                "• <abbreviation> - сокращение",
                "• <full_text> - полный текст",
                "▶️ ai_add <level> <text> - добавить в базу бота выражение, где",
                "• <level> - 0 или 1, 1 - нарушение",
                "• <text> - СЫРОЙ текст из комментария, т.е. просто копипаста (без упоминания других пользователей)",
            )
        )

    if current_permissions >= 3:
        raw_help.extend(
            (
                "\n\n",
                "Команды для лидов: ",
                "▶️ Минус <text> - используется вместе с репостом неправильного бана из Бани в ЛС боту. Текст отправляется модератору в ЛС",
            )
        )

    if current_permissions >= 4:
        raw_help.extend(
            (
                "\n\n",
                "Остальные команды: ",
                "▶️ Права <user_id> <group> <value>",
                "▶️ ai_switch",
            )
        )

    await message.answer("\n".join(raw_help))


@help_labeler.private_message(access=[Groups.LEGAL, Rights.LOW], text="ЛТсокр")
async def legal_abbreviations(message: Message) -> None:
    abbreviations_dict = (
        JSONHandler("formatted.json").get_data().get("legal_abbreviations")
    )
    formatted_abbreviations = await DictionaryFuncs.dict_to_string(
        dictionary=abbreviations_dict, prefix="-", postfix=">", indent=1
    )
    await message.answer(
        message="Список доступных сокращений:\n" + formatted_abbreviations,
    )


@help_labeler.private_message(access=[Groups.LEGAL, Rights.LOW], text="ЛТпомощь")
async def legal_helper(message: Message) -> None:
    raw_help = [
        "Использование бота (команды без учета регистра букв):",
        "▶️ ЛТ <public> <user> <reason> <post> <game>",
        "▶️ ЛТСокр - для просмотра всех доступных сокращений Legal Team",
    ]
    current_permissions = await PermissionChecker.get_user_permissions(
        str(message.from_id), Groups.LEGAL
    )
    if current_permissions >= 2:
        raw_help.extend(
            (
                "\n\n",
                "Закрытые LT команды: ",
                "▶️ ДобЛТ <user_id>",
                "--> Пример: Добмод vk.com/steel_wg 69",
                "▶️ УдалЛТ <vkID>, где <vkID> - ссылка на страницу",
                "▶️ ЛТсписок",
            )
        )

    await message.answer("\n".join(raw_help))
