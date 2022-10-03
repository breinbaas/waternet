from tqdm import tqdm

from shared.levees import LeveeSections
from shared.ahncutter import AHNCutter
from shared.ahn import AHNVersion
from shared.settings import AHN3_YEAR, AHN4_YEAR

ZICHTJAAR = 2024

for ls in tqdm(LeveeSections().items):
    left, top, right, bottom = ls.bounding_box(offset=100)
    ahnc = AHNCutter()
    ahn4 = ahnc.execute(left, top, right, bottom, AHNVersion.AHN4)
    ahn3 = ahnc.execute(left, top, right, bottom, AHNVersion.AHN3)

    agz = (ahn3.data - ahn4.data) / (AHN4_YEAR - AHN3_YEAR)
    pred = ahn4.data - agz * (ZICHTJAAR - AHN4_YEAR)

    temp = ahn3
    temp.data = pred

    temp.write("test.tiff")
    break
    # ahn4 = ahnc.execute()
