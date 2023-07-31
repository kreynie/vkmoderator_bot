from vkbottle.user import User

from blueprints import labelers
from config import api, labeler

bot = User(api=api, labeler=labeler)

for level in labelers:
    labeler.load(level)

bot.run_forever()
