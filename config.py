from os import getenv
from vkbottle import API
from vkbottle.user import UserLabeler

DEBUG = getenv("DEBUG", 0)
token = getenv("VKToken")
api = API(token=token)

labeler = UserLabeler()

if DEBUG:
    banGroupID = -200352287
    banReasonGroupID = -200352287
else:
    banGroupID = -49033185
    banReasonGroupID = -112433737
