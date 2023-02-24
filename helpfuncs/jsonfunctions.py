import json
from re import findall
from typing import Union, Any


class JSONHandler:
    def __init__(self, filename: str = "moderators.json") -> None:
        self.filename = filename

    def get_data(self) -> dict:
        with open(self.filename, "r", encoding="utf-8") as file:
            data = json.load(file)
        return data

    def save_data(self, dictionary: dict = {}) -> None:
        with open(self.filename, "w+", encoding="utf-8") as file:
            json.dump(dictionary, file, ensure_ascii=False, indent=4)

    def refresh_and_sort(self, dictionary: dict) -> str:
        data = dict(sorted(dictionary.items(), key=lambda x: x[1]["ID"]))
        self.save_data(data)
        return "success"


class ModeratorHandler(JSONHandler):
    @classmethod
    async def create(cls):
        self = ModeratorHandler()
        self.filename = "moderators.json"
        self.moderator_list = self.get_data()
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

        self.refresh_and_sort(self.moderator_list)
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

        self.refresh_and_sort(self.moderator_list)
        return "success"

    async def find_moderator_by_id(self, moderator_id: str):
        result = await DictionaryFuncs.find_key_by_value(
            value=int(findall("\d+", moderator_id)[0]),
            key="ID",
            dictionary=self.moderator_list,
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

        self.refresh_and_sort(self.moderator_list)
        return "success"


class DictionaryFuncs:
    separator = "."

    @classmethod
    async def find_key_path(cls, dictionary: dict, target_key: str) -> str | None:
        """
        Find the path to a key in a nested dictionary.

        Example:
            >>> find_key_path(my_dict, "key3")

        Returns:
            The path to the key as a string (using the class separator), or None if the key is not found.
        """
        for key, value in dictionary.items():
            if key == target_key:
                return key
            elif isinstance(value, dict):
                subpath = await cls.find_key_path(value, target_key)
                if subpath:
                    return f"{key}{cls.separator}{subpath}"
        return None

    @classmethod
    async def add_value(
        cls, dictionary: dict, target_key: str, new_value: Any
    ) -> tuple((str, dict)):
        """
        Add a new value to a key in a nested dictionary. If the key
        does not exist, create it along with any necessary intermediate dictionaries.

        Example:
            >>> add_value(my_dict, f"{first_key}{separator}{second_key}", value)

        Returns:
            ``exists``: the key already exists
            ``success``: succeeded
        """
        path_parts = target_key.split(cls.separator)
        target_path = await cls.find_key_path(dictionary, path_parts[-1])
        if target_path is not None:
            return "exists", dictionary

        current_dict = dictionary
        for key in path_parts[:-1]:
            if key not in current_dict:
                current_dict[key] = {}
            current_dict = current_dict[key]
        current_dict[path_parts[-1]] = new_value
        return "success", dictionary

    @classmethod
    async def edit_value(
        cls, dictionary: dict, target_key: str, new_value: Any
    ) -> tuple((str, dict)):
        """
        Edit the value of an existing key in a nested dictionary.

        Example:
            >>> edit_value(my_dict, f"{first_key}{cls.separator}{second_key}", value)

        Returns:
            ``not_found``: the key was not found
            ``success``: succeeded
        """
        path_parts = target_key.split(cls.separator)
        target_path = await cls.find_key_path(dictionary, path_parts[-1])
        if target_path is None:
            return "not_found", {}

        current_dict = dictionary
        for key in path_parts[:-1]:
            if key not in current_dict:
                return "not_found", {}
            current_dict = current_dict[key]

        current_dict[path_parts[-1]] = new_value
        return "success", current_dict

    @classmethod
    async def dict_to_string(
        cls, dictionary: dict, prefix: str = " ", postfix: str = "", indent: int = 0
    ) -> str:
        """
        Convert a dictionary to a pretty string representation.

        Example:
            >>> dict_to_string(my_dict)

        Returns:
            A string representation of the dictionary, with nested dictionaries indented and keys sorted alphabetically.
        """
        result = ""
        for key in sorted(dictionary.keys()):
            value = dictionary[key]
            if isinstance(value, dict):
                result += f"{prefix * indent + postfix} {key}:\n{cls.dict_to_string(value, indent + 2)}"
            else:
                result += f"{prefix * indent + postfix} {key}: {value}\n"
        return result

    @staticmethod
    async def find_key_by_value(value, key, dictionary: dict) -> Any | None:
        for val in dictionary:
            if dictionary[val][key] == value:
                return val
        return None
