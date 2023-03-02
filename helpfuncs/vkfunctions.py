from re import match
from typing import Dict, List, Literal, Optional

from vkbottle import VKAPIError
from vkbottle.tools import PhotoWallUploader

from config import api, ban_group_id, ban_reason_group_id


class VKHandler:
    @staticmethod
    async def upload_image(photo: str | bytes) -> str | List[dict]:
        return await PhotoWallUploader(api).upload(photo)

    @staticmethod
    async def get_user_info(
        username: str,
        name_case: Optional[Literal["nom", "gen", "dat", "acc", "ins", "abl"]] = None,
    ) -> Dict[str, str | int] | None:
        matched_mention = None
        matched_link = match(r"\/.*vk\.com\/(.*)", username)
        if matched_link is None:
            matched_mention = match(r"\[id(.+?)\|", username)

        if all(x is None for x in (matched_mention, matched_link)):
            return None

        matched = matched_link if matched_link else matched_mention
        info = await api.users.get([matched.group(1)], name_case)
        if not info:
            return None

        return {
            "first_name": info[0].first_name,
            "last_name": info[0].last_name,
            "id": info[0].id,
        }

    @staticmethod
    async def ban(*args, **kwargs) -> int:
        return await api.groups.ban(group_id=abs(ban_group_id), *args, **kwargs)

    @staticmethod
    async def check_if_banned(user_id: int) -> bool:
        try:
            await api.groups.get_banned(group_id=abs(ban_group_id), owner_id=user_id)
            return True
        except VKAPIError[104]:
            return False

    @staticmethod
    async def post(**kwargs):
        return await api.wall.post(owner_id=ban_reason_group_id, **kwargs)

    @staticmethod
    async def get_posts(count: int = 1) -> list:
        posts = await api.wall.get(owner_id=ban_group_id, count=count)
        return posts.items

    @staticmethod
    async def get_comments(**kwargs):
        return await api.wall.get_comments(owner_id=ban_group_id, sort="desc", **kwargs)

    @staticmethod
    async def send_message(*args, **kwargs) -> int:
        return await api.messages.send(*args, **kwargs)
