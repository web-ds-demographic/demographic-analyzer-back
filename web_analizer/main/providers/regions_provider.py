from collections import defaultdict
import world_bank_data as wb

from main.settings import AppSettings
from main.models import DemographyEntry
from main.core_models import RegionBase, Region
from main.utils import get_local_region_codes

class RegionsProvider:
    _WB_CODE_COLUMN: str = "iso2Code"

    def get_regions(self) -> list[Region]:
        local_regions = get_local_region_codes()
        worldbank_regions = set(wb.get_countries()[self._WB_CODE_COLUMN]) if AppSettings.WORLDBANK_SOURCE is not None else []
        db_regions = DemographyEntry.objects.values("region", "source").distinct().order_by()

        sources_by_region: defaultdict[str, set[str]] = defaultdict(set)
        for region, source in db_regions:
            sources_by_region[region.lower()].add(source)
        for local_region in local_regions:
            sources_by_region[local_region.lower()].add(AppSettings.LOCAL_SOURCE)
        for worldbank_region in worldbank_regions:
            sources_by_region[worldbank_region.lower()].add(AppSettings.WORLDBANK_SOURCE)

        return [Region.from_base(RegionsProvider._get_region_base(region_code), sources) for region_code, sources in sources_by_region.items()]
    
    @staticmethod
    def _get_region_base(region_code: str) -> RegionBase:
        invariant_region_code = region_code.lower()
        known_regions = AppSettings.REGIONS_DICT
        return known_regions[invariant_region_code] if invariant_region_code in known_regions else RegionBase(region_code, region_code)