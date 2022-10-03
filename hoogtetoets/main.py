from tqdm import tqdm

from shared.levees import LeveeSections
from shared.ahncutter import AHNCutter
from shared.ahn import AHNVersion
from shared.settings import AHN3_YEAR, AHN4_YEAR

ZICHTJAAR = 2024

# per dijktraject deel
for ls in tqdm(LeveeSections().items):
    left, top, right, bottom = ls.bounding_box(offset=100)
    # haal de ahn4, 3 en 2 data op
    ahnc = AHNCutter()
    ahn4 = ahnc.execute(left, top, right, bottom, AHNVersion.AHN4)
    ahn3 = ahnc.execute(left, top, right, bottom, AHNVersion.AHN3)
    # ahn3 = ahnc.execute(left, top, right, bottom, AHNVersion.AHN2)

    # bereken de agz43, 42 en 32
    agz43 = ahn4.subtract(ahn3)

    i = 1

# als agz43 None is dan agz42 gebruiken, als agz42 None is dan agz32 gebruiken
# limieten toepassen
# nagaan over 1.5m breedte
# nagaan over de opgegeven breedte

# for ls in tqdm(LeveeSections().items):


#     agz = (ahn3.data - ahn4.data) / (AHN4_YEAR - AHN3_YEAR)
#     pred = ahn4.data - agz * (ZICHTJAAR - AHN4_YEAR)

#     temp = ahn3
#     temp.data = pred

#     temp.write("test.tiff")
#     break
#     # ahn4 = ahnc.execute()
