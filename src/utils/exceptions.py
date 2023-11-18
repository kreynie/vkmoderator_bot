from functools import wraps
import typing

from vkbottle import VKAPIError

from src.database import exceptions as db_exc
from config import logger

if typing.TYPE_CHECKING:
    from vkbottle.user import Message


class InformationError(Exception):
    def __init__(self, e: typing.Optional[str] = None):
        self.error_description = e

    def __str__(self):
        return f"{self.__class__.__name__} occurred" + (
            f": {self.error_description}" if self.error_description else ""
        )

    def __repr__(self):
        return self.__str__()


class ObjectInformationReError(InformationError):
    pass


class ObjectInformationRequestError(InformationError):
    pass


class InvalidObjectRequestError(InformationError):
    pass


def handle_errors_decorator(
        send_answer_message: bool = True,
        custom_exc: dict[Exception, str] | None = None,
        *func_args, **func_kwargs
):
    if custom_exc is None:
        custom_exc = {}

    def decorator(func):
        @wraps(func)
        async def wrapped(message: "Message", *args, **kwargs):
            message_answer = handle_message_sender(send_answer_message, message)
            try:
                result = await func(message, *args, *func_args, **kwargs, **func_kwargs)
                return result
            except ObjectInformationReError:
                reply = "Ссылка на страницу должна быть полной и корректной"
                await message_answer(reply)
            except ObjectInformationRequestError:
                reply = "Не удалось найти информацию об объекте по указанной ссылке"
                await message_answer(reply)
            except VKAPIError as e:
                provided_vk_api_errors = {
                    exc: exc_message for exc, exc_message in custom_exc if isinstance(exc, VKAPIError)
                } if custom_exc else {}
                provided_vk_api_errors.update(
                    {VKAPIError: f"Ошибка при выполнении VK API запроса\n{e.code} - {e.description}"}
                )
                await handle_custom_exceptions(message_answer, e, provided_vk_api_errors)
            except db_exc.EntityAlreadyExists:
                reply = "Объект уже есть в базе данных"
                await message_answer(reply)
            except db_exc.EntityDoesNotExist:
                reply = "Объект не записан в базе данных"
                await message_answer(reply)
            except db_exc.DatabaseException as e:
                reply = "Ошибка во время транзакции в базе данных"
                await message_answer(reply)
                logger.opt(exception=True).exception(e)
            except Exception as e:
                await handle_custom_exceptions(message_answer, e, custom_exc)

        return wrapped

    return decorator


def handle_message_sender(
        send: bool, message: "Message",
) -> typing.Callable[[str], typing.Coroutine[..., ..., None]]:
    async def inner(text: str) -> None:
        if send:
            await message.answer(text)

    return inner


async def handle_custom_exceptions(
        message_sender_handler,
        exc,
        custom_exc: dict[Exception, str],
):
    if exc not in custom_exc:
        await message_sender_handler(f"Произошла неизвестная ошибка")
        logger.opt(exception=True).exception(exc)
    for custom_error, custom_error_message in custom_exc.items():
        if isinstance(exc, custom_error):  # type: ignore
            await message_sender_handler(custom_error_message or str(exc))
