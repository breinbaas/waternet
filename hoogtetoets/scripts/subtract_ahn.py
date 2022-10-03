"""
This script subtracts the AHN3 data from the AHN4 data. 

It uses the original TIF files and generates new TIF files where the 
raster values is the difference of the AHN4 and AHN3 values (ahn4 - ahn3)
which can be seen as settlement over the time between AHN4 and AHN3
"""

from shared.helpers import case_insensitive_glob
from shared.settings import (
    AHN2_DATA,
    AHN3_DATA,
    AHN4_DATA,
    AGZ43_DATA,
    AGZ42_DATA,
    AGZ32_DATA,
    AHN2_YEAR,
    AHN3_YEAR,
    AHN4_YEAR,
)
import rasterio as rio
from pathlib import Path
from tqdm import tqdm

ahn2 = case_insensitive_glob(AHN2_DATA, ".tif")
ahn3 = case_insensitive_glob(AHN3_DATA, ".tif")
ahn4 = case_insensitive_glob(AHN4_DATA, ".tif")

# AHN4 - AHN3
for fn4 in tqdm(ahn4):
    fn3 = str(fn4).replace("AHN4", "AHN3").replace("ahn4", "ahn3")

    if Path(fn3).exists():
        r4 = rio.open(fn4)
        r3 = rio.open(fn3)
        data3 = r3.read(1, masked=True).data
        data4 = r4.read(1, masked=True).data
        dsm_meta = r4.profile
        ddata = (data4 - data3) / (AHN4_YEAR - AHN3_YEAR)
        # the subtraction makes the nodata invalid so we make our own
        ddata[ddata > 1e9] = 1e9
        ddata[ddata < -1e9] = 1e9
        # set this value as nodata
        dsm_meta["nodata"] = 1e9
        # save the raster file
        with rio.open(
            Path(AGZ43_DATA) / f"{fn4.stem.replace('AHN4_', 'AGZ43_')}.tif",
            "w",
            **dsm_meta,
        ) as ff:
            ff.write(ddata, 1)


# AHN4 - AHN2 TODO
for fn4 in tqdm(ahn4):
    code = Path(fn4).stem.split("_")[-1]
    fn2 = str(fn4).replace("AHN4", "AHN2").replace("ahn4", "ahn2")
    fn2 = fn2.replace(Path(fn2).name, f"AHN2_n{code.lower()}.tif")
    if Path(fn2).exists() and Path(fn4).exists():
        r4 = rio.open(fn4)
        r2 = rio.open(fn2)
        data2 = r2.read(1, masked=True).data
        data4 = r4.read(1, masked=True).data
        dsm_meta = r4.profile
        ddata = (data4 - data2) / (AHN4_YEAR - AHN2_YEAR)
        # the subtraction makes the nodata invalid so we make our own
        ddata[ddata > 1e9] = 1e9
        ddata[ddata < -1e9] = 1e9
        # set this value as nodata
        dsm_meta["nodata"] = 1e9
        # save the raster file
        with rio.open(
            Path(AGZ42_DATA) / f"{fn4.stem.replace('AHN4_', 'AGZ42_')}.tif",
            "w",
            **dsm_meta,
        ) as ff:
            ff.write(ddata, 1)
    else:
        print(f"Could not subtract {fn2} from {fn4}, probably missing files...")


# AHN3 - AHN2
for fn3 in tqdm(ahn3):
    code = Path(fn3).stem.split("_")[-1]
    fn2 = Path(AHN2_DATA) / f"AHN2_n{code.lower()}.tif"

    if Path(fn2).exists() and Path(fn3).exists():
        r3 = rio.open(fn3)
        r2 = rio.open(fn2)
        data2 = r2.read(1, masked=True).data
        data3 = r3.read(1, masked=True).data
        dsm_meta = r3.profile
        ddata = (data3 - data2) / (AHN3_YEAR - AHN2_YEAR)
        # the subtraction makes the nodata invalid so we make our own
        ddata[ddata > 1e9] = 1e9
        ddata[ddata < -1e9] = 1e9
        # set this value as nodata
        dsm_meta["nodata"] = 1e9
        # save the raster file
        with rio.open(
            Path(AGZ32_DATA) / f"AGZ32_{code.lower()}.tif",
            "w",
            **dsm_meta,
        ) as ff:
            ff.write(ddata, 1)
    else:
        print(f"Could not subtract {fn2} from {fn3}, probably missing files...")
