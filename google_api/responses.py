from dataclasses import dataclass


@dataclass
class OkResponse:
    spreadsheet_id: str
    updated_cells: int
    updated_columns: int
    updated_range: str
    updated_rows: int
