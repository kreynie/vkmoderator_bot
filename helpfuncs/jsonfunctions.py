import json
from re import findall
from typing import Union, Any

from .functions import find_key_by_value


class JSONHandler(object):
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


class ModeratorHandler(JSONHandler):
    @classmethod
    async def create(cls):
        self = ModeratorHandler()
        self.filename = "moderators.json"
        self.moderator_list = await self.get_data()
        return self

    async def add_moderator(self, moderator_id: str, moderator_data: dict) -> str:
        """Add moderator's key to dictionary

        Args:
            moderator_id (str): key to be created. Gets from user's VK ID
            moderator_data (dict): values to be in the key

        Returns:
            str: "not_exists" if there is no moderator_id in dictionary
                "success" if succeed
        """
        if moderator_id in self.moderator_list:
            return "exists"
        self.moderator_list[moderator_id] = moderator_data

        await self.refresh_and_sort(self.moderator_list)
        return "success"

    async def delete_moderator(self, moderator_id: str) -> str:
        """Delete moderator's key from dictionary

        Args:
            moderator_id (str): key to be deleted. Gets from user's VK ID

        Returns:
            str: "not_exists" if there is no moderator_id in dictionary
                "success" if succeed
        """
        if moderator_id not in self.moderator_list:
            return "not_exists"
        del self.moderator_list[str(moderator_id)]

        await self.refresh_and_sort(self.moderator_list)
        return "success"

    async def find_moderator_by_id(self, moderator_id: str):
        result = await find_key_by_value(
            value=int(findall("\d+", moderator_id)[0]),
            key="ID",
            dictionary=await self.moderator_list,
        )
        return result

    async def edit_value(
        self,
        moderator_id: str,
        key: Union[int, str, bool],
        value: Any,
    ) -> str:
        """Edit any value in moderator dict

        Args:
            moderator_id (str): key for editing. Gets from user's VK ID
            key (Union[int, str, bool]): key to change
            value (Any): value that will be changed

        Returns:
            str: "not_exists" if there is no moderator_id in dictionary
                "success" if succeed
        """
        if moderator_id not in self.moderator_list:
            return "not_exists"

        self.moderator_list[moderator_id][key] = value

        await self.refresh_and_sort(self.moderator_list)
        return "success"
