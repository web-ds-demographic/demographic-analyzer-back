import pandas as pd

import main.constants as const
import main.providers.demography_providers as demography_providers
from ds.alg import get_pred
from main.settings import AppSettings
from main.models import DemographyEntry
from main.core_models import TimePeriod, Region
from main.providers.regions_provider import RegionsProvider
from main.utils import series_to_entity, get_dates_from_timestamps

class DemographyManager:
    _providers: dict[str, demography_providers.BaseProvider]
    _db_cache_providers: dict[str, demography_providers.DatabaseProvider]
    _regions_provider: RegionsProvider

    def __init__(self):
        self._regions_provider = RegionsProvider()

        self._providers = {}
        self._db_cache_providers = {}

        local_source = AppSettings.LOCAL_SOURCE
        if local_source is not None:
            self._providers[local_source.lower()] = demography_providers.CSVFilesProvider(local_source)
            self._db_cache_providers[local_source.lower()] = demography_providers.DatabaseProvider(local_source)

        worldbank_source = AppSettings.WORLDBANK_SOURCE
        if worldbank_source is not None:
            self._providers[worldbank_source.lower()] = demography_providers.WorldBankProvider(worldbank_source)
            self._db_cache_providers[worldbank_source.lower()] = demography_providers.DatabaseProvider(worldbank_source)

        for db_source in AppSettings.DATABASE_SOURCES:
            if db_source not in self._db_cache_providers:
                self._db_cache_providers[db_source.lower()] = demography_providers.DatabaseProvider(db_source)

    def clear_cache(self, region: str | None, source: str | None, period: TimePeriod | None):
        filters = {}
        if region is not None:
            filters["region"] = region
        if source is not None:
            filters["source"] = source
        if period is not None:
            filters["year__range"] = (period.start, period.end)
        manager = DemographyEntry.objects
        if len(filters) != 0:
            objects = manager.filter(**filters)
        else:
            objects = manager.all()
        objects.delete()

    def get_regions(self) -> list[Region]:
        return self._regions_provider.get_regions()
    
    def get_availible_period(self, region: str, source: str) -> TimePeriod | None:
        cache_provider = self._db_cache_providers.get(source.lower())
        provider = self._providers.get(source.lower())

        cached_period = cache_provider.get_availible_period(region) if cache_provider is not None else None
        period = provider.get_availible_period(region) if provider is not None else None

        if period is None:
            return cached_period
        return period.merge_with(cached_period)
    
    def predict(self, region: str, source: str, input_period: TimePeriod, predict_years_count: int) -> pd.DataFrame | None:
        data = self._get_data(region, source, input_period)
        if data is None:
            return None
        data = data.reset_index()
        data[const.DATAFRAME_INDEX_COLUMN] = data[const.DATAFRAME_INDEX_COLUMN].dt.year
        return get_pred(data.reset_index(), predict_years_count)

    def _get_data(self, region: str, source: str, period: TimePeriod | None) -> pd.DataFrame | None:
        if source.lower() not in self._db_cache_providers:
            return self._get_and_cache_data(region, source, period)

        cache_provider = self._db_cache_providers[source.lower()]
        cached_data = cache_provider.get_data(region, period)
        
        if period is None:
            period = cache_provider.get_availible_period(region)
            if period is None:
                return cached_data
        
        non_cached_periods = period.split_by(get_dates_from_timestamps(cached_data.index))
        non_cached_data = []
        for non_cached_period in non_cached_periods:
            data = self._get_and_cache_data(region, source, non_cached_period)
            if data is not None and not data.empty:
                non_cached_data.append(data)

        if cached_data is None or cached_data.empty:
            if len(non_cached_data) == 0:
                return None
            to_concat = non_cached_data
        else:
            to_concat = [cached_data, *non_cached_data]
        result = pd.concat(to_concat, join="outer")

        return result[~result.index.duplicated()].sort_index()

    def _get_and_cache_data(self, region: str, source: str, period: str | None) -> pd.DataFrame | None:
        if source.lower() not in self._providers:
            return None
        
        result = self._providers[source.lower()].get_data(region, period)
        if result is None:
            return None

        entities = [series_to_entity(index, series, region, source) for index, series in result.iterrows()]
        DemographyEntry.objects.bulk_create(entities, ignore_conflicts=True)
        return result
