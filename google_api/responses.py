from dataclasses import dataclass
from typing import Optional


@dataclass
class OkResponse:
    spreadsheet_id: Optional[str] = None
    updated_cells: Optional[int] = None
    updated_columns: Optional[int] = None
    updated_range: Optional[str] = None
    updated_rows: Optional[int] = None
