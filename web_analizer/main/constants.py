DATAFRAME_COLUMNS: list[str] = [ "Year", "N(t)", "B(t)", "D(t)", "NM(t)" ]
DATAFRAME_INDEX_COLUMN: str = "Year"
ENTITY_FIELD_TO_SERIES_COLUMN_MAP: dict[str, str] = {
    "total_population": "N(t)",
    "births": "B(t)",
    "deaths": "D(t)",
    "migration": "NM(t)"
}
ENTITY_FIELD_FOR_SERIES_INDEX: str = "year"