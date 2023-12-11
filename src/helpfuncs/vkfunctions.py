from typing import Literal, Optional

from vkbottle import VKAPIError
from vkbottle.tools import PhotoWallUploader
from vkbottle_types.codegen.objects import GroupsGroupFull
from vkbottle_types.responses.photos import PhotosPhoto
from vkbottle_types.responses.wall import PostResponseModel

from config import groups_id_settings
from src.schemas import VKObjectInfo
from src.schemas.user import UserSchema
from src.utils.exceptions import (
    ObjectInformationReError,
    ObjectInformationRequestError,
)
from src.vkbottle_config import vk_api
from . import functions as funcs


async def upload_image(photo: str | bytes | PhotosPhoto) -> str:
    """
    Upload an image to VK servers and return the string attach to

    :param photo: String, bytes representing an image or PhotosPhoto object
    :return: String in format photo<owner_id>_<photo_id>
    """
    photo_uploader = PhotoWallUploader(vk_api)
    if isinstance(photo, PhotosPhoto):
        photo = await funcs.get_photo(photo)

    raw_photo = await photo_uploader.read(photo)
    file = photo_uploader.get_bytes_io(raw_photo)
    return await photo_uploader.upload(file)


async def upload_images(photos: list[str | bytes | PhotosPhoto]) -> list[str]:
    """
    Upload several images to VK servers and return list of strings attach to

    :param photos: List of string, bytes representing images or PhotosPhoto objects
    :return: List of string in format photo<owner_id>_<photo_id>
    """
    uploaded = []
    async for photo in funcs.async_list_generator(photos):
        data = await upload_image(photo)
        uploaded.append(data)
    return uploaded


async def get_user_info(
    user: str,
    name_case: Optional[Literal["nom", "gen", "dat", "acc", "ins", "abl"]] = None,
    fields: Optional[list[str]] = None,
) -> UserSchema:
    """
    Get VK user's page information

    :param user: Raw string containing mention or user's page link
    :param name_case: Case for declension of user's name and surname: "nom" — nominative (default), "gen" — genitive,
        "dat" — dative, "acc" — accusative, "ins" — instrumental, "abl" — prepositional
    :param fields: Profile fields to return. Sample values: "nickname", "screen_name", "sex", "bdate" (birthdate),
        "city", "country", "timezone", "photo", "photo_medium", "photo_big", "has_mobile", "contacts", "education",
        "online", "counters", "relation", "last_seen", "activity", "can_write_private_message", "can_see_all_posts",
        "can_post", "universities", "can_invite_to_chats"
    """
    matched = await funcs.get_id_from_text(user)
    if not matched:
        raise ObjectInformationReError

    fields = fields or ["screen_name"]
    if "screen_name" not in fields:
        fields.append("screen_name")

    info = await vk_api.users.get(matched, fields, name_case)

    if not info:
        raise ObjectInformationRequestError(f"{user=}")

    return UserSchema(**info[0].dict())


async def get_group_info(group: str, fields: Optional[list[str]] = None) -> GroupsGroupFull:
    """
    Get VK group's page information

    :param group: Raw string containing mention or group's page link
    :param fields: Group fields to return
    :return:
    """
    matched = await funcs.get_id_from_text(group)
    if not matched:
        raise ObjectInformationReError

    fields = fields or ["screen_name"]
    if "screen_name" not in fields:
        fields.append("screen_name")

    try:
        info = await vk_api.groups.get_by_id(group_id=matched, fields=fields)
    except VKAPIError:
        raise ObjectInformationRequestError

    if not info:
        raise ObjectInformationRequestError(f"{group=}")

    return info[0]


async def get_object_info(link: str) -> VKObjectInfo:
    """
    Returns an object's info from a given link or screen name

    :param link: link or screen name
    :return: ObjectInfo or raises ObjectInformationRequestError
    """
    is_group = True
    try:
        object_info = await get_group_info(link)
    except ObjectInformationRequestError:
        is_group = False
        object_info = await get_user_info(link)

    return VKObjectInfo(object=object_info, is_group=is_group)


async def ban(*args, **kwargs) -> int:
    return await vk_api.groups.ban(group_id=groups_id_settings.main_group, *args, **kwargs)


async def check_if_banned(user_id: int) -> bool:
    try:
        await vk_api.groups.get_banned(group_id=groups_id_settings.main_group, owner_id=user_id)
        return True
    except VKAPIError[104]:
        return False


async def post(**kwargs) -> PostResponseModel | None:
    try:
        return await vk_api.wall.post(owner_id=-groups_id_settings.ban_archive_group, **kwargs)
    except VKAPIError:
        return None


async def get_short_link(link: str) -> str:
    """
    Get a shortened version of the link

    :param link: link to shorten
    """
    result = await vk_api.utils.get_short_link(url=link, private=1)
    return result.short_url


async def get_photos(photos: str | list) -> PhotosPhoto | list[PhotosPhoto]:
    """
    Returns photos data from VK

    :param photos: each photo should be in format "photo<owner>_<photo_id>_<access_key>"
    """
    if isinstance(photos, str):
        photos = [photos.removeprefix("photo")]
        result = await vk_api.photos.get_by_id(photos)
        return result[0]
    return await vk_api.photos.get_by_id([photo.removeprefix("photo") for photo in photos])


async def send_reaction(peer_id: int, conversation_message_id: int, reaction_id: int):
    """
    Send a reaction to a conversation message

    :param peer_id: peer_id of the conversation
    :param conversation_message_id: local message id
    :param reaction_id: reaction id to be sent
    """
    await vk_api.request(
        method="messages.sendReaction",
        data={
            "peer_id": peer_id,
            "cmid": conversation_message_id,
            "reaction_id": reaction_id,
        },
    )


async def invite_chat_user(chat_id: int, user_id: int, visible_message_count: int | None = None):
    """
    Invites user to a chat

    :param chat_id: Chat ID
    :param user_id: User's ID to be added to the chat
    :param visible_message_count: Show invited user previous messages
    """
    await vk_api.messages.add_chat_user(chat_id=chat_id, user_id=user_id, visible_message_count=visible_message_count)


async def remove_chat_user(chat_id: int, user_id: int | None = None, member_id: int | None = None):
    """
    Remove a user from a chat

    :param chat_id: Chat ID
    :param user_id: User ID to be removed from the chat (mutually exclusive with member_id)
    :param member_id: Member ID to be removed from the chat (mutually exclusive with user_id)
    """
    assert not (user_id is None and member_id is None), "At least one of user_id or member_id must be provided"
    await vk_api.messages.remove_chat_user(chat_id=chat_id, user_id=user_id, member_id=member_id)


async def edit_manager(user_id: int, remove: bool = False):
    """
    Edit the manager role for a user in a group

    :param user_id: User ID to edit the manager role for
    :param remove: If True, remove the manager role; if False, set the editor role
    """
    role = "editor" if not remove else None
    await vk_api.groups.edit_manager(group_id=groups_id_settings.ban_archive_group, user_id=user_id, role=role)
