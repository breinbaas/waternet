from enum import IntEnum
from math import atan2, cos, hypot, pi, sin
from pathlib import Path
from turtle import right
import rasterio as rio
from tqdm import tqdm
from typing import List, Optional, Union
import numpy as np
from shapely.geometry import LineString


from .settings import (
    AHN2_DATA,
    AHN3_DATA,
    AHN4_DATA,    
)
from .helpers import case_insensitive_glob, polyline_to_regularly_spaced_polyline
from .tile import Tile


class AHNVersion(IntEnum):
    AHN2 = 2
    AHN3 = 3
    AHN4 = 4

class AHN:
    def __init__(self, version: AHNVersion = AHNVersion.AHN4):
        self.version: str = version
        self.inifile: str = ""
        self.tiles: List[Tile] = []

        if self.version == AHNVersion.AHN2:
            self.path = AHN2_DATA
        elif self.version == AHNVersion.AHN3:
            self.path = AHN3_DATA
        elif self.version == AHNVersion.AHN4:
            self.path = AHN4_DATA        
        else:
            raise ValueError(f"Invalid AHNVersion {version}")

        self._setup()

    def _setup(self):
        # check for the ini file, if not available add it else read it
        self.inifile = Path(self.path) / "data.ini"

        # generate it if it is not available
        if not self.inifile.exists():
            self._generate_ini()

        # read it and store the metadata
        self._read_ini()

    def _read_ini(self):
        lines = open(self.inifile, "r").readlines()
        for line in lines[1:]:
            args = line.split(",")
            self.tiles.append(
                Tile(
                    filename=args[0],
                    left=float(args[1]),
                    right=float(args[2]),
                    bottom=float(args[3]),
                    top=float(args[4]),
                    resolution=float(args[5]),
                    ncols=int(args[7]),
                    nrows=int(args[8]),
                    nodata=float(args[9]),
                )
            )

    def _generate_ini(self):
        fout = open(self.inifile, "w")
        fout.write("filename,left,right,bottom,top,res_x,res_y,width,height,nodata\n")
        files = case_insensitive_glob(self.path, ".tif")
        for fn in tqdm(files):
            r = rio.open(fn)
            fout.write(
                f"{fn},{r.bounds.left},{r.bounds.right},{r.bounds.bottom},{r.bounds.top},{r.res[1]},{r.res[0]},{r.meta['width']},{r.meta['height']},{r.meta['nodata']}\n"
            )

        fout.close()

    def get_tile_by_xy(self, x: float, y: float) -> Optional[Tile]:
        for tile in self.tiles:
            if (
                x >= tile.left
                and x <= tile.right
                and y >= tile.bottom
                and y <= tile.top
            ):
                return tile
        return None

    def z_at(self, x: float, y: float) -> Optional[float]:
        """Get the z value at the given coordinate

        Args:
            x (float): x coordinate RD space
            y (float): y coordinate RD space

        Returns:
            Optional[float]: The z value or None if there is no value
        """
        for tile in self.tiles:
            if x >= tile.left and x < tile.right and y > tile.bottom and y <= tile.top:
                z = tile.z_at(x, y)
                if z is not None:
                    return float(z)
        return None

    def zs_from_polyline(
        self,
        polyline: List[Union[float, float]],
        offset: float = 0,
        interval: float = 0.5,
        num_digits: int = 4,
    ) -> List[Union[float, float, float, float]]:
        """Generate a list of l,x,y,z points from a given (poly)line

        Args:
            polyline (List[Union[float, float]]): The points on the (poly)line
            offset (float): The offset to use (+ = up)
            interval (float, optional): The interval distance between the point. Defaults to 0.5.
            num_digits (int, optional): The number of digits to round the z value to. Defaults to 4.

        Returns:
            List[Union[float, float, float, float]]: Returns a list of (l, x, y, z)
        """
        #
        if offset != 0:
            ls = LineString(polyline)
            if offset > 0:
                ls = ls.parallel_offset(offset, join_style=2)
                polyline = [p for p in reversed(ls.coords)]
            else:
                ls = ls.parallel_offset(offset, join_style=2, side="left")
                polyline = [p for p in ls.coords]

            if len(polyline) == 0:
                raise ValueError("The offset you gave returns an invalid polygon")

        # add first point
        polyline = polyline_to_regularly_spaced_polyline(polyline, interval)

        result = []
        ltot = 0
        for pt in polyline:
            z = self.z_at(pt[1], pt[2])
            if z is not None:
                z = round(z, num_digits)
            result.append((ltot, pt[1], pt[2], z))
            ltot += interval

        return result
