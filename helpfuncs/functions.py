from random import randint
from time import time

from aiofiles import open as aiOpen
from aiohttp import ClientSession as aioClientSession

SECONDS = 3600

formattedTime = {
    "час": 1,
    "день": 24,
    "сутки": 24,
    "неделя": 24 * 7,
    "месяц": 24 * 30,
    "год": 24 * 365,
}


async def reformatTime(banTime: str = "час"):
    if formattedTime.get(banTime) is None:
        return None
    banUntil = time() + (formattedTime.get(banTime) * SECONDS)
    return int(banUntil)


async def timeToText(banTime: str = "час"):
    if banTime in formattedTime:
        return f"на {banTime}"
    elif banTime in (None, "", "перм", "навсегда", "пермач"):
        return "навсегда"
    return 0


formattedComments = {
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
}


async def reformatComment(comment: str) -> str:
    if formattedComments.get(comment) is not None:
        return formattedComments.get(comment)


async def getMaxSizePhotoURL(photo: list) -> str:
    maxSize, maxSizeIndex = 0, 0
    for index, size in enumerate(photo):
        if maxSize < size.height:
            maxSize = size.height
            maxSizeIndex = index
    return dict(photo[maxSizeIndex])["url"]


async def downloadPhoto(url: str) -> str:
    async with aioClientSession() as session:
        async with session.get(url) as resp:
            fileName = f"{round(time() + randint(0, 1000))}.jpg"
            if resp.status == 200:
                async with aiOpen(fileName, mode="wb") as f:
                    await f.write(await resp.read())
                    await f.close()
    return fileName


async def reformatModeratorID(rights: int = 1) -> str:
    return "SМВ" if rights == 3 else "МВ"


async def reformatModeratorDict(moderatorDict: dict) -> str:
    r = []
    for moderator in moderatorDict:
        current_moderator = moderatorDict[moderator]
        if (
            current_moderator["first_name"] != "TEST"
            and current_moderator["rights"] >= 1
        ):
            level = await reformatModeratorID(current_moderator["rights"])
            r.append(
                f"@id{moderator}"
                f"({current_moderator['first_name']} {current_moderator['last_name']})"
                f"({level}{current_moderator['ID']})"
            )

    return "\n".join(r)


async def asyncListGenerator(lst: list):
    for key in lst:
        yield key


async def findKeyByValue(value, key, dictionary: dict):
    for val in dictionary:
        if dictionary[val][key] == value:
            return val
    return "notFound"


async def get_texts_from_comments(comments: list) -> list:
    texts = [x.text for x in comments.items]
    return texts


async def get_text_from_comments(comments: list) -> str:
    text = await get_texts_from_comments(comments)
    return text[0] if text != [] else None
