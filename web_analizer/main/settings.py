from main.core_models import RegionBase

class AppSettings:    
    LOCAL_DATA_DIR: str = "./input"
    LOCAL_SOURCE: str = "local"
    WORLDBANK_SOURCE: str = "worldbank"
    DATABASE_SOURCES: list[str] = []
    REGIONS: list[RegionBase] = [
        RegionBase(code="ru", name="Российская Федерация")
    ]

    REGIONS_DICT: dict[str, list[RegionBase]] = { region.code.lower(): region for region in REGIONS}