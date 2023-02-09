import json
from re import findall
from typing import Union

from .functions import find_key_by_value


class JSONHandler:
    def __init__(self, filename: str = "moderators.json"):
        self.filename = filename

    async def get_data(self) -> dict:
        with open(self.filename, "r", encoding="utf-8") as file:
            data = json.load(file)
        return data

    async def save_data(self, dictionary: dict = {}) -> None:
        with open(self.filename, "w+", encoding="utf-8") as file:
            json.dump(dictionary, file, ensure_ascii=False, indent=4)

    async def refresh_and_sort(self, dictionary: dict) -> str:
        data = dict(sorted(dictionary.items(), key=lambda x: x[1]["ID"]))
        await self.save_data(data)
        return "success"

    async def edit_value(
        self,
        moderator_id: str,
        key: Union[int, str, bool],
        value: Union[int, str, bool],
    ) -> str:
        """Edit any value in moderator dict

        Args:
            moderator_id (str): key for editing. Gets from user's VK ID
            key (Union[int, str, bool]): key to change
            value (Union[int, str, bool]): value that will be changed

        Returns:
            str: "not_exists" if there is no moderator_id in dictionary
                "success" if succeed
        """
        all_mods = await self.get_data()

        if moderator_id not in all_mods:
            return "not_exists"

        all_mods[moderator_id][key] = value

        await self.refresh_and_sort(all_mods)
        return "success"


class ModeratorHandler(JSONHandler):
    def __init__(self, filename: str = "moderators.json"):
        self.filename = filename
        self.all_mods = self.get_data()

    async def add_moderator(self, moderator_id: str, moderator_data: dict) -> str:
        """Add moderator's key to dictionary

        Args:
            moderator_id (str): key to be created. Gets from user's VK ID
            moderator_data (dict): values to be in the key

        Returns:
            str: "not_exists" if there is no moderator_id in dictionary
                "success" if succeed
        """
        if moderator_id in self.all_mods:
            return "exists"
        self.all_mods[moderator_id] = moderator_data

        await self.refresh_and_sort(self.all_mods)
        return "success"

    async def delete_moderator(self, moderator_id: str) -> str:
        """Delete moderator's key from dictionary

        Args:
            moderator_id (str): key to be deleted. Gets from user's VK ID

        Returns:
            str: "not_exists" if there is no moderator_id in dictionary
                "success" if succeed
        """
        if moderator_id not in self.all_mods:
            return "not_exists"
        del self.all_mods[str(moderator_id)]

        await self.refresh_and_sort(self.all_mods)
        return "success"

    async def find_moderator_by_id(self, moderator_id: str):
        result = await find_key_by_value(
            value=int(findall("\d+", moderator_id)[0]),
            key="ID",
            dictionary=await self.all_mods,
        )
        return result
