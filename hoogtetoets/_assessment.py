from cProfile import label
from enum import IntEnum
import enum
from pydantic import BaseModel
from typing import List, Optional
from pathlib import Path
import matplotlib.pyplot as plt
from tqdm import tqdm
import pandas as pd
import numpy as np

from shared.levees import LeveeSections
from shared.ahn import AHN, AHNVersion
from shared.settings import AHN4_YEAR


from settings import *

plt.rcParams["figure.figsize"] = (15, 10)

OFFSET_WATER_STRICT = 0
OFFSET_POLDER_STRICT = 1.5
OFFSET_WATER_KERNZONE = 10
OFFSET_POLDER_KERNZONE = 20

ahn4 = AHN(AHNVersion.AHN4)
agz42 = AHN(AHNVersion.AGZ42)
agz43 = AHN(AHNVersion.AGZ43)
agz32 = AHN(AHNVersion.AGZ32)

PREDICTION_YEAR = 2024

# voor elk dijkdeel
for levee in tqdm(LeveeSections().items):
    # en elk punt om de m
    for c, x, y, a in levee.regulary_spaced_referenceline(1):
        # maak een dwarsprofiel voor beide methode
        # een dp wordt x, y
        dp_strict = levee.perpendicular_points(
            c, OFFSET_WATER_STRICT, OFFSET_POLDER_STRICT
        )
        dp_kernzone = levee.perpendicular_points(
            c, OFFSET_WATER_KERNZONE, OFFSET_POLDER_KERNZONE
        )

        # haal de ahn4 waardes op
        # een dp wordt nu x, y, z_ahn4
        dp_strict = [(p[0], p[1], ahn4.z_at(p[0], p[1])) for p in dp_strict]
        dp_kernzone = [(p[0], p[1], ahn4.z_at(p[0], p[1])) for p in dp_kernzone]

        # haal de agz waardes op
        # een dp wordt nu x, y, z_ahn4, agz42, agz43, agz32
        dp_strict = [
            (
                p[0],
                p[1],
                p[2],
                agz42.z_at(p[0], p[1]),
                agz43.z_at(p[0], p[1]),
                agz32.z_at(p[0], p[1]),
            )
            for p in dp_strict
        ]

        dp_kernzone = [
            (
                p[0],
                p[1],
                p[2],
                agz42.z_at(p[0], p[1]),
                agz43.z_at(p[0], p[1]),
                agz32.z_at(p[0], p[1]),
            )
            for p in dp_strict
        ]

        # STRIKTE METHODE
        # voor de strikte methode bepalen we de te hanteren agz o.b.v. het gemiddelde over de gegeven breedte
        agz42 = [p[3] for p in dp_kernzone if p[3] is not None]
        agz43 = [p[4] for p in dp_kernzone if p[3] is not None]
        agz32 = [p[5] for p in dp_kernzone if p[3] is not None]

        if len(agz42) > 0:
            agz42 = sum(agz42) / len(agz42)
        else:
            agz42 = None
        if len(agz43) > 0:
            agz43 = sum(agz43) / len(agz43)
        else:
            agz43 = None
        if len(agz32) > 0:
            agz32 = sum(agz32) / len(agz32)
        else:
            agz32 = None

        # kies de te gebruiken agz, volgorde is 42 dan 43 dan 32
        agz = agz42
        if agz is None:
            agz = agz43
        if agz is None:
            agz = agz32

        # als het None is zijn we klaar voor dit profiel
        if agz is None:
            continue
        else:
            # voer de limieten uit
            if agz > DEFAULT_SWELL_LIMIT:
                agz = DEFAULT_SWELL_LIMIT
            if agz < DEFAULT_BGS_LIMIT:
                agz = DEFAULT_BGS_LIMIT

            dp_strict = [
                (
                    p[0],
                    p[1],
                    p[2],
                    agz,
                )
                for p in dp_strict
            ]

            # bereken de hoogte van alle punten op het jaar dat opgegeven is
            dp_strict = [
                (p[0], p[1], p[2], p[3], p[2] - p[3] * (PREDICTION_YEAR - AHN4_YEAR))
                for p in dp_strict
            ]

            # bepaal of het voldoende is
            i = 1


# class HeightAssessmentMethod(IntEnum):
#     """
#     De methode van de hoogtetoets

#     STRICT kijkt van het referentiepunt 1.5m naar de polder of alle punten hoger liggen
#     dan de vereiste dijktafelhoogte. Resultaat = 1 (voldoet) of 0 (voldoet niet)

#     LEGGERPROFIEL kijkt over offset_water meters van de referentielijn tot offset_polder
#     meters richting de polder of in die zone een aaneengesloten stuk van 1.5m aanwezig
#     is dat boven de dijktafelhoogte ligt. Resultaat = 2 (geen inundatie gevaar) or 0 (voldoet niet)
#     """

