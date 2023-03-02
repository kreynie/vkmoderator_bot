import io
from asyncio import to_thread
from time import time
from typing import Literal

from aiohttp import ClientSession

from .jsonfunctions import JSONHandler

json_handler = JSONHandler("formatted.json")
data = json_handler.get_data()
formatted_time = data["time"]
formatted_abbreviations = data["abbreviations"]


class ReformatHandler:
    def __init__(self, ban_time: str | None) -> None:
        self.ban_time = ban_time

    async def reformat_time(self) -> int | None:
        if formatted_time.get(self.ban_time) is None:
            return None
        return int(time() + (formatted_time.get(self.ban_time) * 3600))

    async def reformat_time_to_text(self) -> str | None:
        if self.ban_time in (None, "", "перм", "навсегда", "пермач"):
            return "навсегда"
        if formatted_time.get(self.ban_time) is None:
            return None
        return f"на {self.ban_time}"

    @staticmethod
    async def reformat_comment(comment: str) -> str | None:
        result = []
        if "+" in comment:
            for value in comment.split("+"):
                result.append(formatted_abbreviations.get(value, ""))
            result = ", ".join(result)
        else:
            result = formatted_abbreviations.get(comment, "")
        return result.capitalize() if result != "" else None

    @staticmethod
    async def reformat_moderator_id(rights: int = 1) -> str:
        return "SМВ" if rights == 3 else "МВ"

    @staticmethod
    async def reformat_moderator_dict(
        moderator_dict: dict, group: Literal["moderator", "legal"]
    ) -> str:
        r = []
        for moderator in moderator_dict:
            current_moderator = moderator_dict[moderator]
            if current_moderator["first_name"] != "TEST":
                prefix = await ReformatHandler.reformat_moderator_id(
                    current_moderator["groups"][group]
                )
                r.append(
                    f"@id{moderator}"
                    f"({current_moderator['first_name']} {current_moderator['last_name']}) "
                    f"({prefix}{current_moderator['ID']})"
                )

        return "\n".join(r)


class PhotoHandler:
    def __init__(self, photo: list | None) -> None:
        self.photo = photo

    async def get_photo_max_size(self) -> str:
        """get_photo_max_size

        Returns:
            str: returns max photo size from all sizes list
        """
        maxSize, maxSizeIndex = 0, 0
        for index, size in enumerate(self.photo):
            if maxSize < size.height:
                maxSize = size.height
                maxSizeIndex = index
        return self.photo[maxSizeIndex].url

    async def get_photo(self) -> str:
        async with ClientSession() as session:
            url = await self.get_photo_max_size()
            async with session.get(url) as resp:
                if resp.status == 200:
                    buffer = await to_thread(io.BytesIO)
                    await to_thread(buffer.write, await resp.read())
                    return buffer.getvalue()


class CommentsHandler:
    @staticmethod
    async def get_texts_from_comments(comments) -> dict:
        for x in comments.items:
            if x.from_id != 0:
                yield {"id": x.id, "from_id": x.from_id, "text": x.text}


async def async_list_generator(lst: list):
    for key in lst:
        yield key
