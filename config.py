from os import getenv
from vkbottle import API
from vkbottle.user import UserLabeler

token = getenv("VKToken")
api = API(token=token)

labeler = UserLabeler()

banGroupID: int = -200352287  # -49033185
banReasonGroupID: int = -200352287  # -112433737
testID: int = -200352287
