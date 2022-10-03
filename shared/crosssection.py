from pydantic import BaseModel
from typing import List, Optional
import matplotlib.pyplot as plt
from pathlib import Path
from rdp import rdp

from shared.ahn import AHNVersion


class CrosssectionPoint(BaseModel):
    c: float
    x: float
    y: float
    z: Optional[float]


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
        new_points = [p for p in self.points if p.z is not None]

        # apply rdp
        rdp_points = rdp([(p.c, p.z) for p in new_points], epsilon=0.1)
        cs = [p[0] for p in rdp_points]

        new_points = [p for p in new_points if p.c in cs]

        if len(new_points) <= 1:
            self.points = []
            return

        # check if we have the left limit, if not, add it again and use the z of the next point
        if new_points[0].c != left:
            new_points.insert(0, self.points[0])

        if new_points[0].z is None:
            new_points[0].z = self.points[1].z

        # check if we have the right limit, if not, add it again and use the z of the previous point
        if new_points[-1].c != right:
            new_points.append(self.points[-1])

        if new_points[-1].z is None:
            new_points[-1].z = new_points[-2].z

        self.points = new_points

    def to_csv(self, output_dir):
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
