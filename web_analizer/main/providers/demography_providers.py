import pandas as pd
from django.db.models import Min, Max
from abc import ABC, abstractmethod
import world_bank_data as wp

import main.constants as const
from main.models import DemographyEntry
from main.core_models import TimePeriod
from main.utils import get_local_data_file_path, entities_to_dataframe


class BaseProvider(ABC):
    source: str

    def __init__(self, source: str):
        self.source = source

    @abstractmethod
    def get_data(self, region: str, period: TimePeriod | None) -> pd.DataFrame | None:
        pass

    @abstractmethod
    def get_availible_period(self, region: str) -> TimePeriod | None:
        pass


class DatabaseProvider(BaseProvider):
    def get_data(self, region: str, period: TimePeriod | None) -> pd.DataFrame | None:
        filters = {
            "source": self.source,
            "region": region
        }
        if period is not None:
            filters["year__range"] = (period.start, period.end)
        manager = DemographyEntry.objects
        entities = manager.filter(**filters)
        return entities_to_dataframe(entities)

    def get_availible_period(self, region: str) -> TimePeriod | None:
        manager = DemographyEntry.objects
        entities = manager.filter(source=self.source, region=region).aggregate(Min("year", default=None), Max("year", default=None))
        start, end = entities["year__min"], entities["year__max"]
        return TimePeriod(start, end) if start is not None and end is not None else None

class CSVFilesProvider(BaseProvider):
    def get_data(self, region: str, period: TimePeriod | None) -> pd.DataFrame | None:
        filepath = get_local_data_file_path(region)
        if not filepath.exists():
            return None

        all_data = pd.read_csv(filepath, names=const.DATAFRAME_COLUMNS, index_col=const.DATAFRAME_INDEX_COLUMN)
        return all_data.loc[period.start : period.end] if period is not None else all_data
    
    def get_availible_period(self, region: str) -> TimePeriod | None:
        data = self.get_data(region, period=None)
        if data is None or data.shape[0] == 0:
            return None
        
        start, end = data.index.min(), data.index.max()
        return TimePeriod(start, end)
    

class WorldBankProvider(BaseProvider):
    _TOTAL_POPULATION_INDICATOR_CODE = "SP.POP.TOTL"
    _CRUDE_BIRTH_RATE_INDICATOR_CODE = "SP.DYN.CBRT.IN"
    _CRUDE_DEATH_RATE_INDICATOR_CODE = "SP.DYN.CDRT.IN"
    _NET_MIGRATION_INDICATOR_CODE = "SM.POP.NETM"
    _INDEX_COLUMN = "Year"

    def get_data(self, region: str, period: TimePeriod | None) -> pd.DataFrame | None:
        total_population = wp.get_series(self._TOTAL_POPULATION_INDICATOR_CODE, country=region)
        crude_birth_rate = wp.get_series(self._CRUDE_BIRTH_RATE_INDICATOR_CODE, country=region)
        crude_death_rate = wp.get_series(self._CRUDE_DEATH_RATE_INDICATOR_CODE, country=region)
        migration = -wp.get_series(self._NET_MIGRATION_INDICATOR_CODE, country=region)

        result = pd.merge(total_population, crude_birth_rate, on=self._INDEX_COLUMN)
        result = pd.merge(result, crude_death_rate, on=self._INDEX_COLUMN)
        result = pd.merge(result, migration, on=self._INDEX_COLUMN)
        result["Births"] = (result[self._CRUDE_BIRTH_RATE_INDICATOR_CODE] * result[self._TOTAL_POPULATION_INDICATOR_CODE] / 1000).round()
        result["Deaths"] = (result[self._CRUDE_DEATH_RATE_INDICATOR_CODE] * result[self._TOTAL_POPULATION_INDICATOR_CODE] / 1000).round()
        columns = [self._TOTAL_POPULATION_INDICATOR_CODE, "Births", "Deaths", self._NET_MIGRATION_INDICATOR_CODE]
        result = result[columns]
        new_columns = list(const.DATAFRAME_COLUMNS)
        new_columns.remove(const.DATAFRAME_INDEX_COLUMN)
        result.rename(columns={old_column: new_column for old_column, new_column in zip(columns, new_columns)}, inplace=True)
        result.index = pd.to_datetime(result.index, format="%Y")

        return result[period.start : period.end] if period is not None else result
    
    def get_availible_period(self, region: str) -> TimePeriod | None:
        data = self.get_data(region, period=None)
        if data is None or data.shape[0] == 0:
            return None
        
        start, end = data.index.min().date(), data.index.max().date()
        return TimePeriod(start, end)