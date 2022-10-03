from pathlib import Path
from tqdm import tqdm

from shared.levees import Levees
from shared.helpers import polyline_to_regularly_spaced_polyline
from shared.ahn import AHN, AHNVersion
import matplotlib.pyplot as plt
import shapefile

from shared.crosssection import Crosssection, CrosssectionPoint
from shared.settings import CROSSSECTION_OUTPUT_DIR

plt.rcParams["figure.figsize"] = (15, 5)


DTCODE = "V344"  # dit is de dijktraject code
HOH = 100  # dit is de gewenste hart op hart afstand
LEFT = 20  # het aantal meters dat het dwarsprofiel richting de boezem moet lopen
RIGHT = 50  # het aantal meters dat het dwarsprofiel richting de polder moet lopen


if __name__ == "__main__":
    levee = Levees().get_from_code(DTCODE)

    ahn2 = AHN(version=AHNVersion.AHN2)
    ahn3 = AHN(version=AHNVersion.AHN3)
    ahn4 = AHN(version=AHNVersion.AHN4)

    if levee is None:
        raise ValueError(
            f"Could not find dtcode '{DTCODE}', check the code or the shapefile."
        )

    pts = levee.regulary_spaced_referenceline(interval=10)

    shapepoints = []
    for p in tqdm(pts):
        xl, yl, xr, yr = levee.perpendicular_line(p[0], left=LEFT, right=RIGHT + 0.1)
        crspoints = polyline_to_regularly_spaced_polyline(
            [(xl, yl), (xr, yr)], interval=0.5
        )
        shapepoints.append((xl, yl, xr, yr, p[0]))
        plt.subplot(1, 1, 1)
        plt.title(f"{DTCODE}_{int(p[0]):05d} crosssection")
        crosssection = Crosssection(
            ahn_version=AHNVersion.AHN2, dtcode=DTCODE, chainage=p[0]
        )
        for crspoint in crspoints:
            crosssection.points.append(
                CrosssectionPoint(
                    c=crspoint[0] - LEFT,
                    x=crspoint[1],
                    y=crspoint[2],
                    z=ahn2.z_at(crspoint[1], crspoint[2]),
                )
            )
        crosssection.clean()
        crosssection.to_csv(CROSSSECTION_OUTPUT_DIR)
        plt.plot(
            [p.c for p in crosssection.points],
            [p.z for p in crosssection.points],
            label="AHN2",
        )

        crosssection = Crosssection(
            ahn_version=AHNVersion.AHN3, dtcode=DTCODE, chainage=p[0]
        )
        for crspoint in crspoints:
            crosssection.points.append(
                CrosssectionPoint(
                    c=crspoint[0] - LEFT,
                    x=crspoint[1],
                    y=crspoint[2],
                    z=ahn3.z_at(crspoint[1], crspoint[2]),
                )
            )
        crosssection.clean()
        crosssection.to_csv(CROSSSECTION_OUTPUT_DIR)
        plt.plot(
            [p.c for p in crosssection.points],
            [p.z for p in crosssection.points],
            label="AHN3",
        )

        crosssection = Crosssection(
            ahn_version=AHNVersion.AHN4, dtcode=DTCODE, chainage=p[0]
        )

        for crspoint in crspoints:
            crosssection.points.append(
                CrosssectionPoint(
                    c=crspoint[0] - LEFT,
                    x=crspoint[1],
                    y=crspoint[2],
                    z=ahn4.z_at(crspoint[1], crspoint[2]),
                )
            )
        crosssection.clean()
        crosssection.to_csv(CROSSSECTION_OUTPUT_DIR)
        plt.plot(
            [p.c for p in crosssection.points],
            [p.z for p in crosssection.points],
            label="AHN4",
        )

        plt.xlabel("lengte [m]")
        plt.ylabel("hoogte [m tov NAP]")
        plt.legend(loc="upper left")
        plt.grid()

        path = Path(CROSSSECTION_OUTPUT_DIR) / f"{DTCODE}" / "plots"
        path.mkdir(parents=True, exist_ok=True)
        plt.savefig(
            path / f"{int(p[0]):05d}.jpg",
        )
        plt.clf()

    w = shapefile.Writer(
        str(Path(CROSSSECTION_OUTPUT_DIR) / f"{DTCODE}" / f"{DTCODE}.shp")
    )
    w.field("metrering", "C", "40")

    for p in shapepoints:
        w.line([[[p[0], p[1]], [p[2], p[3]]]])
        w.record(f"{int(p[4]):05d}")
