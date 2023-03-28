from typing import Optional

from config import credentials_path, legal_db, spreadsheet
from google_api import GoogleSheetAPI
from helpfuncs import VKHandler
from helpfuncs.functions import PhotoHandler, ReformatHandler
from vkbottle.user import Message, UserLabeler

from .rules import CheckPermissions, Groups, Rights

lt_labeler = UserLabeler()
lt_labeler.vbml_ignore_case = True
lt_labeler.custom_rules["access"] = CheckPermissions


@lt_labeler.private_message(
    access=[Groups.LEGAL, Rights.LOW],
    text=[
        "ЛТ <violator_link> <reason> <violation_link> <game> <flea:int>",
        "ЛТ <violator_link> <reason> <violation_link> <game> <dialog_time>",
        "ЛТ <violator_link> <reason> <violation_link> <game>",
        "ЛТ <violator_link> <reason> <game>",
    ],
)
async def legal_helper(
    message: Message,
    violator_link: str = None,
    reason: str = None,
    violation_link: Optional[str] = None,
    game: str = None,
    flea: int = 0,
    dialog_time: Optional[str] = None,
) -> None:
    is_group, violator = await VKHandler.get_object_info(violator_link)

    if violator is None:
        await message.answer(
            "Не удалось найти информацию о группе (пользователе) по ссылке"
        )
        return

    reason = await ReformatHandler.legal(
        type_="abbreviations", abbreviation=reason.lower()
    )
    if reason is None:
        await message.answer(
            "Не удалось расшифровать причину."
            + 'Введи "ЛТСокращения" (регистр букв не учитывается)'
        )
        return

    game = await ReformatHandler.legal(type_="games", abbreviation=game.lower())
    if game is None:
        await message.answer(
            "Не удалось расшифровать игру. "
            + "Доступные: \n"
            + "• блиц - Tanks Blitz \n"
            + "• бб - Мир танков \n"
            + "• корабли - Мир кораблей"
        )
        return

    await message.answer("Начинаю обработку...")

    pinned_screenshot = message.get_photo_attachments()
    screenshot = None
    if not pinned_screenshot:
        if violation_link is None:
            screenshot = await PhotoHandler.screenshot(violator_link)
        else:
            screenshot = await PhotoHandler.screenshot(violation_link, wallpost=True)

    if not bool(screenshot) and not bool(pinned_screenshot):
        await message.answer(
            "Нет скриншота, либо не удалось его получить. Прикрепи его вручную"
        )
        return

    if pinned_screenshot:
        uploaded_image = await VKHandler.upload_image(pinned_screenshot[0])
    else:
        uploaded_image = await VKHandler.upload_image(screenshot)
    del screenshot, pinned_screenshot

    flea = "TRUE" if flea == 1 else "FALSE"
    moderator = await legal_db.get_user_by_id(message.from_id)

    photo_data = await VKHandler.get_photos(uploaded_image)
    photo_link = await PhotoHandler.get_photo_max_size_url(photo_data.sizes)
    short_screenshot_link = await VKHandler.get_short_link(photo_link)
    violator_link = "https://vk.com/" + ("club" if is_group else "id")
    original_violator_link = f"{violator_link}{violator.id}"
    violator_screen_name = f"https://vk.com/{violator.screen_name}"

    formatted_row = await ReformatHandler.sheets_row(
        is_group,
        violator_link=original_violator_link,
        violator_screen_name=violator_screen_name,
        reason=reason,
        violation_link=violation_link,
        screenshot_link=short_screenshot_link,
        game=game,
        moderator_key=str(moderator.key),
        flea=flea,
        dialog_time=dialog_time,
    )
    sheet_name = "Сообщества (2023)" if is_group else "Пользователи (2023)"
    async with GoogleSheetAPI(credentials_path, spreadsheet) as g_api:
        update = await g_api.update_last_row(
            f"{sheet_name}!A:K",
            formatted_row.split("+"),
        )
    await message.answer(
        "Обновлено:\n"
        + f"Лист: {update.updated_range}\n"
        + f"Количество изменённых ячеек: {update.updated_cells}"
    )
