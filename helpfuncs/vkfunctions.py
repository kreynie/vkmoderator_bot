from re import match

from vkbottle.tools import PhotoWallUploader

from config import api, banGroupID, banReasonGroupID


async def uploadImage(photo):
    return await PhotoWallUploader(api).upload(photo)


async def getUserInfo(text) -> dict:
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


async def banUser(*args):
    await api.groups.ban(abs(banGroupID), *args)


async def post(**kwargs):
    await api.wall.post(owner_id=banReasonGroupID, **kwargs)


async def get_last_post():
    post = await api.wall.get(owner_id=banGroupID, count=2)
    return post.items[1]


async def get_comments(**kwargs):
    comments = await api.wall.get_comments(banGroupID, sort="desc", **kwargs)
    return comments


async def send_message(*args, **kwargs):
    await api.messages.send(*args, **kwargs)
