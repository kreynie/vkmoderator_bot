from asyncio import sleep as asleep
from enum import Enum
from vkbottle import VKAPIError
from vkbottle.user import Message, UserLabeler

from .rules import CheckRights, Rights
from helpfuncs.functions import get_text_from_comments
from helpfuncs.vkfunctions import get_last_post, get_comments, send_message

from wordsdetector import BadWordsDetector


ai_labeler = UserLabeler()
ai_labeler.vbml_ignore_case = True
ai_labeler.custom_rules["access"] = CheckRights


ai = BadWordsDetector()


class AIState(Enum):
    DISABLED_STATE = 0
    ACTIVE_STATE = 1
    QUESTION_STATE = 2
    TRAINING_STATE = 3


ai_state = AIState.DISABLED_STATE


async def check_ai_state(state: AIState) -> bool:
    return ai_state == state


@ai_labeler.private_message(
    access=Rights.admin,
    text="ai_active",
)
async def ai_activate(message: Message):
    state = await check_ai_state(AIState.DISABLED_STATE)
    if state:
        ai_state = AIState.ACTIVE_STATE
        await message.answer(f"ai status: {ai_state} {ai_state.value}")


@ai_labeler.private_message(
    access=Rights.admin,
    text=[
        "ai_disable",
    ],
)
async def ai_disable(message: Message):
    state = await check_ai_state(AIState.ACTIVE_STATE)
    if state:
        ai_state = AIState.DISABLED_STATE
        await message.answer(f"ai status: {ai_state}")


@ai_labeler.private_message(
    access=Rights.admin,
    text="ai_add_text <level> <text>",
)
async def ai_add_text(message: Message, level: int, text: str):
    await ai.add_text_data(text, float(level))
    await message.answer("ok")


async def ai_train():
    state = await check_ai_state(AIState.ACTIVE_STATE)
    while True:
        if state:
            await send_message(651285022, 0, message="AI training started")
            try:
                post_id = await get_last_post()
                comments = await get_comments(post_id=post_id.id)
                last_comment = (await get_text_from_comments(comments),)
                if last_comment:
                    predictions = tuple(await ai.predict(last_comment))
                    await send_message(
                        651285022,
                        0,
                        message=f"AI results in comment [{predictions[0]}]:\n{last_comment[0]}",
                    )
            except VKAPIError as e:
                await asleep(5)
                await send_message(
                    651285022, 0, message=f"Failed\n{e.code}: {e.description}"
                )
        state = await check_ai_state(AIState.ACTIVE_STATE)
        await asleep(600)

