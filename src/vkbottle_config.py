from vkbottle import API, User
from vkbottle.framework.labeler import UserLabeler

from config import settings

vk_api = API(token=settings.vk_api.token)
vk_labeler = UserLabeler()
vk_user_bot = User(api=vk_api, labeler=vk_labeler)
