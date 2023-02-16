from random import randint, choice
from time import time
from typing import Any

from aiofiles import open as async_open
from aiohttp import ClientSession as aioClientSession

SECONDS = 3600

formatted_time = {
    "час": 1,
    "день": 24,
    "сутки": 24,
    "неделя": 24 * 7,
    "месяц": 24 * 30,
    "год": 24 * 365,
}


formatted_comments = {
    "ннл": "Ненормативная лексика",
    "рек": "Реклама",
    "реклама": "Реклама",
    "оффтоп": "Оффтоп",
    "флуд": "Флуд",
    "провокация": "Провокации и (или) побуждения Игроков к нарушению Пользовательского соглашения",
    "клевета": "Клевета, размещение заведомо ложной информации об Игре, Администрации, Модераторах или Пользователях",
    "буст": "Рекламные сообщения, которые содержут контент, нарушающий Пользовательское соглашение",
    "читы": "Реклама ПО, нарушающее Пользовательское соглашение",
    "грм": "Реклама магазина аккаунтов",
    "ода": "Обсуждение действий модератора(-ов)",
    "оса": "Операции с аккаунтом (-ами)",
    "оа": "Оскорбление администрации",
    "оу": "Оскорбление участника (-ов)",
    "ор": "Оскорбление разработчиков",
    "ом": "Оскорбление модератора (-ов)",
    "оп": "Оскорбление проекта",
    "ур": "Оскорбления, содержащие упоминание родных (родственников)",
    "рсп": "Реклама сторонних проектов",
    "попр": "Попрошайничество",
    "полит": "Обсуждение вопросов современной политики",
    "спам": "Спам",
    "пнрв": "Прямая или косвенная пропаганда алкоголя (наркотических или психотропных веществ)",
    "нац": "Нацизм / радикализм / призыв к массовому насилию",
    "порно": "Контент эротического характера",
    "мош": "Мошенничество",
    "ава": "Аватар, нарушающий правила сообщества",
    "фио": "Фамилия и (или) Имя, нарушающая (-ее, -ие) правила сообщества",
}


class Reformatter:
    def __init__(self, ban_time: str | None):
        self.ban_time = ban_time

    async def reformat_time(self) -> int | None:
        if formatted_time.get(self.ban_time) is None:
            return None
        return int(time() + (formatted_time.get(self.ban_time) * SECONDS))

    async def reformat_time_to_text(self) -> str | None:
        if self.ban_time in (None, "", "перм", "навсегда", "пермач"):
            return "навсегда"
        if formatted_time.get(self.ban_time) is None:
            return None
        return f"на {self.ban_time}"

    async def reformat_comment(self, comment: str) -> str | None:
        return formatted_comments.get(comment)

    async def reformat_moderator_id(self, rights: int = 1) -> str:
        return "SМВ" if rights == 3 else "МВ"

    async def reformat_moderator_dict(self, moderator_dict: dict) -> str:
        r = []
        for moderator in moderator_dict:
            current_moderator = moderator_dict[moderator]
            if current_moderator["first_name"] != "TEST":
                prefix = await self.reformat_moderator_id(current_moderator["rights"])
                r.append(
                    f"@id{moderator}"
                    f"({current_moderator['first_name']} {current_moderator['last_name']}) "
                    f"({prefix}{current_moderator['ID']})"
                )

        return "\n".join(r)


class PhotoHandler:
    def __init__(self, photo: list | None):
        self.photo = photo

    async def get_photo(self) -> str:
        """get_photo

        Returns:
            str: returns max size of photo from list of all sizes
        """
        maxSize, maxSizeIndex = 0, 0
        for index, size in enumerate(self.photo):
            if maxSize < size.height:
                maxSize = size.height
                maxSizeIndex = index
        return self.photo[maxSizeIndex].url

    async def download_photo(self) -> str | None:
        async with aioClientSession() as session:
            url = await self.get_photo()
            async with session.get(url) as resp:
                if resp.status == 200:
                    file_name = f"{round(time() + randint(0, 1000))}.jpg"
                    async with async_open(file_name, mode="wb") as f:
                        await f.write(await resp.read())
                        await f.close()
                    return file_name


class CommentsHandler:
    def __init__(self, comments: list):
        self.comments = comments

    async def get_texts_from_comments(self) -> tuple:
        return (x.text for x in self.comments.items)

    async def get_random_text_from_comments(self) -> tuple:
        texts = await self.get_texts_from_comments()
        return choice(texts) if texts != () else ()


async def async_list_generator(lst: list):
    for key in lst:
        yield key


async def find_key_by_value(value, key, dictionary: dict) -> Any | None:
    for val in dictionary:
        if dictionary[val][key] == value:
            return val
    return None
