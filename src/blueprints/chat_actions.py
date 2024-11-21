from vkbottle import VKAPIError
from vkbottle.user import Message, rules, UserLabeler
from vkbottle_types.codegen.objects import MessagesChatFull

from src.helpfuncs import vkfunctions as vkf
from src.schemas import stuff, user
from src.services.stuffs import StuffsService
from src.utils.dependencies import UOWDep
from src.utils.enums import ChatPeers, ReactionIDs, StuffGroups, chat_ids
from src.utils.unitofwork import IUnitOfWork
from asyncio import sleep as async_sleep

chat_actions_labeler = UserLabeler()
primary_chat = chat_ids.news
primary_chat_peer_enum = ChatPeers.NEWS


@chat_actions_labeler.chat_message(
    peer_ids=primary_chat_peer_enum.value,
    text="<invited_user> МВ<( )#key:int><!>",
)
async def add_new_stuff(
    message: Message,
    invited_user: str,
    key: int,
    uow: IUnitOfWork = UOWDep,
) -> None:
    user_info = await vkf.get_user_info(invited_user)

    try:
        complete_schema = stuff.StuffCompleteCreateSchema(
            user_create_info=user.UserCreateSchema(**user_info.dict()),
            stuff_create_info=stuff.StuffCreateSchema(
                user_id=user_info.id,
                group_id=StuffGroups.MODERATOR.value,
                key=key,
                allowance=1,
            ),
        )
        await StuffsService().add_stuff(uow, complete_schema)
    except Exception as e:
        await vkf.send_reaction(
            peer_id=primary_chat_peer_enum.value,
            conversation_message_id=message.conversation_message_id,
            reaction_id=ReactionIDs.QUESTION_MARKS.value,
        )
        await vkf.vk_api.messages.send(
            peer_id=ChatPeers.DED_CHAT.value,
            message=f"Не смог добавить @id{user_info.id} (пользователя) в базу бота.\nОшибка: {e}",
        )
        return

    invite_chat_ids = chat_ids.dict().values()
    invite_chat_ids_len = len(invite_chat_ids)
    failed_invite_chat_ids_tries = 0

    for chat_id in invite_chat_ids:
        if primary_chat == chat_id:
            continue

        chat_info: MessagesChatFull = await vkf.vk_api.messages.get_chat(
            chat_id=chat_id
        )

        try:
            await vkf.remove_chat_user(chat_id=chat_id, member_id=user_info.id)
        except VKAPIError:
            pass

        try:
            await vkf.invite_chat_user(chat_id=chat_id, user_id=user_info.id)
        except VKAPIError as e:
            await vkf.vk_api.messages.send(
                peer_id=ChatPeers.DED_CHAT.value,
                message=f"Не смог пригласить @id{user_info.id} (пользователя) в чат {chat_info.title}.\n"
                f"Ошибка: [{e.code}] {e.error_msg}",
                random_id=0,
            )
        await async_sleep(1.5)

    if failed_invite_chat_ids_tries == invite_chat_ids_len:
        await vkf.send_reaction(
            peer_id=primary_chat_peer_enum.value,
            conversation_message_id=message.conversation_message_id,
            reaction_id=ReactionIDs.QUESTION_MARKS.value,
        )
        return
    await vkf.send_reaction(
        peer_id=primary_chat_peer_enum.value,
        conversation_message_id=message.conversation_message_id,
        reaction_id=ReactionIDs.THUMB_UP.value,
    )


@chat_actions_labeler.chat_message(
    rules.ChatActionRule("chat_kick_user"),
    peer_ids=primary_chat_peer_enum.value,
)
async def remove_stuff(message: Message, uow: IUnitOfWork = UOWDep) -> None:
    user_id = message.action.member_id
    stuff_info = await StuffsService().get_stuff_by(
        uow,
        user_id=user_id,
        group_id=StuffGroups.MODERATOR.value,
    )
    stuff_schema = stuff.StuffDeleteSchema(id=stuff_info.id)
    await StuffsService().delete_stuff(uow, stuff_schema)
    for chat_id in chat_ids.dict().values():
        if primary_chat == chat_id:  # skip same chat
            continue

        await vkf.remove_chat_user(chat_id=chat_id, member_id=user_id)
        await async_sleep(1.5)

    await vkf.edit_manager(user_id=user_id, remove=True)
