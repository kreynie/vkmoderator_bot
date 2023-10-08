from vkbottle.user import User

from blueprints import labelers
from config import api, labeler

bot = User(api=api, labeler=labeler)

for level in labelers:
    labeler.load(level)


if __name__ == "__main__":
    bot.run_forever()
