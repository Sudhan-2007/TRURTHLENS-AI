from enum import Enum


class HistorySort(str, Enum):
    CREATED_DESC = "created_desc"
    CREATED_ASC = "created_asc"
