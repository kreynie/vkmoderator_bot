import json
from re import findall
from typing import Union

from .functions import findKeyByValue


async def getData(filename: str = "moderators.json") -> dict:
    with open(filename, "r", encoding="utf-8") as file:
        data = json.load(file)
    return data


async def saveData(filename: str = "moderators.json", dictionary: dict = {}) -> None:
    with open(filename, "w+", encoding="utf-8") as file:
        json.dump(dictionary, file, ensure_ascii=False, indent=4)


async def refreshAndSort(dictionary: dict) -> str:
    data = dict(sorted(dictionary.items(), key=lambda x: x[1]["ID"]))
    await saveData("moderators.json", data)
    return "success"


async def addModerator(moderatorID: str, moderatorData: dict) -> str:
    """Add moderator's key to dictionary

    Args:
        moderatorID (str): key to be created. Gets from user's VK ID
        moderatorData (dict): values to be in the key

    Returns:
        str: "notExists" if there is no moderatorID in dictionary
             "success" if succeed
    """
    allMods = await getData()

    if moderatorID in allMods:
        return "exists"
    allMods[moderatorID] = moderatorData

    await refreshAndSort(allMods)
    return "success"


async def deleteModerator(moderatorID: str) -> str:
    """Delete moderator's key from dictionary

    Args:
        moderatorID (str): key to be deleted. Gets from user's VK ID

    Returns:
        str: "notExists" if there is no moderatorID in dictionary
             "success" if succeed
    """
    allMods = await getData()

    if moderatorID not in allMods:
        return "notExists"
    del allMods[str(moderatorID)]

    await refreshAndSort(allMods)
    return "success"


async def editValues(
    moderatorID: str, key: Union[int, str, bool], value: Union[int, str, bool]
) -> str:
    """Edit any value in moderator dict

    Args:
        moderatorID (str): key for editing. Gets from user's VK ID
        key (Union[int, str, bool]): key to change
        value (Union[int, str, bool]): value that will be changed

    Returns:
        str: "notExists" if there is no moderatorID in dictionary
             "success" if succeed
    """
    allMods = await getData()

    if moderatorID not in allMods:
        return "notExists"

    allMods[moderatorID][key] = value

    await refreshAndSort(allMods)
    return "success"


async def findModeratorByID(moderatorID: str):
    allMods = await getData()
    result = await findKeyByValue(
        value=int(findall("\d+", moderatorID)[0]),
        key="ID",
        dictionary=allMods,
    )
    return result
