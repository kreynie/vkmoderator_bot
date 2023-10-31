import json
from os import PathLike
from pathlib import Path

from typing import Any, Literal


class JSONHandler:
    def __init__(self, filename: str | Path | PathLike) -> None:
        self.filename = filename

    def get_data(self) -> dict:
        with open(self.filename, "r", encoding="utf-8") as file:
            data = json.load(file)
        return data

    def save_data(self, dictionary: dict) -> None:
        with open(self.filename, "w+", encoding="utf-8") as file:
            json.dump(dictionary, file, ensure_ascii=False, indent=4)

    def refresh_and_sort(self, dictionary: dict) -> str:
        data = dict(sorted(dictionary.items(), key=lambda x: x[1]["ID"]))
        self.save_data(data)
        return "success"


class DictionaryFuncs:
    separator = "."

    @classmethod
    def find_key_path(cls, dictionary: dict, target_key: str) -> str | None:
        """
        Find the path to a key in a nested dictionary.
        Example:
            >>> find_key_path(my_dict, "key3")
        Returns:
            The path to the key as a string (using the class separator),
            or None if the key is not found.
        """
        for key, value in dictionary.items():
            if key == target_key:
                return key
            elif isinstance(value, dict):
                subpath = cls.find_key_path(value, target_key)
                if subpath:
                    return f"{key}{cls.separator}{subpath}"
        return None

    @classmethod
    def add_value(
        cls, dictionary: dict, target_key: str, new_value: Any
    ) -> tuple[Literal["success", "exists"], dict]:
        """
        Add a new value to a key in a nested dictionary. If the key
        does not exist, create it along with any necessary intermediate dictionaries.
        Example:
            >>> add_value(my_dict, f"{first_key}{separator}{second_key}", value)
        Returns:
            ``exists``: the key already exists, old dictionary
            ``success``: succeeded, new dictionary
        """
        path_parts = target_key.split(cls.separator)
        target_path = cls.find_key_path(dictionary, path_parts[-1])
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
    def edit_value(
        cls, dictionary: dict, target_key: str, new_value: Any
    ) -> tuple[str, dict]:
        """
        Edit the value of an existing key in a nested dictionary.
        Example:
            >>> edit_value(my_dict, f"{first_key}{cls.separator}{second_key}", value)
        Returns:
            ``not_found``: the key was not found
            ``success``: succeeded
        """
        path_parts = target_key.split(cls.separator)

        current_dict = dictionary
        for key in path_parts[:-1]:
            if key not in current_dict:
                return "not_found", {}
            current_dict = current_dict[key]

        current_dict[path_parts[-1]] = new_value
        return "success", current_dict

    @classmethod
    def remove_key(
        cls,
        dictionary: dict,
        target_key: str,
        *args,
        **kwargs,
    ) -> tuple[str, dict]:
        """
        Remove an existing key in a nested dictionary.
        Example:
            >>> remove_key(my_dict, f"{first_key}{cls.separator}{second_key}")
        Returns:
            ``not_found``: the key was not found
            ``success``: succeeded
        """
        path_parts = target_key.split(cls.separator)

        current_dict = dictionary
        for key in path_parts[:-1]:
            if key not in current_dict:
                return "not_found", {}
            current_dict = current_dict[key]

        del current_dict[path_parts[-1]]
        return "success", current_dict

    @classmethod
    def dict_to_string(
        cls,
        dictionary: dict,
        prefix: str = "-",
        postfix: str = ">",
        separator: str = ":",
        indent: int = 1,
    ) -> str:
        """
        Convert a dictionary to a pretty string representation.

        Example:
            >>> dict_to_string(my_dict)

        Returns:
            A string representation of the dictionary, with nested dictionaries indented
            and keys sorted alphabetically.
        """
        result = ""
        for key in sorted(dictionary.keys()):
            value = dictionary[key]
            if isinstance(value, dict):
                result += f"{prefix * indent + postfix} {key}:\n"
                result += f"{cls.dict_to_string(value, indent=indent * 2)}"
            else:
                result += f"{prefix * indent + postfix} {key}{separator} {value}\n"
        return result
