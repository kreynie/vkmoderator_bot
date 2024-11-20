from vkbottle.user import Message

from config import project_path
from src.blueprints import rules
from src.helpfuncs import DictionaryFuncs, JSONHandler
from .base_labeler import labeler

get_json = JSONHandler(project_path / "formatted.json").get_data


@labeler.private_message(
    access=[rules.StuffGroups.MODERATOR, rules.Rights.LOW],
    text="сокращения",
)
async def get_abbreviations(message: Message) -> None:
    abbreviations_dict = get_json().get("abbreviations")
    formatted_abbreviations = DictionaryFuncs.dict_to_string(
        dictionary=abbreviations_dict,
    )
    await message.answer("Список доступных сокращений:\n" + formatted_abbreviations)


@labeler.private_message(
    access=[rules.StuffGroups.MODERATOR, rules.Rights.LOW],
    text=["помощь", "команды", "help"],
)
async def moderator_helper(
        message: Message,
        rights: int,
) -> None:
    raw_help = [
        "Использование бота:",
        "▶️ Сокращения - для просмотра всех доступных сокращений",
        "▶️ Бан <user> <reason> <time>",
        "• <user> - ссылка на страницу либо упоминание через @",
        '• <reason> - "ключ" для комментария к бану. Для уточнения введи команду "Сокращения"',
        "• <time> - срок бана",
        "---> Бан https://vk.com/steel_lesta оффтоп день",
        "---> Бан vk.com/steel_lesta нац пермач",
        "---> Бан vk.com/steel_lesta спам",
        "---> Бан @steel_lesta ава+разб месяц",
        "\n",
        "⚠️ Для банов от недели и выше требуются скриншоты для публикации в баню",
        "⚠️ Для пермачей используйте один из следующих вариантов:",
        "---> <time> - ничего не указывать / перм / пермач / навсегда",
    ]
    if rights >= 2:
        raw_help.extend(
            (
                "\n\n",
                "Закрытые модераторские команды:",
                "▶️ Добмод <user> <id>",
                "▶️ Удалмод <user>",
                "• <user> - ссылка на страницу или упоминание через @",
                "• <id> - НОМЕР модератора",
                "--> Пример: Добмод vk.com/steel_lesta 69",
                "--> Пример: Удалмод @steel_lesta 69",
                "▶️ Модсписок",
                "▶️ Добсокр <abbreviation> <full_text>",
                "▶️ Измсокр <abbreviation> <full_text>",
                "▶️ Удалсокр <abbreviation>",
                "• <abbreviation> - сокращение",
                "• <full_text> - полный текст",
            )
        )

    if rights >= 3:
        raw_help.extend(
            (
                "\n\n",
                "Команды для лидов:",
                "Отсутствуют",
            )
        )

    if rights >= 4:
        raw_help.extend(
            (
                "\n\n",
                "Остальные команды:",
                "▶️ Права <user> <group> <value>",
            )
        )

    await message.answer("\n".join(raw_help))
