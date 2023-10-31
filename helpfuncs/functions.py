import io
from asyncio import to_thread
import re
from time import time
from typing import Any, Generator, List, Literal, Optional

from aiohttp import ClientSession

from config import project_path
from utils.info_classes import StuffInfo

from .jsonfunctions import JSONHandler
from .ssaver import ScreenSaver

json_handler = JSONHandler(project_path / "formatted.json")
data = json_handler.get_data()
formatted_time: dict = data["time"]
formatted_abbreviations: dict = data["abbreviations"]
formatted_legal_abbreviations: dict = data["ltabbreviations"]
formatted_games: dict = data["games"]


class ReformatHandler:
    def __init__(self, ban_time: str | None) -> None:
        self.ban_time = ban_time

    def time(self) -> int | None:
        if formatted_time.get(self.ban_time) is None:
            return None
        return int(time() + (formatted_time.get(self.ban_time) * 3600))

    def time_to_text(self) -> str | None:
        if self.ban_time in (None, "", "перм", "навсегда", "пермач"):
            return "навсегда"
        if formatted_time.get(self.ban_time) is None:
            return None
        return self.ban_time

    @staticmethod
    def comment(comment: str) -> str | None:
        if "+" in comment:
            result = [
                formatted_abbreviations.get(value)
                for value in comment.strip().split("+")
            ]
            if None in result:
                return None
            result = ", ".join(result)
        else:
            result = formatted_abbreviations.get(comment)
        return result.capitalize() if result else None

    @staticmethod
    def legal(
        type_: Literal["abbreviations", "games"],
        abbreviation: str,
    ) -> str | None:
        if type_ == "games":
            return formatted_games.get(abbreviation)
        if type_ == "abbreviations":
            return formatted_legal_abbreviations.get(abbreviation)

    @staticmethod
    def generate_legal_public_row(
        violator_link: str,
        reason: str,
        violation_link: str,
        screenshot_link: str,
        game: str,
        moderator_key: str,
        violator_screen_name: str,
        flea: Literal["TRUE", "FALSE"] = "FALSE",
        *args,
        **kwargs,
    ) -> str:
        result_string = [flea]
        result_string.extend(
            [
                violator_link,
                violator_screen_name if violator_screen_name != violator_link else " ",
                reason,
                violation_link if violation_link else " ",
                " ",
                screenshot_link,
            ]
        )
        result_string.extend([game, moderator_key])
        return "+".join(result_string)

    @staticmethod
    def generate_legal_user_row(
        violator_link: str,
        reason: str,
        violation_link: str,
        screenshot_link: str,
        game: str,
        moderator_key: str,
        violator_screen_name: str,
        dialog_time: Optional[str] = None,
        *args,
        **kwargs,
    ) -> str:
        result_string = [
            violator_link,
            violator_screen_name if violator_screen_name != violator_link else " ",
            reason,
            violation_link,
            " ",
            screenshot_link,
            dialog_time if dialog_time is not None else " ",
            game,
            moderator_key,
        ]
        return "+".join(result_string)

    @staticmethod
    def sheets_row(is_group: bool, **kwargs) -> str:
        if is_group:
            return ReformatHandler.generate_legal_public_row(**kwargs)
        return ReformatHandler.generate_legal_user_row(**kwargs)

    @staticmethod
    def moderator_id(allowance: int, prefix_base: str | Literal["МВ", "LT"]) -> str:
        return "S" + prefix_base if allowance == 3 else prefix_base

    @staticmethod
    def moderator_list(
        moderator_dict: List[StuffInfo],
        group: Literal["moderators", "legal"],
    ) -> str:
        r = []
        for moderator in moderator_dict:
            if moderator.key >= 0:
                prefix_base = "МВ" if group == "moderators" else "LT"
                prefix = ReformatHandler.moderator_id(moderator.allowance, prefix_base)
                r.append(
                    f"@id{moderator.id}"
                    f"({moderator.full_name}) "
                    f"({prefix}{moderator.key})"
                )

        return "\n".join(r)


class PhotoHandler:
    def __init__(self, photo: list | None) -> None:
        self.photo = photo

    async def get_photo(self) -> bytes | None:
        async with ClientSession() as session:
            url = PhotoHandler.get_photo_max_size_url(self.photo)
            async with session.get(url) as resp:
                if resp.status == 200:
                    photo = await to_thread(io.BytesIO)
                    await to_thread(photo.write, await resp.read())
                    return photo.getvalue()
        return None

    @staticmethod
    def get_photo_max_size_url(photo: list) -> str:
        """get_photo_max_size_url

        Returns:
            str: returns photo url from all sizes list
        """
        max_size, max_size_index = 0, 0
        for index, size in enumerate(photo):
            if max_size < size.height:
                max_size = size.height
                max_size_index = index
        return photo[max_size_index].url

    @staticmethod
    async def screenshot(url: str, **kwargs) -> bytes | None:
        if not LinkHandler.check_vk_link(url):
            return None
        if not url.startswith("https://"):
            url = "https://" + url

        return await ScreenSaver(height=2160).screenshot(url, **kwargs)


class CommentsHandler:
    @staticmethod
    def get_data_from_comments(comments) -> Generator:
        for x in comments.items:
            if x.from_id != 0:
                yield {"id": x.id, "from_id": x.from_id, "text": x.text}


class LinkHandler:
    @staticmethod
    def check_vk_link(url: str, slug: bool = False) -> str | None:
        matched_link = re.match(r".*vk\.com/(.*)", url)
        if matched_link is None:
            return None
        if slug:
            return matched_link.group(1)
        return matched_link.group(0)


async def async_list_generator(lst: list[Any]):
    for key in lst:
        yield key


async def get_id_from_text(user: str) -> str | None:
    matched_mention = None
    matched = LinkHandler.check_vk_link(user, slug=True)
    if matched is None:
        matched_mention = re.findall(r"\[(id\d*|club\d+)\|.*?\]", user)

    if matched_mention is None and matched is None:
        return None

    if matched_mention:
        matched = matched_mention[0]

    return matched
