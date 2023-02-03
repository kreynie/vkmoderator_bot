from os import getenv
from vkbottle import API
from vkbottle.user import UserLabeler

token = getenv("VKToken")
api = API(token=token)

labeler = UserLabeler()

banGroupID = -49033185  # -49033185
banReasonGroupID = -112433737  # -112433737
testID = -200352287
