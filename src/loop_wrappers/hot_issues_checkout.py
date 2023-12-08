from datetime import datetime
from random import randint

from src.helpfuncs.hot_issues import hot_issues_processor
from src.schemas.hot_issues import HotIssueSchema
from src.utils.api_requests import fetch_active_issues
from src.utils.enums import ChatPeers
from src.vkbottle_config import vk_api
from .loop_wrapper import vk_loop_wrapper
from config import logger


@logger.catch
async def check_for_new_hot_issues() -> HotIssueSchema | None:
    logger.debug("Checking for new hot issues...")
    new_issues = fetch_active_issues()
    logger.debug(f"Response status code: {new_issues.status_code}")
    if new_issues.status_code == 200:
        logger.debug("Response is ok, processing new issues...")
        return await hot_issues_processor.process_issues(new_issues.content)
    logger.debug("Bad response from Lesta ;( Maybe try again later")


def get_next_interval_for_hot_issues_checkout(
        minimum_minutes: int = 15, maximum_minutes: int = 25
) -> int:
    return randint(minimum_minutes, maximum_minutes)


@vk_loop_wrapper.interval(minutes=get_next_interval_for_hot_issues_checkout())
async def check_hot_issues() -> None:
    new_issue = await check_for_new_hot_issues()
    if new_issue is None:
        return

    issue_url = f"https://lesta.ru/support/ru/products/wotb/hot-issues/{new_issue.id}/"
    send_chat_peer_id = ChatPeers.NEWS.value
    message = (f"{new_issue.title}\n"
               f"Время публикации: {datetime.fromisoformat(new_issue.published):%d.%m.%Y в %H:%M }\n"
               f"{issue_url}\n\n"
               f"{new_issue.text}")
    await vk_api.messages.send(peer_id=send_chat_peer_id, message=message, random_id=0)
    logger.debug(f"New issue was sent to chat with peer id: {send_chat_peer_id}")
