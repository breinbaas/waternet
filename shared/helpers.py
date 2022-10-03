from math import hypot
from pathlib import Path
from typing import List, Union
import numpy as np


def case_insensitive_glob(filepath: str, fileextension: str) -> List[Path]:
    """Find files in given path with given file extension (case insensitive)

    Arguments:
        filepath (str): path to files
        fileextension (str): file extension to use as a filter (example .gef or .csv)

    Returns:
        List(str): list of files
    """
    p = Path(filepath)
    result = []
    for filename in p.glob("**/*"):
        if str(filename.suffix).lower() == fileextension.lower():
            result.append(filename.absolute())
    return result


def polyline_to_regularly_spaced_polyline(
    polyline: List[Union[float, float]], interval: float
) -> List[Union[float, float, float]]:
    result = []
    ltot = 0
    for i in range(1, len(polyline)):
        p1 = polyline[i - 1]
        p2 = polyline[i]
        dx = p2[0] - p1[0]
        dy = p2[1] - p1[1]
        dl = hypot(dx, dy)
        ls = np.arange(0, dl, interval)
        for l in ls:
            x = p1[0] + l / dl * dx
            y = p1[1] + l / dl * dy
            result.append((ltot, round(x, 2), round(y, 2)))
            ltot += interval
    return result
