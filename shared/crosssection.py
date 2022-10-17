from pydantic import BaseModel
from typing import List, Optional
import matplotlib.pyplot as plt
from pathlib import Path
from rdp import rdp
import numpy as np

from shared.ahn import AHNVersion


class CrosssectionPoint(BaseModel):
    c: float
    x: float
    y: float
    z: Optional[float]

    def to_string(self) -> str:
        return f"{self.c},{self.x},{self.y},{round(self.z,2)}"


class Crosssection(BaseModel):
    dtcode: str
    ahn_version: AHNVersion
    chainage: int
    points: List[CrosssectionPoint] = []

    def plot(self, filename: str):
        pass

    def clean(self):
        if len(self.points) < 2:
            self.points = []
            return

        # get the current limits
        left = self.points[0].c
        right = self.points[-1].c

        # remove all none points
        new_points = [p for p in self.points if not np.isnan(p.z)]

        # apply rdp
        rdp_points = rdp([(p.c, p.z) for p in new_points], epsilon=0.05)
        cs = [p[0] for p in rdp_points]

        new_points = [p for p in new_points if p.c in cs]

        if len(new_points) <= 1:
            self.points = []
            return

        # check if we have the left limit, if not, add it again and use the z of the next point
        if new_points[0].c != left:
            new_points.insert(0, self.points[0])

        if np.isnan(new_points[0].z):
            new_points[0].z = new_points[1].z

        # check if we have the right limit, if not, add it again and use the z of the previous point
        if new_points[-1].c != right:
            new_points.append(self.points[-1])

        if np.isnan(new_points[-1].z):
            new_points[-1].z = new_points[-2].z

        if np.isnan(new_points[0].z):
            self.points = []
        else:
            # add zero (reference line point if not available)
            p0 = [p for p in new_points if p.c == 0.0]
            if len(p0) == 0:
                below0 = [p for p in new_points if p.c < 0]
                above0 = [p for p in new_points if p.c > 0]
                c1 = below0[-1].c
                c2 = above0[0].c
                x1 = below0[-1].x
                x2 = above0[0].x
                y1 = below0[-1].y
                y2 = above0[0].y
                z1 = below0[-1].z
                z2 = above0[0].z
                c = 0.0
                x = x1 + ((c - c1) / (c2 - c1) * (x2 - x1))
                y = y1 + ((c - c1) / (c2 - c1) * (y2 - y1))
                z = z1 + ((c - c1) / (c2 - c1) * (z2 - z1))
                new_points.append(CrosssectionPoint(c=0, x=x, y=y, z=z))

            new_points = sorted(new_points, key=lambda x: x.c)
            self.points = new_points

    def to_one_line(self) -> str:
        """Generate a one line string with the crosssection information

        Returns:
            str: String with the crosssection information
        """
        points = ",".join([p.to_string() for p in self.points])
        return f"{self.dtcode},{self.chainage},{points}"

    def to_csv(self, output_dir):
        if len(self.points) == 0:
            return
        prefixes = {
            AHNVersion.AHN2: "ahn2",
            AHNVersion.AHN3: "ahn3",
            AHNVersion.AHN4: "ahn4",
        }
        self.clean()

        path3d = Path(output_dir) / f"{self.dtcode}" / "3d"
        path3d.mkdir(parents=True, exist_ok=True)
        f = open(
            path3d / f"{prefixes[self.ahn_version]}_{self.chainage:05d}.csv",
            "w",
        )
        f.write("l,x,y,z\n")
        f.write("[m],[m RD],[m RD],[m tov NAP]\n")
        for p in self.points:
            f.write(f"{p.c},{p.x:.2f},{p.y:.2f},{p.z:.2f}\n")
        f.close()

        path2d = Path(output_dir) / f"{self.dtcode}" / "2d"
        path2d.mkdir(parents=True, exist_ok=True)
        f = open(
            path2d / f"{prefixes[self.ahn_version]}_{self.chainage:05d}.csv",
            "w",
        )
        for p in self.points:
            f.write(f"{p.c},{p.z:.2f}\n")
        f.close()
