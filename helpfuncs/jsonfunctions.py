import json
from re import findall
from typing import Union

from .functions import find_key_by_value


async def get_data(filename: str = "moderators.json") -> dict:
    with open(filename, "r", encoding="utf-8") as file:
        data = json.load(file)
    return data


async def save_data(filename: str = "moderators.json", dictionary: dict = {}) -> None:
    with open(filename, "w+", encoding="utf-8") as file:
        json.dump(dictionary, file, ensure_ascii=False, indent=4)


async def refresh_and_sort(dictionary: dict) -> str:
    data = dict(sorted(dictionary.items(), key=lambda x: x[1]["ID"]))
    await save_data("moderators.json", data)
    return "success"


async def add_moderator(moderator_id: str, moderator_data: dict) -> str:
    """Add moderator's key to dictionary

    Args:
        moderator_id (str): key to be created. Gets from user's VK ID
        moderatorData (dict): values to be in the key

    Returns:
        str: "notExists" if there is no moderator_id in dictionary
             "success" if succeed
    """
    all_mods = await get_data()

    if moderator_id in all_mods:
        return "exists"
    all_mods[moderator_id] = moderator_data

    await refresh_and_sort(all_mods)
    return "success"


async def delete_moderator(moderator_id: str) -> str:
    """Delete moderator's key from dictionary

    Args:
        moderator_id (str): key to be deleted. Gets from user's VK ID

    Returns:
        str: "notExists" if there is no moderator_id in dictionary
             "success" if succeed
    """
    all_mods = await get_data()

    if moderator_id not in all_mods:
        return "notExists"
    del all_mods[str(moderator_id)]

    await refresh_and_sort(all_mods)
    return "success"


async def edit_values(
    moderator_id: str, key: Union[int, str, bool], value: Union[int, str, bool]
) -> str:
    """Edit any value in moderator dict

    Args:
        moderator_id (str): key for editing. Gets from user's VK ID
        key (Union[int, str, bool]): key to change
        value (Union[int, str, bool]): value that will be changed

    Returns:
        str: "notExists" if there is no moderator_id in dictionary
             "success" if succeed
    """
    all_mods = await get_data()

    if moderator_id not in all_mods:
        return "not_exists"

    all_mods[moderator_id][key] = value

    await refresh_and_sort(all_mods)
    return "success"


async def find_moderator_by_id(moderator_id: str):
    all_mods = await get_data()
    result = await find_key_by_value(
        value=int(findall("\d+", moderator_id)[0]),
        key="ID",
        dictionary=all_mods,
    )
    return result
