from tqdm import tqdm

from shared.settings import CPTS_BOREHOLES_PATH
from shared.helpers import case_insensitive_glob


def update_gis_csv():
    geffiles = case_insensitive_glob(CPTS_BOREHOLES_PATH, ".gef")
    fout = open("cptboreholelist.csv", "w")
    fout.write(f"x,y,type,filename\n")
    for gf in tqdm(geffiles):
        x = 0
        y = 0
        gftype = ""

        lines = open(gf, "r").readlines()
        for line in lines:
            if line.find("PROCEDURECODE") > -1 or line.find("REPORTCODE") > -1:
                if line.find("CPT") > -1:
                    gftype = "cpt"
                elif line.find("BORE") > -1:
                    gftype = "borehole"
            if line.find("XYID") > -1:
                try:
                    _, argline = line.split("=")
                    args = argline.split(",")
                    x = float(args[1])
                    y = float(args[2])
                except:
                    pass

        if x > 0 and gftype != "":
            fout.write(f"{x},{y},{gftype},{gf}\n")

    fout.close()


if __name__ == "__main__":
    update_gis_csv()
