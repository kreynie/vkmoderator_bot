import io
from asyncio import to_thread
from time import time
from typing import Any, AsyncGenerator, Dict, List, Literal

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
    async def reformat_moderator_id(
        allowance: int, prefix_base: Literal["МВ", "LT"]
    ) -> str:
        return "S" + prefix_base if allowance == 3 else prefix_base

    @staticmethod
    async def reformat_moderator_dict(
        moderator_dict: List[Dict[str, Any]],
        group: Literal["moderators", "legal"],
    ) -> str:
        r = []
        for moderator in moderator_dict:
            if moderator["first_name"] != "TEST":
                prefix_base = "МВ" if group == "moderators" else "LT"
                prefix = await ReformatHandler.reformat_moderator_id(
                    moderator.get("allowance"), prefix_base
                )
                r.append(
                    f"@id{moderator['id']}"
                    f"({moderator['first_name']} {moderator['last_name']}) "
                    f"({prefix}{moderator['key']})"
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
        max_size, max_size_index = 0, 0
        for index, size in enumerate(self.photo):
            if max_size < size.height:
                max_size = size.height
                max_size_index = index
        return self.photo[max_size_index].url

    async def get_photo(self) -> bytes:
        async with ClientSession() as session:
            url = await self.get_photo_max_size()
            async with session.get(url) as resp:
                if resp.status == 200:
                    photo = await to_thread(io.BytesIO)
                    await to_thread(photo.write, await resp.read())
                    return photo.getvalue()


class CommentsHandler:
    @staticmethod
    async def get_data_from_comments(comments) -> AsyncGenerator:
        for x in comments.items:
            if x.from_id != 0:
                yield {"id": x.id, "from_id": x.from_id, "text": x.text}


async def async_list_generator(lst: list):
    for key in lst:
        yield key
