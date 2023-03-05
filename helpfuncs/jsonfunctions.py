import json


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


class DictionaryFuncs:
    @classmethod
    async def dict_to_string(
        cls,
        dictionary: dict,
        prefix: str = " ",
        postfix: str = "",
        separator: str = ":",
        indent: int = 0,
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
                result += f"{prefix * indent + postfix} {key}{separator} {value}\n"
        return result
