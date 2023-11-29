from pathlib import Path
import re
from datetime import datetime, date
import pandas as pd

from typing import Generator, Iterable

import main.constants as const
from main.settings import AppSettings
from main.models import DemographyEntry

_LOCAL_DATA_FILE_NAME_TEMPLATE: str = "{region}__{source}.csv"
_ALPHANUM_CHAR = "[A-Za-z0-9]"
_REGION_CAPTURE_GROUP: str = f"(?P<region>{_ALPHANUM_CHAR}*)"
_SOURCE_ALPHA_GROUP: str = f"(?P<source>{_ALPHANUM_CHAR}*)"

def get_local_region_codes() -> Generator[str, None, None]:
    if AppSettings.LOCAL_SOURCE is None:
        return

    file_name_template = str.format(_LOCAL_DATA_FILE_NAME_TEMPLATE, source=AppSettings.LOCAL_SOURCE, region="{region}")
    file_name_pattern = str.format(file_name_template, region="*")
    file_name_regex = re.compile(str.format(file_name_template, region=_REGION_CAPTURE_GROUP))
    local_files = _get_base_path().glob(file_name_pattern)
    for file_name in local_files:
        match = re.fullmatch(file_name_regex, file_name.name)
        if match is not None:
            yield match.group("region")

def get_local_data_file_path(region: str) -> Path:
    filename = str.format(_LOCAL_DATA_FILE_NAME_TEMPLATE, region=region, source=AppSettings.LOCAL_SOURCE)
    return _get_base_path().joinpath(filename)

def _get_base_path() -> Path:
    return Path(AppSettings.LOCAL_DATA_DIR)

def get_dates_from_timestamps(points: Iterable[pd.Timestamp]) -> set[date]:
    return { dt.date() for dt in points }

def series_to_entity(index: datetime, series: pd.Series, region: str, source: str) -> DemographyEntry:
    entity_fields = {field: series[column] for field, column in const.ENTITY_FIELD_TO_SERIES_COLUMN_MAP.items()}
    entity_fields[const.ENTITY_FIELD_FOR_SERIES_INDEX] = index
    for field, value in entity_fields.items():
        if not pd.notna(value):
            entity_fields[field] = None
    return DemographyEntry(region=region, source=source,  **entity_fields)

def entities_to_dataframe(entities: Iterable[DemographyEntry]) -> pd.DataFrame:
    data = [_entity_to_column_list(entity) for entity in entities]
    result = pd.DataFrame(data, columns=const.DATAFRAME_COLUMNS)
    result.set_index(const.DATAFRAME_INDEX_COLUMN, inplace=True)
    result.index = pd.to_datetime(result.index)
    return result

def _entity_to_column_list(entity: DemographyEntry) -> list:
    column_to_field_map = {column: field for field, column in const.ENTITY_FIELD_TO_SERIES_COLUMN_MAP.items()}
    column_to_field_map[const.DATAFRAME_INDEX_COLUMN] = const.ENTITY_FIELD_FOR_SERIES_INDEX
    return [getattr(entity, column_to_field_map[column]) for column in const.DATAFRAME_COLUMNS]
