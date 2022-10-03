from pydantic import BaseModel
from typing import Any, Optional
import rasterio as rio
from rasterio.transform import Affine
from rasterio.crs import CRS
import numpy as np


class Tile(BaseModel):
    filename: str = ""
    left: float = 0.0
    right: float = 0.0
    bottom: float = 0.0
    top: float = 0.0
    ncols: int = 0
    nrows: int = 0
    resolution: float = 0.0
    nodata: float = 0.0

    data: Any = None
    profile: Any = None

    @classmethod
    def from_filename(self, filename: str) -> "Tile":
        t = Tile()
        t.filename = filename
        t._read()
        return t

    def _read(self):
        if self.data is None:
            r = rio.open(self.filename)
            self.data = r.read(1, masked=True).data
            self.profile = r.profile
            self.nodata = r.profile.data["nodata"]
            self._apply_filer()  # make my own np.nan instead of the rasterio based one

    def write(self, filename):
        if self.profile is None:
            self.profile = {
                "driver": "GTiff",
                "dtype": "float32",
                "nodata": -3.4028234663852886e38,
                "width": self.ncols,
                "height": self.nrows,
                # "resolution": self.resolution,
                "count": 1,
                "crs": CRS.from_epsg(28992),
                "transform": Affine(0.5, 0.0, self.left, 0.0, -0.5, self.top),
                "tiled": False,
                "interleave": "band",
            }

        with rio.open(filename, "w", **self.profile) as dst:
            dst.write(self.data.astype(rio.float32), 1)

    def _apply_filer(self):
        mask = self.data > 1e4
        mask |= self.data < -1e4
        self.data[mask] = np.nan

    def subtract(self, t: "Tile"):
        self.data -= t.data

    def add(self, t: "Tile"):
        self.data += t.data

    def divide(self, f):
        assert f != 0.0
        self.data[self.data == self.nodata] = np.nan
        self.data /= f

    def multiply(self, f):
        self.data[self.data == self.nodata] = np.nan
        self.data *= f

    def limits(self, lower_limit, upper_limit):
        self.upper_limit(upper_limit)
        self.lower_limit(lower_limit)

    def upper_limit(self, f):
        self.data[self.data > f] = f

    def lower_limit(self, f):
        self.data[self.data < f] = f

    def z_at(self, x: float, y: float) -> Optional[float]:
        self._read()
        dx = x - self.left
        dy = self.top - y

        idx = int(dx / self.resolution)
        if idx < 0 or idx >= self.ncols:
            return None

        idy = int(dy / self.resolution)
        if idy < 0 or idy >= self.nrows:
            return None

        z = self.data[idy, idx]
        if z == self.nodata:
            return None
        return float(z)
