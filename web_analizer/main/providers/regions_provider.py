from collections import defaultdict
import world_bank_data as wb

from main.settings import AppSettings
from main.models import DemographyEntry
from main.core_models import RegionBase, Region
from main.utils import get_local_region_codes

class RegionsProvider:
    _WB_CODE_COLUMN: str = "iso2Code"
    _WB_NAME_COLUMN: str = "name"

    def get_regions(self) -> list[Region]:
        local_regions = get_local_region_codes()
        if AppSettings.WORLDBANK_SOURCE is not None:
            worldbank_regions_df = wb.get_countries()[[RegionsProvider._WB_CODE_COLUMN, RegionsProvider._WB_NAME_COLUMN]]
            worldbank_regions = {
                country[RegionsProvider._WB_CODE_COLUMN].lower(): country[RegionsProvider._WB_NAME_COLUMN] for _, country in worldbank_regions_df.iterrows()
            }
        else:
            worldbank_regions = {}
        db_regions = DemographyEntry.objects.values("region", "source").distinct().order_by()

        sources_by_region: defaultdict[str, set[str]] = defaultdict(set)
        for region, source in db_regions:
            sources_by_region[region.lower()].add(source)
        for local_region in local_regions:
            sources_by_region[local_region.lower()].add(AppSettings.LOCAL_SOURCE)
        for worldbank_region in worldbank_regions.keys():
            sources_by_region[worldbank_region].add(AppSettings.WORLDBANK_SOURCE)

        return [Region.from_base(self._get_region_base(region_code, worldbank_regions), sources) for region_code, sources in sources_by_region.items()]
    
    def _get_region_base(self, region_code: str, region_name_by_code_map: dict[str, str]) -> RegionBase:
        invariant_region_code = region_code.lower()
        if invariant_region_code in AppSettings.REGIONS_DICT:
            return AppSettings.REGIONS_DICT[invariant_region_code]
        if invariant_region_code in region_name_by_code_map:
            return region_name_by_code_map[invariant_region_code]
        return RegionBase(region_code, region_code)