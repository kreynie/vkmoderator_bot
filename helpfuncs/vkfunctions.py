from typing import Literal, Optional

from vkbottle import VKAPIError
from vkbottle.tools import PhotoWallUploader
from vkbottle_types.responses.photos import PhotosPhoto
from vkbottle_types.responses.wall import PostResponseModel

from config import api, ban_group_id, ban_reason_group_id
from utils.exceptions import (
    ObjectInformationReError,
    ObjectInformationRequestError,
)
from utils.info_classes import GroupInfo, ObjectInfo, UserInfo
from . import functions as funcs
from .functions import async_list_generator, get_id_from_text


async def upload_image(photo: str | bytes | PhotosPhoto) -> str | list[dict]:
    if isinstance(photo, PhotosPhoto):
        photo = await funcs.get_photo(photo)
    return await PhotoWallUploader(api).upload(photo)


async def upload_images(
    photos: list[str | bytes | PhotosPhoto],
) -> list[str | list[dict]]:
    uploaded = []
    async for photo in async_list_generator(photos):
        data = await upload_image(photo)
        uploaded.append(data)
    return uploaded


async def get_user_info(
    user: str,
    name_case: Optional[Literal["nom", "gen", "dat", "acc", "ins", "abl"]] = None,
    fields: Optional[list[str]] = None,
) -> UserInfo:
    matched = await get_id_from_text(user)
    if not matched:
        raise ObjectInformationReError

    fields = fields or ["screen_name"]
    if "screen_name" not in fields:
        fields.append("screen_name")

    info = await api.users.get(matched, fields, name_case)

    if not info:
        raise ObjectInformationRequestError(f"{user=}")

    return UserInfo(**info[0].dict())


async def get_group_info(group: str, fields: Optional[list[str]] = None) -> GroupInfo:
    matched = await get_id_from_text(group)
    if not matched:
        raise ObjectInformationReError

    fields = fields or ["screen_name"]
    if "screen_name" not in fields:
        fields.append("screen_name")

    try:
        info = await api.groups.get_by_id(group_id=matched, fields=fields)
    except VKAPIError:
        raise ObjectInformationRequestError

    if not info:
        raise ObjectInformationRequestError(f"{group=}")

    return GroupInfo(**info[0].dict())


async def get_object_info(url: str) -> ObjectInfo:
    """Returns an object info from a given url

    :param url: url to get object info
    :return: ObjectInfo or raises ObjectInformationRequestError
    """
    is_group = True
    try:
        object_info = await get_group_info(url)
    except ObjectInformationRequestError:
        is_group = False
        object_info = await get_user_info(url)

    return ObjectInfo(object=object_info, is_group=is_group)


async def ban(*args, **kwargs) -> int:
    return await api.groups.ban(group_id=abs(ban_group_id), *args, **kwargs)


async def check_if_banned(user_id: int) -> bool:
    try:
        await api.groups.get_banned(group_id=abs(ban_group_id), owner_id=user_id)
        return True
    except VKAPIError[104]:
        return False


async def post(**kwargs) -> PostResponseModel | None:
    try:
        return await api.wall.post(owner_id=ban_reason_group_id, **kwargs)
    except VKAPIError:
        return None


async def get_short_link(link: str) -> str:
    result = await api.utils.get_short_link(url=link, private=1)
    return result.short_url


async def get_photos(photos: str | list) -> PhotosPhoto | list[PhotosPhoto]:
    """Returns photos data from VK

    :param photos: each photo should be in format "photo<owner>_<photo_id>_<access_key>"
    """
    if isinstance(photos, str):
        photos = [photos.removeprefix("photo")]
        result = await api.photos.get_by_id(photos)
        return result[0]
    return await api.photos.get_by_id([photo.removeprefix("photo") for photo in photos])
