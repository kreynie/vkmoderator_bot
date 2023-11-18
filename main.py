from src.vkbottle_config import vk_labeler, vk_user_bot
from src.blueprints import labelers
from src.loop_wrappers import vk_loop_wrapper

for labeler in labelers:
    vk_labeler.load(labeler)


if __name__ == "__main__":
    vk_user_bot.loop_wrapper = vk_loop_wrapper
    vk_user_bot.run_forever()
