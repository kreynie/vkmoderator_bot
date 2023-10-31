from functools import wraps
from typing import Optional, TYPE_CHECKING

from vkbottle import VKAPIError

if TYPE_CHECKING:
    from vkbottle.user import Message


class InformationError(Exception):
    def __init__(self, e: Optional[str] = None):
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


def handle_errors_decorator(func, custom_exc: Optional[dict[Exception, str]] = None):
    if custom_exc is None:
        custom_exc = {}

    @wraps(func)
    async def wrapped_function(message: "Message", *args, **kwargs):
        try:
            result = await func(message, *args, **kwargs)
            return result
        except ObjectInformationReError:
            await message.answer("Ссылка на страницу должна быть полной и корректной")
        except ObjectInformationRequestError:
            await message.answer(
                "Не удалось найти информацию об объекте по указанной ссылке"
            )
        except VKAPIError:
            await message.answer("Ошибка при выполнении VK API запроса")
        except Exception as e:
            if e not in custom_exc:
                await message.answer("Произошла неизвестная ошибка")
                raise
            for custom_error, custom_error_message in custom_exc.items():
                if isinstance(e, custom_error):
                    await message.answer(custom_error_message)

    return wrapped_function
