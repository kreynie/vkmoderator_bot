from datetime import datetime
from random import randint

from src.helpfuncs.hot_issues import hot_issues_processor
from src.schemas.hot_issues import HotIssueSchema
from src.utils.api_requests import fetch_active_issues
from src.utils.enums import ChatPeers
from src.vkbottle_config import vk_api
from .loop_wrapper import vk_loop_wrapper
from config import logger


async def startup_hot_issues_processor() -> None:
    await hot_issues_processor.initialize_cache()


@logger.catch
async def check_for_new_hot_issues():
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


vk_loop_wrapper.on_startup.append(startup_hot_issues_processor())


@vk_loop_wrapper.interval(minutes=get_next_interval_for_hot_issues_checkout())
async def check_hot_issues() -> None:
    await check_for_new_hot_issues()
    if hot_issues_processor.is_cache_updated:
        hot_issues_processor.is_cache_updated = False
        issue: HotIssueSchema = hot_issues_processor.last_hot_issue
        issue_url = f"https://lesta.ru/support/ru/products/wotb/hot-issues/{issue.id}/"
        send_chat_peer_id = ChatPeers.NEWS.value
        message = (f"{issue.title}\n"
                   f"Время публикации: {datetime.fromisoformat(issue.published):%d.%m.%Y в %H:%M }\n"
                   f"{issue_url}\n\n"
                   f"{issue.text}")
        await vk_api.messages.send(peer_id=send_chat_peer_id, message=message, random_id=0)
        logger.debug(f"New issue was sent to chat with peer id: {send_chat_peer_id}")
