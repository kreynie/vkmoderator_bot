from vkbottle.user import Message, rules, UserLabeler

from src.helpfuncs import vkfunctions as vkf
from src.schemas import stuff, user
from src.services.stuffs import StuffsService
from src.utils.dependencies import UOWDep
from src.utils.enums import ChatPeers, ReactionIDs, StuffGroups, chat_ids
from src.utils.exceptions import handle_errors_decorator
from src.utils.unitofwork import IUnitOfWork
from asyncio import sleep as async_sleep

chat_actions_labeler = UserLabeler()
primary_chat = chat_ids.news
primary_chat_peer_enum = ChatPeers.NEWS


@chat_actions_labeler.chat_message(
    peer_ids=primary_chat_peer_enum.value,
    text="<invited_user> МВ<( )#key:int><!>",
)
@handle_errors_decorator(send_answer_message=False)
async def add_new_stuff(
        message: Message,
        invited_user: str,
        key: int,
        uow: IUnitOfWork = UOWDep,
) -> None:
    try:
        user_info = await vkf.get_user_info(invited_user)
        new_user_schema = user.UserCreateSchema(**user_info.dict())
        new_moderator_schema = stuff.StuffCreateSchema(
            user_id=user_info.id, group_id=StuffGroups.MODERATOR.value, key=key, allowance=1
        )
        complete_schema = stuff.StuffCompleteCreateSchema(
            user_create_info=new_user_schema,
            stuff_create_info=new_moderator_schema,
        )
        await StuffsService().add_stuff(uow, complete_schema)

        for chat_id in chat_ids.dict().values():
            if primary_chat_peer_enum.value % chat_id == 20:  # skip same chat (i.e. 2000000001 % 1 = 20)
                continue

            await vkf.invite_chat_user(chat_id=chat_id, user_id=user_info.id)
            await async_sleep(1.5)

        await vkf.send_reaction(
            peer_id=primary_chat_peer_enum.value,
            conversation_message_id=message.conversation_message_id,
            reaction_id=ReactionIDs.THUMB_UP.value,
        )
    except Exception:
        await vkf.send_reaction(
            peer_id=primary_chat_peer_enum.value,
            conversation_message_id=message.conversation_message_id,
            reaction_id=ReactionIDs.QUESTION_MARKS.value,
        )
        raise


@chat_actions_labeler.chat_message(
    rules.ChatActionRule("chat_kick_user"),
    peer_ids=primary_chat_peer_enum.value,
)
@handle_errors_decorator(send_answer_message=False)
async def remove_stuff(message: Message, uow: IUnitOfWork = UOWDep) -> None:
    user_id = message.action.member_id
    stuff_info = await StuffsService().get_stuff_by(uow, user_id=user_id, group_id=StuffGroups.MODERATOR.value)
    stuff_schema = stuff.StuffDeleteSchema(id=stuff_info.id)
    await StuffsService().delete_stuff(uow, stuff_schema)
    for chat_id in chat_ids.dict().values():
        if primary_chat_peer_enum.value % chat_id == 20:  # skip same chat (i.e. 2000000001 % 1 = 20)
            continue

        await vkf.remove_chat_user(chat_id=chat_id, member_id=user_id)
        await async_sleep(1.5)

    await vkf.edit_manager(user_id=user_id, remove=True)
