import io
import re
from asyncio import to_thread
from functools import reduce
from time import time
from typing import Literal

from aiohttp import ClientSession
from vkbottle_types.codegen.objects import PhotosPhotoSizes
from vkbottle_types.objects import PhotosPhoto

from config import project_path
from src.helpfuncs.jsonfunctions import JSONHandler
from src.helpfuncs.ssaver import ScreenSaver
from src.schemas.registration import LegalBanRegistrationInfo

json_handler = JSONHandler(project_path / "formatted.json")
data = json_handler.get_data()
formatted_time: dict = data["time"]
formatted_abbreviations: dict = data["abbreviations"]
formatted_legal_abbreviations: dict = data["ltabbreviations"]
formatted_games: dict = data["games"]


def calculate_unix_time_after_period(str_time: str) -> int | None:
    """
    Get unix time after period of time in string

    :param str_time: amount of time from formatted time
    :return: unix time if correct period, None otherwise
    """
    time_value = formatted_time.get(str_time)
    if time_value is None:
        return None
    return int(time() + (time_value * 3600))


def time_to_text(ban_time: str) -> str | None:
    """
    Check if ban time is valid and return

    :param ban_time: ban time in string
    :return: ban time if valid, None otherwise
    """
    if ban_time in (None, "", "перм", "навсегда", "пермач"):
        return "навсегда"
    if formatted_time.get(ban_time) is None:
        return None
    return ban_time


def get_sheets_row(parameters: LegalBanRegistrationInfo) -> list[str]:
    return _generate_legal_common_row(parameters)


def _generate_legal_common_row(parameters: LegalBanRegistrationInfo) -> list[str]:
    common_part = [
        parameters.violator_link,
        parameters.violator_screen_name
        if parameters.violator_screen_name != parameters.violator_link
        else " ",
        parameters.reason,
        parameters.violation_link if parameters.violation_link else " ",
        " ",
        parameters.screenshot_link,
    ]

    if not parameters.is_group and parameters.dialog_time is None:
        parameters.dialog_time = " "

    if parameters.dialog_time is not None:
        common_part.append(parameters.dialog_time)

    if parameters.is_group and parameters.flea is None:
        parameters.flea = "FALSE"

    if parameters.flea is not None:
        common_part.insert(0, parameters.flea)

    common_part.extend([parameters.game, parameters.moderator_key])

    return common_part


def get_legal_abbreviation_text(
    abbreviation: str,
    abbreviation_type: Literal["abbreviations", "games"],
) -> str | None:
    if abbreviation_type == "games":
        return formatted_games.get(abbreviation)
    if abbreviation_type == "abbreviations":
        return formatted_legal_abbreviations.get(abbreviation)


def get_reformatted_comment(comment: str) -> str | None:
    if "+" in comment:
        result = [
            formatted_abbreviations.get(value) for value in comment.strip().split("+")
        ]
        if None in result:
            return None
        result = ", ".join(result)
    else:
        result = formatted_abbreviations.get(comment)
    return result.capitalize() if result else None


async def get_photo(photo: PhotosPhoto) -> bytes | None:
    """Get photo in bytes format

    :param photo: photo
    :return: bytes of photo or None
    """
    async with ClientSession() as session:
        url = get_photo_max_size_url(photo.sizes)
        async with session.get(url) as resp:
            if resp.status == 200:
                photo = await to_thread(io.BytesIO)
                await to_thread(photo.write, await resp.read())
                return photo.getvalue()
    return None


def get_photo_max_size_url(photo: list[PhotosPhotoSizes]) -> str:
    """Get url of max size photo from list of photo sizes

    :param photo: list of photo sizes
    :return: photo url in original size
    """
    max_size, max_size_index = 0, 0
    for index, size in enumerate(photo):
        if max_size < size.height:
            max_size = size.height
            max_size_index = index
    return photo[max_size_index].url


async def screenshot(url: str, **kwargs) -> bytes | None:
    if not get_vk_link(url):
        return None
    if not url.startswith("https://"):
        url = "https://" + url

    return await ScreenSaver(height=2160).screenshot(url, **kwargs)


def get_vk_link(url: str, slug: bool = False) -> str | None:
    matched_link = re.match(r".*vk\.com/(.*)", url)
    if matched_link is None:
        return None
    if slug:
        return matched_link.group(1)
    return matched_link.group(0)


async def async_list_generator(lst: list):
    for key in lst:
        yield key


async def get_id_from_text(user: str) -> str | None:
    matched_mention = None
    matched_link = get_vk_link(user, slug=True)

    # If no direct link is found, try to extract it from a mention
    if matched_link is None:
        matched_mention = re.findall(r"\[(id\d*|club\d+)\|.*?]", user)

    # Use the mention if it exists, otherwise use the direct link
    return matched_mention[0] if matched_mention else matched_link


def split_for_text_for_command(text: str) -> list[str]:
    """Split text for vkbottle command correct validation.

    This function takes a command text as input and cascade deletes last parameter.

    :param text: The command text to split.
    :return: A list of cascades.

    >>> split_for_text_for_command("Права <user> <group:int> <new_allowance:int>")
    >>> [
    >>> "Права <user> <group:int> <new_allowance:int>",
    >>> "Права <user> <group:int>",
    >>> "Права <user>",
    >>> "Права",
    >>> ]
    """
    result = []
    text = text.split(" ")
    for i in range(len(text), 0, -1):
        result.append(" ".join(text[:i]))
    return result


def camel_to_sneak(string: str) -> str:
    """
    Converts a camelCase string to sneak_case

    Python reduce() method applies a function to all the string alphabets, that wherever it find
    uppercase alphabet, it adds '_' in front of it and replace the uppercase alphabet with lowercase alphabet.
    :param string: string to convert
    :return: sneak_case string
    """
    return reduce(lambda x, y: x + ("_" if y.isupper() else "") + y, string).lower()
