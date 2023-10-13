from typing import Literal, Optional

from config import api, ban_group_id, ban_reason_group_id
from utils.info_classes import GroupInfo, UserInfo, ObjectInfo
from utils.exceptions import (
    ObjectInformationReError,
    ObjectInformationRequestError,
    InvalidObjectRequestError,
    VKAPIRequestError,
)
from vkbottle import VKAPIError
from vkbottle.tools import PhotoWallUploader
from vkbottle_types.responses.wall import GetCommentsResponseModel, PostResponseModel
from vkbottle_types.responses.photos import PhotosPhoto

from .functions import LinkHandler, PhotoHandler, async_list_generator, get_id_from_text


class VKHandler:
    @staticmethod
    async def upload_image(photo: str | bytes | PhotosPhoto) -> str | list[dict]:
        if isinstance(photo, PhotosPhoto):
            photo_handler = PhotoHandler(photo=photo.sizes)
            photo = await photo_handler.get_photo()
        return await PhotoWallUploader(api).upload(photo)

    @staticmethod
    async def upload_images(
        photos: list[str | bytes | PhotosPhoto],
    ) -> list[str | list[dict]]:
        uploaded = []
        async for photo in async_list_generator(photos):
            data = await VKHandler.upload_image(photo)
            uploaded.append(data)
        return uploaded

    @staticmethod
    async def get_user_info(
        user: str,
        name_case: Optional[Literal["nom", "gen", "dat", "acc", "ins", "abl"]] = None,
        fields: Optional[list[str]] = None,
    ) -> UserInfo:
        matched = await get_id_from_text(user)
        if not matched:
            raise ObjectInformationReError

        if LinkHandler.is_group(matched):
            raise InvalidObjectRequestError

        if fields is None:
            fields = ["screen_name"]
        if "screen_name" not in fields:
            fields.append("screen_name")
        try:
            info = await api.users.get(matched, fields, name_case)
        except VKAPIError:
            raise VKAPIRequestError

        if not info:
            raise ObjectInformationRequestError(f"{user=}")

        return UserInfo(**info[0].dict())

    @staticmethod
    async def get_group_info(
        group: str, fields: Optional[list[str]] = None
    ) -> GroupInfo:
        matched = await get_id_from_text(group)
        if not matched:
            raise ObjectInformationReError

        if not LinkHandler.is_group(matched):
            raise InvalidObjectRequestError

        if fields is None:
            fields = ["screen_name"]
        if "screen_name" not in fields:
            fields.append("screen_name")
        try:
            info = await api.groups.get_by_id(group_id=matched, fields=fields)
        except VKAPIError:
            raise ObjectInformationRequestError

        if not info:
            raise ObjectInformationRequestError(f"{group=}")

        return GroupInfo(**info[0].dict())

    @staticmethod
    async def get_object_info(url: str) -> ObjectInfo:
        """Returns an object info from a given url

        :param url: url to get object info
        :return: ObjectInfo or raises ObjectInformationRequestError
        """
        is_user = None
        is_group = None
        try:
            is_group = await VKHandler.get_group_info(url)
        except (ObjectInformationRequestError, InvalidObjectRequestError):
            is_user = await VKHandler.get_user_info(url)

        if is_user is None and is_group is None:
            raise ObjectInformationRequestError

        response = {
            "object": is_group or is_user,
            "is_group": bool(is_group),
        }
        return ObjectInfo(**response)

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
    async def post(**kwargs) -> PostResponseModel:
        return await api.wall.post(owner_id=ban_reason_group_id, **kwargs)

    @staticmethod
    async def get_posts(count: int = 1, **kwargs) -> list:
        posts = await api.wall.get(owner_id=ban_group_id, count=count, **kwargs)
        return posts.items

    @staticmethod
    async def get_comments(**kwargs) -> GetCommentsResponseModel:
        return await api.wall.get_comments(owner_id=ban_group_id, sort="desc", **kwargs)

    @staticmethod
    async def send_message(user_id: int, message: str, *args, **kwargs) -> int:
        return await api.messages.send(
            user_id=user_id,
            message=message,
            random_id=0,
            *args,
            **kwargs,
        )

    @staticmethod
    async def get_short_link(link: str) -> str:
        result = await api.utils.get_short_link(url=link, private=1)
        return result.short_url

    @staticmethod
    async def get_short_links(links: list[str]) -> list[str]:
        return [await VKHandler.get_short_link(link) for link in links]

    @staticmethod
    async def get_photos(photos: str | list) -> list[PhotosPhoto]:
        """Returns photos data from VK

        :param photos: each photo should be in format "photo<owner>_<photo_id>_<access_key>"
        """
        if isinstance(photos, str):
            photos = [photos.removeprefix("photo")]
            result = await api.photos.get_by_id(photos)
            return result[0]
        return await api.photos.get_by_id(
            [photo.removeprefix("photo") for photo in photos]
        )
