from re import match

from vkbottle.tools import PhotoWallUploader

from config import api, banGroupID, banReasonGroupID


async def upload_image(photo):
    return await PhotoWallUploader(api).upload(photo)


async def get_user_info(text) -> dict:
    matched = match(r".*vk.com/(.*)", text)
    if matched is not None:
        info = await api.users.get([matched.group(1)])
        if info != []:
            return {
                "first_name": info[0].first_name,
                "last_name": info[0].last_name,
                "id": info[0].id,
            }
    return None


async def ban(*args):
    await api.groups.ban(abs(banGroupID), *args)


async def post(**kwargs):
    await api.wall.post(owner_id=banReasonGroupID, **kwargs)


async def get_posts(count: int = 1):
    posts = await api.wall.get(owner_id=banGroupID, count=count)
    return posts.items


async def get_comments(**kwargs):
    comments = await api.wall.get_comments(owner_id=banGroupID, sort="desc", **kwargs)
    return comments


async def send_message(*args, **kwargs):
    await api.messages.send(*args, **kwargs)
