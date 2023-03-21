import asyncio
from time import time
from typing import NoReturn

from helpfuncs import VKHandler
from loguru import logger
from vkbottle.user import Message, UserLabeler
from wordsdetector import AIHandler, AIState, BadWordsDetector

from .rules import CheckPermissions, Groups, Rights

ai = BadWordsDetector()
ai_handler = AIHandler()
ai_labeler = UserLabeler()
ai_labeler.vbml_ignore_case = True
ai_labeler.custom_rules["access"] = CheckPermissions


@ai_labeler.message(
    access=[Groups.MODERATOR, Rights.MIDDLE],
    text="ai_add <level> <text>",
)
async def ai_add_text(message: Message, level: int, text: str) -> None:
    await ai.add_text_data(text, float(level))
    await message.answer("ok")


@ai_labeler.message(
    access=[Groups.MODERATOR, Rights.MIDDLE],
    text="ai_test <text>",
)
async def ai_test(message: Message, text: str) -> None:
    predictions = await ai.predict(text)
    await message.answer(
        "AI predictions:\n"
        + ("No violations" if predictions == 0 else "Violated comment(-s)")
    )


@ai_labeler.private_message(
    access=[Groups.MODERATOR, Rights.ADMIN],
    text="ai_switch",
)
async def ai_switch_state(message: Message) -> None:
    state = ai_handler.switch()
    await message.answer(f"ai state: {state.name}")


@ai_labeler.message(
    access=[Groups.MODERATOR, Rights.ADMIN],
    text="ai_train",
)
async def ai_train(message: Message) -> None:
    await message.answer("Пробую...")
    try:
        await ai.train()
    except Exception as e:
        await message.answer("Произошла ошибка при попытке обучить нейросеть\n" + e)
        raise
    else:
        await message.answer("Нейросеть переобучилась")


async def ai_activate() -> NoReturn:
    last_state = None
    while True:
        state = ai_handler.state
        logger.debug("AI | Checking state")
        logger.debug(
            f"AI | Last state: {AIState(last_state).name if last_state else 'no state'}"
        )
        logger.debug(f"AI | Current state: {AIState(state).name}")
        last_state = state
        if not state.value:
            await asyncio.sleep(300)
            continue

        start_time = time()
        posts = await VKHandler.get_posts(5)
        detected_comments = []
        for post in posts:
            comments = await VKHandler.get_comments(post_id=post.id, count=100)
            comments = comments.items
            predictions = await asyncio.gather(
                *[ai.predict(comment.text) for comment in comments]
            )
            for comment, prediction in zip(comments, predictions):
                if prediction == 0:
                    continue
                detected_comments.append(
                    {
                        "post_id": post.id,
                        "id": comment.id,
                        "text": comment.text,
                    }
                )
        results = [
            f"{comment['text']}\n"
            + f"https://vk.com/wall-49033185_{comment['post_id']}?reply={comment['id']}\n"
            for comment in detected_comments
        ]
        end_time = time()
        if detected_comments:
            elapsed_time = end_time - start_time
            text_template = (
                f"Elapsed time: {elapsed_time:.2f} seconds\n"
                + f"AI found {len(results)} violent comments:\n"
                + "\n".join(results)
            )
            await VKHandler.send_message(
                peer_id=2000000001,
                random_id=0,
                message=text_template,
            )
        await asyncio.sleep(900)
