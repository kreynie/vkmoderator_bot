import asyncio
from typing import Any

import aiohttp
from google.oauth2.service_account import Credentials
from googleapiclient.discovery import build

from .responses import OkResponse


class GoogleSheetAPI:
    def __init__(self, credentials_file, spreadsheet_id) -> None:
        self.creds = Credentials.from_service_account_file(credentials_file)
        self.service = build("sheets", "v4", credentials=self.creds)
        self.spreadsheet_id = spreadsheet_id
        self.session = aiohttp.ClientSession()

    async def __aenter__(self):
        return self

    async def __aexit__(self, exc_type, exc, tb) -> None:
        await self.session.close()

    async def get_values(self, list_range: str) -> list[list[str]] | None:
        async with self.session:
            request = (
                self.service.spreadsheets()
                .values()
                .get(
                    spreadsheetId=self.spreadsheet_id,
                    range=list_range,
                    majorDimension="ROWS",
                )
            )
            response = await asyncio.to_thread(request.execute)
        return response.get("values") if response else None

    async def get_last_row(self, list_range: str, left_column: str = "A") -> str:
        spreadsheet = await self.get_values(list_range)
        last_row = 1
        for row_id, row in enumerate(spreadsheet):
            last_row = row_id + 1
            if len(row) <= 2:
                return self._refactor_range(list_range, last_row, left_column)
        return self._refactor_range(list_range, last_row, left_column)

    def _refactor_range(self, list_range: str, last_row: int, left_column: str) -> str:
        return f"{list_range[:-3]}{left_column}{last_row}:{list_range[-1]}{last_row}"

    async def append(self, list_range: str, *args) -> OkResponse:
        data = []
        for arg in args:
            try:
                iter(arg)
            except TypeError:
                data.append(arg)
            else:
                data.extend(arg)
        async with self.session:
            request = (
                self.service.spreadsheets()
                .values()
                .append(
                    spreadsheetId=self.spreadsheet_id,
                    range=list_range,
                    valueInputOption="USER_ENTERED",
                    body={"values": [data]},
                )
            )
            response = await asyncio.to_thread(request.execute)
        return OkResponse(
            spreadsheet_id=response.get("spreadsheetId"),
            updated_cells=response.get("updatedCells"),
            updated_columns=response.get("updatedColumns"),
            updated_range=response.get("updatedRange"),
            updated_rows=response.get("updatedRows"),
        )

    async def update(self, list_range: str, row: str | list[Any]) -> OkResponse:
        if isinstance(row, str):
            row = [row]

        async with self.session:
            request = (
                self.service.spreadsheets()
                .values()
                .update(
                    spreadsheetId=self.spreadsheet_id,
                    range=list_range,
                    valueInputOption="USER_ENTERED",
                    body={"values": [row]},
                )
            )
            response = await asyncio.to_thread(request.execute)
        return OkResponse(
            spreadsheet_id=response.get("spreadsheetId"),
            updated_cells=response.get("updatedCells"),
            updated_columns=response.get("updatedColumns"),
            updated_range=response.get("updatedRange"),
            updated_rows=response.get("updatedRows"),
        )

    async def update_last_row(
        self, list_range: str, data: str | list[Any]
    ) -> OkResponse:
        last_row = await self.get_last_row(list_range, "B")
        response = await self.update(last_row, data)
        return response
