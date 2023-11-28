from typing import TypeAlias

from vkbottle.user import Message
from vkbottle_types.objects import PhotosPhoto

from config import settings
from src.blueprints import rules
from src.google_api import GoogleSheetAPI
from src.helpfuncs import functions as funcs, vkfunctions as vkf
from src.schemas import VKObjectInfo
from src.schemas.registration import LegalBanRegistrationInfo
from src.services.stuffs import StuffsService
from src.utils.dependencies import UOWDep
from src.utils.enums import SheetsNames
from src.utils.exceptions import handle_errors_decorator
from src.utils.unitofwork import IUnitOfWork
from .base_labeler import labeler

UploadResult: TypeAlias = tuple[str | None, str | None]
ViolatorLinks: TypeAlias = tuple[str, str | None]


@labeler.private_message(
    access=[rules.StuffGroups.LEGAL, rules.Rights.LOW],
    text=funcs.split_for_text_for_command("ЛТ <violator_link> <reason> <violation_link> <game> <flea:int>"),
)
@handle_errors_decorator()
async def legal_helper(
    message: Message,
    violator_link: str | None = None,
    reason: str | None = None,
    violation_link: str | None = None,
    game: str | None = None,
    flea: int | None = None,
    dialog_time: str | None = None,
) -> None:
    if game is None:
        return await message.answer("Не указан проект, в котором произошло нарушение")
    if violation_link is None:
        return await message.answer("Нет ссылки на нарушение")
    if reason is None:
        return await message.answer("Нет причины")
    if violator_link is None:
        return await message.answer("Нет ссылки на нарушителя")
    if flea is not None and flea not in (0, 1):
        return await message.answer("Флаг <flea> может быть только 0 или 1")

    photo_attachment = message.get_photo_attachments()
    if photo_attachment is None:
        return await message.answer("Нет прикрепленного фото нарушения")

    await message.answer("Минутку...")

    result, return_reason = await process_legal_request(
        dialog_time=dialog_time,
        flea=flea,
        game=game,
        moderator_vk_id=message.from_id,
        photo_attachment=photo_attachment[0],
        reason=reason,
        violation_link=violation_link,
        violator_link=violator_link,
    )

    if return_reason is not None:
        return await message.answer(return_reason)
    await message.answer(result)


async def process_legal_request(
    dialog_time: str | None,
    flea: int | None,
    game: str,
    moderator_vk_id: int,
    photo_attachment: PhotosPhoto,
    reason: str,
    violation_link: str | None,
    violator_link: str,
    uow: IUnitOfWork = UOWDep,
) -> UploadResult:
    target = await vkf.get_object_info(violator_link)

    reason_full, game_full = await get_legal_abbreviations(reason.lower(), game.lower())

    if reason_full is None:
        return (
            None,
            'Не удалось расшифровать причину. Введи "ЛТСокр" (регистр букв не учитывается)',
        )
    if game_full is None:
        return (
            None,
            'Не удалось расшифровать игру. Введи "ЛТСокр" (регистр букв не учитывается)',
        )

    moderator = await StuffsService().get_stuff_by(
        uow,
        user_id=moderator_vk_id,
        group_id=rules.StuffGroups.LEGAL.value,
    )

    uploaded_photo = await vkf.upload_image(photo_attachment)
    uploaded_photo_data = await vkf.get_photos(uploaded_photo)
    uploaded_photo_link = funcs.get_photo_max_size_url(uploaded_photo_data.sizes)
    short_screenshot_link = await vkf.get_short_link(uploaded_photo_link)
    violator_link, violator_screen_name = get_violator_links(target)

    if flea is not None:
        flea = ["FALSE", "TRUE"].pop(flea)

    registration_parameters = LegalBanRegistrationInfo(
        dialog_time=dialog_time,
        flea=flea,
        game=game_full,
        is_group=target.is_group,
        moderator_key=str(moderator.key),
        reason=reason_full,
        screenshot_link=short_screenshot_link,
        violation_link=violation_link,
        violator_link=violator_link,
        violator_screen_name=violator_screen_name,
    )
    formatted_row = funcs.get_sheets_row(registration_parameters)
    sheet_name = SheetsNames.groups if target.is_group else SheetsNames.users
    async with GoogleSheetAPI(settings.google_api.credentials_path, settings.google_api.spreadsheet) as g_api:
        update = await g_api.update_last_row(
            f"{sheet_name.value}!A:K",
            formatted_row,
        )
    return f"Обновлено: {update.updated_range}\n", None


async def get_legal_abbreviations(reason: str, game: str):
    reason = funcs.get_legal_abbreviation_text(
        abbreviation_type="abbreviations",
        abbreviation=reason,
    )
    game_full = funcs.get_legal_abbreviation_text(
        abbreviation_type="games",
        abbreviation=game,
    )
    return reason, game_full


def get_violator_links(target: VKObjectInfo) -> ViolatorLinks:
    violator_type = "club" if target.is_group else "id"
    original_violator_link = f"https://vk.com/{violator_type}{target.object.id}"
    violator_screen_name = f"https://vk.com/{target.object.screen_name}"
    return original_violator_link, violator_screen_name