#     STRICT = 0
#     LEGGERPROFIEL = 1


# class BackgroundSettlementPoint(BaseModel):
#     c: float = 0.0
#     x: float = 0.0
#     y: float = 0.0
#     ahn4: Optional[float] = 0.0
#     ahn3: Optional[float] = 0.0
#     ahn2: Optional[float] = 0.0
#     bgs42: Optional[float] = 0.0
#     bgs43: Optional[float] = 0.0
#     bgs32: Optional[float] = 0.0
#     bgs: float = 0.0


# class Assessment(BaseModel):
#     # input
#     levee: Levee = None
#     year_prediction: int = 0
#     dth: float = 0.0

#     # output
#     log_dir: str
#     plot_dir: str
#     background_settlement_points: List[BackgroundSettlementPoint] = []

#     def execute(self, method: HeightAssessmentMethod = HeightAssessmentMethod.STRICT):
#         # basis gegevens
#         ahn4 = AHN(AHNVersion.AHN4)
#         agz42 = AHN(AHNVersion.AGZ42)
#         agz43 = AHN(AHNVersion.AGZ43)
#         agz32 = AHN(AHNVersion.AGZ32)

#         # bepaal de methode en bijbehorende afstanden
#         offset_water = STRICT_OFFSET_WATER
#         offset_polder = STRICT_OFFSET_POLDER
#         if method == HeightAssessmentMethod.LEGGERPROFIEL:
#             offset_water = LEGGERPROFIEL_OFFSET_WATER
#             offset_polder = LEGGERPROFIEL_OFFSET_POLDER

#         # loop de referentielijn af op een vast interval (5m)
#         result = []
#         for p in self.levee.regulary_spaced_referenceline():
#             # haal alle xy punt informatie op
#             points = self.levee.perpendicular_points(p[0], offset_water, offset_polder)

#             # haal alle AHN4 waarden op
#             z_ahn4 = [ahn4.z_at(p[0], p[1]) for p in points]

#             # haal de AGZ42,43,32 waarden op per punt
#             dz42 = [agz42.z_at(p[0], p[1]) for p in points]
#             dz43 = [agz43.z_at(p[0], p[1]) for p in points]
#             dz32 = [agz32.z_at(p[0], p[1]) for p in points]

#             # bepaal de geldende AGZ waarde
#             agz = []
#             for i, dz in enumerate(dz42):
#                 if dz is None:
#                     dz = dz43[i]
#                 if dz is None:
#                     dz = dz32[i]

#                 if dz is None:
#                     agz.append(None)
#                 else:
#                     if dz > DEFAULT_SWELL_LIMIT:
#                         agz.append(DEFAULT_SWELL_LIMIT)
#                     elif dz < DEFAULT_BGS_LIMIT:
#                         agz.append(DEFAULT_BGS_LIMIT)
#                     else:
#                         agz.append(dz)


#             # voeg de punten aan een shapefile toe

#             # bepaal of het voldoet

#             # df = pd.DataFrame(
#             #     {
#             #         "x": [p[0] for p in points],
#             #         "y": [p[1] for p in points],
#             #         "z": z_ahn4,
#             #         "dz42": dz42,
#             #         "dz43": dz43,
#             #         "dz32": dz32,
#             #         "dz": agz,
#             #     }
#             # )

#             # # bepaal voorspelde hoogte
#             # df[f"z_{self.year_prediction}"] = df["z"] - df["dz"] * (
#             #     self.year_prediction - AHN4_YEAR
#             # )

#             # # bepaal of ze voldoen

#             # df.to_csv("test.csv")

#             # schrijf de resultaten in een shape bestand
#             break

#     def _calculate_bgs(
#         self,
#         bgs_limit: float = DEFAULT_BGS_LIMIT,
#         swell_limit: float = DEFAULT_SWELL_LIMIT,
#     ):
#         """Rules:

#         Use the background settlement calculated from AHN4 - AHN2
#         if that is not available use AHN4 - AHN3
#         if that is not available use AHN3 - AHN2
#         if that is not available set the value to -9999

#         also limit the value to the maximum allowed background settlement (bgs_limit)
#         and limit the value to the maximum allowed swell (swell_limit)
#         """
#         ahn4 = AHN(AHNVersion.AHN4)
#         ahn3 = AHN(AHNVersion.AHN3)
#         ahn2 = AHN(AHNVersion.AHN2)
#         agz42 = AHN(AHNVersion.AGZ42)
#         agz43 = AHN(AHNVersion.AGZ43)
#         agz32 = AHN(AHNVersion.AGZ32)

