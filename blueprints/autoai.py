from asyncio import sleep
from loguru import logger
from time import time
from vkbottle import VKAPIError
from vkbottle.user import Message, UserLabeler

from .rules import CheckRights, Rights
from helpfuncs.functions import CommentsHandler, async_list_generator
from helpfuncs.vkfunctions import VKHandler


from wordsdetector import BadWordsDetector, AIState, AIHandler


ai = BadWordsDetector()
ai_handler = AIHandler()
ai_labeler = UserLabeler()
ai_labeler.vbml_ignore_case = True
ai_labeler.custom_rules["access"] = CheckRights


@ai_labeler.private_message(
    access=Rights.supermoderator,
    text="ai_add <level> <text>",
)
async def ai_add_text(message: Message, level: int, text: str):
    await ai.add_text_data(text, float(level))
    await message.answer("ok")


@ai_labeler.private_message(
    access=Rights.supermoderator,
    text="ai_test <text>",
)
async def ai_add_text(message: Message, text: str):
    predictions = await ai.predict(text)
    await message.answer(
        "AI predictions:\n"
        + ("No violations" if predictions == 0 else "Violated comment")
    )


@ai_labeler.private_message(
    access=Rights.admin,
    text="ai_switch",
)
async def ai_switch_state(message: Message):
    state = ai_handler.switch()
    await message.answer(f"ai state: {state.name}")


@ai_labeler.private_message(access=Rights.admin, text="ai_train")
async def ai_train(message: Message):
    await message.answer("Пробую...")
    try:
        await ai.train()
    except Exception as e:
        await message.answer("Произошла ошибка при попытке обучить нейросеть\n" + e)
    else:
        await message.answer("Нейросеть переобучилась")


async def ai_activate():
    last_state = None
    while True:
        state = ai_handler.state
        logger.info("AI | Checking state")
        logger.info(
            "AI | Last state: {}".format(
                "no state" if last_state is None else AIState(last_state).name
            )
        )
        logger.info(f"AI | Current state: {AIState(state).name}")
        if state.value:
            try:
                start_time = time()
                posts = await VKHandler.get_posts(5)
                detected_comments = []
                async for post in async_list_generator(posts):
                    comments_raw = await VKHandler.get_comments(
                        post_id=post.id, count=100
                    )
                    async for comment in CommentsHandler.get_texts_from_comments(
                        comments_raw
                    ):
                        predictions = tuple(await ai.predict(comment["text"]))
                        if predictions > 0:
                            detected_comments.append(
                                {
                                    "post_id": post.id,
                                    "id": comment["id"],
                                    # "from_id": comment["from_id"],
                                    "text": comment["text"],
                                }
                            )
                results = [
                    f"▶️{comment['text']}\n"
                    + f"https://vk.com/wall-49033185_{comment['post_id']}?reply={comment['id']}\n"
                    for comment in detected_comments
                ]
                end_time = time()
                elapsed_time = end_time - start_time
                counted_time = f"Elapsed time: {elapsed_time:.2f} seconds\n"
                await VKHandler.send_message(
                    651285022,
                    0,
                    message=counted_time
                    + f"AI found {len(results)} violent comments:\n"
                    + "\n".join(results)
                    if detected_comments != []
                    else f"{counted_time}AI does not found violations",
                )
            except VKAPIError as e:
                await sleep(5)
                await VKHandler.send_message(
                    651285022, 0, message=f"Failed\n{e.code}: {e.description}"
                )
        last_state = state
        await sleep(900)
