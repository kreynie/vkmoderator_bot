from asyncio import sleep as asleep
from loguru import logger
from vkbottle import VKAPIError
from vkbottle.user import Message, UserLabeler

from .rules import CheckRights, Rights
from helpfuncs.functions import CommentsHandler
from helpfuncs.vkfunctions import get_last_post, get_comments, send_message


from wordsdetector import BadWordsDetector, AIState, AIHandler


ai = BadWordsDetector()
ai_handler = AIHandler()
ai_labeler = UserLabeler()
ai_labeler.vbml_ignore_case = True
ai_labeler.custom_rules["access"] = CheckRights


@ai_labeler.private_message(
    access=Rights.admin,
    text="ai_switch",
)
async def ai_switch_state(message: Message):
    status = await ai_handler.switch_ai_state()
    await message.answer(f"ai status: {status.name}")


@ai_labeler.private_message(
    access=Rights.admin,
    text="ai_add_text <level> <text>",
)
async def ai_add_text(message: Message, level: int, text: str):
    await ai.add_text_data(text, float(level))
    await message.answer("ok")


async def ai_train():
    last_state = None
    while True:
        state = await ai_handler.get_ai_state()
        logger.info("AI | Checking state")
        logger.info(
            "AI | Last state: {}".format(
                "no state" if last_state is None else last_state
            )
        )
        logger.info("AI | Current state: {}".format(AIState(state).name))
        if state:
            if state != last_state:
                await send_message(651285022, 0, message="AI training started")
            try:
                post_id = await get_last_post()
                comments = await get_comments(post_id=post_id.id)
                comment_handler = CommentsHandler(comments)
                random_comment = (
                    await comment_handler.get_random_text_from_comments(),
                )
                if random_comment:
                    predictions = tuple(await ai.predict(random_comment))
                    await send_message(
                        651285022,
                        0,
                        message=f"AI results in comment [{predictions[0]}]:\n{random_comment[0]}",
                    )
            except VKAPIError as e:
                await asleep(5)
                await send_message(
                    651285022, 0, message=f"Failed\n{e.code}: {e.description}"
                )
        last_state = state
        await asleep(600)
