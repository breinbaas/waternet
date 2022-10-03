from tqdm import tqdm
import numpy as np
from pathlib import Path

from shared.levees import LeveeSections
from shared.ahncutter import AHNCutter
from shared.ahn import AHNVersion
from shared.settings import (
    AHN3_YEAR,
    AHN4_YEAR,
    AHN2_YEAR,
    HEIGHT_ASSESSMENT_OUTPUT_DIR,
)

from copy import deepcopy

ZICHTJAAR = 2024

# per dijktraject deel
for ls in tqdm(LeveeSections().items):
    left, top, right, bottom = ls.bounding_box(offset=100)
    # haal de ahn4, 3 en 2 data op
    ahnc = AHNCutter()
    ahn4 = ahnc.execute(left, top, right, bottom, AHNVersion.AHN4)
    ahn3 = ahnc.execute(left, top, right, bottom, AHNVersion.AHN3)
    ahn2 = ahnc.execute(left, top, right, bottom, AHNVersion.AHN2)

    # bereken de agz43
    m = deepcopy(ahn4)
    m.subtract(ahn3)
    m.divide(AHN4_YEAR - AHN3_YEAR)  # agz43
    m.limits(-0.02, 0.0)
    agz43 = deepcopy(m)

    # bereken agz42
    m = deepcopy(ahn4)
    m.subtract(ahn2)
    m.divide(AHN4_YEAR - AHN2_YEAR)  # agz43
    m.limits(-0.02, 0.0)
    agz42 = deepcopy(m)

    # bereken agz32
    m = deepcopy(ahn3)
    m.subtract(ahn2)
    m.divide(AHN3_YEAR - AHN2_YEAR)  # agz43
    m.limits(-0.02, 0.0)
    agz32 = deepcopy(m)

    # create the final matrix.. red or blue pill?
    # AHN4 tot 2 is de basis
    agz = deepcopy(agz42)
    # als daar nan in staat dan gaan we naar 43
    mask = np.isnan(agz.data)
    agz.data[mask] = agz43.data[mask]
    # als daar nog nan in staan dan gaan we naar 32
    mask = np.isnan(agz.data)
    agz.data[mask] = agz32.data[mask]

    # op dit moment hebben we de zetting per jaar
    # omrekenen naar totale zetting in zichtjaar
    agz.multiply(ZICHTJAAR - AHN4_YEAR)
    # en bepaal de huidige hoogte
    m = deepcopy(ahn4)
    m.add(agz)
    # dit is het rasterbestand met de hoogte voor het zichtjaar
    m.write(Path(HEIGHT_ASSESSMENT_OUTPUT_DIR) / f"{ls.dtcode}.tif")
    # nagaan over 1.5m breedte

    # nagaan over de opgegeven breedte

    break
