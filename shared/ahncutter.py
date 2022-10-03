from typing import Optional
import numpy as np

from .ahn import AHNVersion, AHN, Tile


class AHNCutter:
    def __init__(self):
        self.ahn_data = {
            AHNVersion.AHN2: AHN(version=AHNVersion.AHN2),
            AHNVersion.AHN3: AHN(version=AHNVersion.AHN3),
            AHNVersion.AHN4: AHN(version=AHNVersion.AHN4),
            # AHNVersion.AGZ32: AHN(version=AHNVersion.AGZ32),
            # AHNVersion.AGZ42: AHN(version=AHNVersion.AGZ42),
            # AHNVersion.AGZ43: AHN(version=AHNVersion.AGZ43),
        }

    def execute(
        self,
        left: float,
        top: float,
        right: float,
        bottom: float,
        ahn_version: AHNVersion,
    ) -> Optional[Tile]:
        ahn_data = self.ahn_data[ahn_version]

        # this will only work if a levee is max 2x2 tiles which is a valid assumption (I think... ;-)
        tile_tl = ahn_data.get_tile_by_xy(left, top)
        tile_tr = ahn_data.get_tile_by_xy(right, top)
        tile_bl = ahn_data.get_tile_by_xy(left, bottom)
        tile_br = ahn_data.get_tile_by_xy(right, bottom)

        # start with the data of the topleft tile
        if tile_tl is None:
            print(f"Could not find tiles for {self.route.name}.")

        tile_tl._read()  # force to read the data and store the data
        data = tile_tl.data  # np.array

        # if there is another tile on the right and it is not the
        # same as tile_tl add it as a column to the final matrix
        if tile_tr != tile_tl:
            if tile_tr is not None:
                tile_tr._read()
                data = np.hstack((data, tile_tr.data))
            else:
                print(f"Could not find tiles for {self.route.name}.")

        # if there is another tile on the bottom..
        if tile_bl is not None and tile_bl != tile_tl:
            tile_bl._read()
            if tile_tr != tile_tl:  # and if we already added a column..
                # then join both first horizontally (or else we could end up with a funny but invalid numpy array)
                if tile_br is not None:
                    tile_br._read()
                    bdata = np.hstack((tile_bl.data, tile_br.data))
                else:
                    print(f"Could not find tiles for {self.route.name}.")
            else:  # ok, just one tile so far, now just join one, no need to add the bottomright one
                bdata = tile_bl.data

            # and now add this matrix bdata as a new row to the final matrix
            data = np.vstack((data, bdata))

        # now limit the size of the matrix based on the boundaries
        res = tile_tl.resolution
        nodata = tile_tl.nodata
        xtl, ytl = tile_tl.left, tile_tl.top

        # find the index in the matrix
        idx_x1 = int((left - xtl) / res)
        idx_y1 = data.shape[0] + int((ytl - top) / res)
        idx_x2 = int((right - xtl) / res)
        idx_y2 = data.shape[0] + int((ytl - bottom) / res)

        # select the final matrix
        selection = data[idx_y1:idx_y2, idx_x1:idx_x2]

        return Tile(
            filename="",
            left=left,
            right=right,
            bottom=bottom,
            top=top,
            ncols=idx_x2 - idx_x1,
            nrows=idx_y2 - idx_y1,
            data=selection,
            resolution=res,
            nodata=nodata,
        )
