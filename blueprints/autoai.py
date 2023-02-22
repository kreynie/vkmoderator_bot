from asyncio import sleep as asleep
from loguru import logger
from vkbottle import VKAPIError
from vkbottle.user import Message, UserLabeler

from .rules import CheckRights, Rights
from helpfuncs.functions import CommentsHandler, async_list_generator
from helpfuncs.vkfunctions import get_posts, get_comments, send_message


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
    status = await ai_handler.switch()
    await message.answer(f"ai status: {status.name}")


@ai_labeler.private_message(
    access=Rights.supermoderator,
    text="ai_add <level> <text>",
)
async def ai_add_text(message: Message, level: int, text: str):
    await ai.add_text_data(text, float(level))
    await message.answer("ok")


async def ai_activate():
    last_state = None
    while True:
        state = ai_handler.state
        logger.info("AI | Checking state")
        logger.info(
            "AI | Last state: {}".format(
                "no state" if last_state is None else last_state
            )
        )
        logger.info(f"AI | Current state: {AIState(state).name}")
        if state:
            if state != last_state:
                await send_message(651285022, 0, message="AI started")
            try:
                posts = await get_posts(5)
                comments = []
                detected_comments = []
                async for post in async_list_generator(posts):
                    comments_raw = await get_comments(post_id=post.id)
                    comments += await CommentsHandler.get_texts_from_comments(
                        comments_raw
                    )
                    for comment in comments:
                        predictions = tuple(await ai.predict(comment))
                        if predictions[0] > 0:
                            detected_comments.append(comment)
                print(detected_comments)
                await send_message(
                    651285022,
                    0,
                    message="AI results in comments:\n"
                    + "\n".join([comment for comment in detected_comments]),
                )
            except VKAPIError as e:
                await asleep(5)
                await send_message(
                    651285022, 0, message=f"Failed\n{e.code}: {e.description}"
                )
        last_state = state
        await asleep(600)
