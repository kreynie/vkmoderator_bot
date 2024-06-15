from .loop_wrapper import vk_loop_wrapper
from src.vkbottle_config import vk_api
from config import logger


@vk_loop_wrapper.interval(minutes=5)
async def update_account_online() -> None:
    logger.debug(f"Updating account's online")
    await vk_api.account.set_online(voip=False)