#         f = open(
#             Path(self.log_dir) / f"height_assessment_{self.levee.dtcode}_bgs.csv", "w"
#         )
#         f.write("metrering,x,y,ahn4,ahn3,ahn2,agz42,agz43,agz32,agz\n")
#         f.write("[m],[m RD],[m RD],[m],[m],[m],[m/jaar],[m/jaar],[m/jaar],[m/jaar]\n")

#         for p in self.levee.regulary_spaced_referenceline(1):
#             # get the background settlement
#             bgs = None
#             z_ahn4 = ahn4.z_at(p[1], p[2])
#             z_ahn3 = ahn3.z_at(p[1], p[2])
#             z_ahn2 = ahn2.z_at(p[1], p[2])
#             bgs42 = agz42.z_at(p[1], p[2])
#             bgs43 = agz43.z_at(p[1], p[2])
#             bgs32 = agz32.z_at(p[1], p[2])

#             bgs = None
#             if bgs42 is not None:
#                 bgs = max(bgs42, bgs_limit)
#             elif bgs43 is not None:
#                 bgs = max(bgs43, bgs_limit)
#             elif bgs32 is not None:
#                 bgs = max(bgs32, bgs_limit)
#             else:
#                 bgs = -9999

#             if bgs > 0:  # if we have swell
#                 if bgs43 is not None and bgs43 < 0:  # apply 43
#                     bgs = max(bgs43, bgs_limit)
#                 elif bgs32 is not None and bgs32 < 0:  # or if that is none, apply 32
#                     bgs = max(bgs32, bgs_limit)

#             bgs = min(bgs, swell_limit)  # apply the swell limit

#             self.background_settlement_points.append(
#                 BackgroundSettlementPoint(
#                     c=p[0],
#                     x=p[1],
#                     y=p[2],
#                     ahn4=z_ahn4,
#                     ahn3=z_ahn3,
#                     ahn2=z_ahn2,
#                     bgs42=bgs42,
#                     bgs43=bgs43,
#                     bgs32=bgs32,
#                     bgs=round(bgs, 4),
#                 )
#             )

#         f.write(
#             f"{p[0]},{p[1]},{p[2]},{z_ahn4},{z_ahn3},{z_ahn2},{bgs42},{bgs43},{bgs32},{round(bgs,4)}\n"
#         )

#         f.close()

#         plt.subplot(2, 1, 1)
#         plt.title(f"{self.levee.dtcode} height data")
#         plt.plot(
#             [p.c for p in self.background_settlement_points],
#             [p.ahn4 for p in self.background_settlement_points],
#             label="AHN4",
#         )
#         plt.plot(
#             [p.c for p in self.background_settlement_points],
#             [p.ahn3 for p in self.background_settlement_points],
#             label="AHN3",
#         )
#         plt.plot(
#             [p.c for p in self.background_settlement_points],
#             [p.ahn2 for p in self.background_settlement_points],
#             label="AHN2",
#         )
#         plt.xlabel("metrering [m]")
#         plt.ylabel("hoogte [m tov NAP]")
#         plt.legend(loc="upper left")
#         plt.grid()

#         plt.subplot(2, 1, 2)
#         plt.title(
#             f"{self.levee.dtcode} background settlement data (swell limit={swell_limit}, bgs limit={bgs_limit})"
#         )
#         plt.plot(
#             [p.c for p in self.background_settlement_points],
#             [p.bgs42 for p in self.background_settlement_points],
#             label="AGZ42",
#         )
#         plt.plot(
#             [p.c for p in self.background_settlement_points],
#             [p.bgs43 for p in self.background_settlement_points],
#             label="AGZ43",
#         )
#         plt.plot(
#             [p.c for p in self.background_settlement_points],
#             [p.bgs32 for p in self.background_settlement_points],
#             label="AGZ32",
#         )
#         plt.plot(
#             [p.c for p in self.background_settlement_points if p.bgs != -9999],
#             [p.bgs for p in self.background_settlement_points if p.bgs != -9999],
#             label="AGZ",
#         )
#         plt.xlabel("metrering [m]")
#         plt.ylabel("zetting [m/jaar]")
#         plt.legend(loc="upper left")
#         plt.grid()

#         plt.tight_layout()

#         plt.savefig(
#             Path(self.plot_dir) / f"height_assessment_{self.levee.dtcode}_bgs.jpg"
#         )
#         plt.clf()


# if __name__ == "__main__":
#     from shared.levees import Levees

#     levees = Levees()

#     for levee in tqdm(levees.items):
#         a = Assessment(
#             levee=levee,
#             year_start=2022,
#             year_prediction=2027,
#             log_dir="/home/breinbaas/Documents/logfiles",
#             plot_dir="/home/breinbaas/Documents/plots",
#         )
#         a.execute()
#         break
#         # a._calculate_bgs()
