from os import getenv

from vkbottle import API
from vkbottle.user import UserLabeler

from database import LegalTable, ModeratorTable, UsersTable

DEBUG = getenv("DEBUG", 0)
token = getenv("VKToken")
api = API(token=token)

labeler = UserLabeler()

db_file_name = "base.db"
users_db = UsersTable(db_file_name)
moderator_db = ModeratorTable(db_file_name)
legal_db = LegalTable(db_file_name)

if DEBUG:
    ban_group_id, ban_reason_group_id = -200352287, -200352287
else:
    ban_group_id, ban_reason_group_id = -49033185, -112433737
