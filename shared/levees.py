from math import atan2, cos, floor, hypot, radians, sin
from typing import List, Tuple, Union
import shapefile
from pydantic import BaseModel
import numpy as np

from .settings import LEVEESECTIONS_SHAPE, LEVEES_SHAPE


class LeveeBase(BaseModel):
    dtcode: str = ""
    points: List[Tuple[float, float, float]] = []  # list of [chainage, x, y]
    rpoints: List[
        Tuple[float, float, float, float]
    ] = []  # list of [chainage, x, y, angle] but with a fixed distance of 1m

    def generate_rpoints(self):
        self.rpoints = self.regulary_spaced_referenceline(interval=1.0)

    def regulary_spaced_referenceline(
        self, interval: float = 5.0
    ) -> list[Tuple[float, float, float, float]]:
        result = []
        cmin = self.points[0][0]
        cmax = self.points[-1][0]
        cs = np.arange(cmin, cmax, interval)

        for l in cs:
            result.append(self.cxya_at_c(l))
        return result

    def perpendicular_points(self, c: float, left: float, right: float, interval=0.5):
        p = self.cxya_at_c(c)
        if p[0] < 0.0:
            raise ValueError(
                f"Invalid chainage, min=0, max={self.points[-1][0]}, but you used {c}"
            )

        angle_left = p[3] - radians(90)
        angle_right = p[3] + radians(90)
        xl = p[1] + left * cos(angle_left)
        yl = p[2] + left * sin(angle_left)
        xr = p[1] + right * cos(angle_right)
        yr = p[2] + right * sin(angle_right)

        result = [(round(xl, 2), round(yl, 2))]
        num_points = int((left + right) / interval) + 1
        for i in range(1, num_points - 1):
            x = xl + interval * i / (left + right) * (xr - xl)
            y = yl + interval * i / (left + right) * (xr - xl)
            result.append((round(x, 2), round(y, 2)))

        result.append((round(xr, 2), round(yr, 2)))

        return result

    def perpendicular_line(self, c: float, left: float, right: float):
        p = self.cxya_at_c(c)
        if p[0] < 0.0:
            raise ValueError(
                f"Invalid chainage, min=0, max={self.points[-1][0]}, but you used {c}"
            )

        angle_left = p[3] - radians(90)
        angle_right = p[3] + radians(90)
        xl = p[1] + left * cos(angle_left)
        yl = p[2] + left * sin(angle_left)
        xr = p[1] + right * cos(angle_right)
        yr = p[2] + right * sin(angle_right)

        return round(xl, 2), round(yl, 2), round(xr, 2), round(yr, 2)

    def cxya_at_c(self, c: float) -> Tuple[float, float, float, float]:
        """Get point information on the given chainage

        Args:
            c (float): Chainage on the levee

        Returns:
            Union[float, float, float, float]: chainage, x, y, angle
        """
        for i in range(1, len(self.points)):
            c1, x1, y1 = self.points[i - 1]
            c2, x2, y2 = self.points[i]

            if c1 <= c <= c2:
                x = x1 + (c - c1) / (c2 - c1) * (x2 - x1)
                y = y1 + (c - c1) / (c2 - c1) * (y2 - y1)
                alpha = atan2((y1 - y2), (x1 - x2))
                return round(c, 2), round(x, 2), round(y, 2), alpha

        return -1, 0.0, 0.0, 0.0

    def bounding_box(self, offset: float = 0) -> Tuple[int, int, int, int]:
        """Return the bounding box of the levee

        Args:
            offset: int, an optional offset to take into account

        Returns:
            Union[int, int, int, int]: left x, top y, right x, bottom y of the bounding box
        """
        if offset < 0:
            offset = 0
        xs = [p[1] for p in self.points]
        ys = [p[2] for p in self.points]
        return (
            floor(min(xs) - offset),
            floor(max(ys) + offset) + 1,
            floor(max(xs) + offset) + 1,
            floor(min(ys) - offset),
        )

    def closest_referenceline_point_to(
        self, x: float, y: float
    ) -> Tuple[float, float, float]:
        """Get the closest point of the referenceline to the given point

        Args:
            x (float): x coordinate of the point to look for
            y (float): y coordinate of the point to look for

        Returns:
            Tuple[float, float, float]: Tuple with the x,y of the closest point and the distance from the point to the point on the referenceline
        """
        if len(self.rpoints) == 0:
            self.generate_rpoints()

        result = -1.0
        for p in self.rpoints:
            dl = hypot(p[1] - x, p[2] - y)
            if result == -1 or dl < result:
                result = dl

        return result


class Levee(LeveeBase):
    ...


class LeveeSection(LeveeBase):
    mhw: float = 0.0
    dth: float = 0.0
    ipo: str = ""


class Levees:
    """Uses the source data that uses one code (like A117) for one referenceline"""

    def __init__(self):
        self.items = []
        self._load()

    def _load(self):
        try:
            sf = shapefile.Reader(LEVEES_SHAPE)
        except Exception as e:
            raise ValueError(f"Could not read file '{LEVEES_SHAPE}', got error '{e}'")

        for sr in sf.shapeRecords():
            points, dl = [], 0.0
            for i, p in enumerate(sr.shape.points):
                if i > 0:
                    dl += hypot(points[i - 1][1] - p[0], points[i - 1][2] - p[1])
                points.append((round(dl, 2), round(p[0], 2), round(p[1], 2)))

            levee = Levee(
                dtcode=sr.record["DWKIDENT"],
                points=points,
            )
            self.items.append(levee)

    def get_from_code(self, code: str) -> List[Levee]:
        for dt in self.items:
            if dt.dtcode == code:
                return dt
        return None


class LeveeSections:
    """Uses the source data that has divided a levee into sections like A117_001, A117_002 etc"""

    def __init__(self):
        self.items = []
        self._load()

    def _load(self):
        try:
            sf = shapefile.Reader(LEVEESECTIONS_SHAPE)
        except Exception as e:
            raise ValueError(
                f"Could not read file '{LEVEESECTIONS_SHAPE}', got error '{e}'"
            )

        for sr in sf.shapeRecords():
            points, dl = [], 0.0
            for i, p in enumerate(sr.shape.points):
                if i > 0:
                    dl += hypot(points[i - 1][1] - p[0], points[i - 1][2] - p[1])
                points.append((round(dl, 2), round(p[0], 2), round(p[1], 2)))

            self.items.append(
                LeveeSection(
                    dtcode=sr.record["dtcode"],
                    dth=sr.record["dth"],
                    ipo=sr.record["ipo"],
                    mhw=sr.record["mhw"],
                    points=points,
                )
            )

    def get_from_code(self, code: str) -> List[Levee]:
        return [d for d in self.items if d.dtcode.find(code) > -1]


def get_waternet_levees():
    return LeveeSections()
