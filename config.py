from os import getenv

from vkbottle import API
from vkbottle.user import UserLabeler

DEBUG = getenv("DEBUG", 0)
token = getenv("VKToken")
api = API(token=token)

labeler = UserLabeler()

if DEBUG:
    ban_group_id, ban_reason_group_id = -200352287, -200352287
else:
    ban_group_id, ban_reason_group_id = -49033185, -112433737
