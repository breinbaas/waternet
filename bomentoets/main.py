import shapefile
from tqdm import tqdm
from pathlib import Path


from shared.objects import Tree
from shared.levees import Levees
from shared.settings import *

# Get all trees and define the levee they belong to and calculate the distance to the reference line

# step 1. get all trees from the source


# we need to be able to add some info to the trees so store them in a new format with 2 added properties
class TreeWithLeveesection(Tree):
    levee_code: str = ""
    distance_to_referenceline = -1


trees = []
print("Reading trees...")
sf = shapefile.Reader(TREES_SHAPE)
for sr in tqdm(sf.shapeRecords()):
    point = sr.shape.points[0]
    if sr.record["height_cr"] is not None:
        height = sr.record["height_cr"]
    else:
        height = 0.0

    trees.append(
        TreeWithLeveesection(
            x_rd=point[0],
            y_rd=point[1],
            id=sr.record["tree_id"],
            stem_id=sr.record["stem_id"],
            height_cr=height,
            method=sr.record["method"],
            management=sr.record["management"],
        )
    )

# step 2. get the levee section for each tree, the distance to the referenceline is leading (so a tree gets assigned to the closest referenceline)

# 2a,
# walk through all leveesections, determine the bounding box with some offset, find all trees in this area and check the distance to the referenceline
# if the distance is smaller than the (maybe) already assigned one, assign the tree to this levee
print("Assigning trees to levees.. might take some minutes")
levees = Levees()
for levee in tqdm(levees.items):
    left, top, right, bottom = levee.bounding_box(offset=100)
    for i, tree in enumerate(trees):
        if (
            left <= tree.x_rd
            and tree.x_rd <= right
            and bottom <= tree.y_rd
            and tree.y_rd <= top
        ):
            # get the distance to the referenceline
            dl = levee.closest_referenceline_point_to(tree.x_rd, tree.y_rd)
            if (
                trees[i].distance_to_referenceline == -1
                or dl < trees[i].distance_to_referenceline
            ):
                trees[i].levee_code = levee.dtcode
                trees[i].distance_to_referenceline = dl

# step 3. write the results to a new shape with the tree information and added levee code and distance to referenceline
sf_out = shapefile.Writer(
    str(Path(TREES_OUTPUT_DIR) / "trees_with_levee_information.shp")
)
sf_out.field("tree_id", "N")
sf_out.field("stem_id", "N")
sf_out.field("height_cr", "F", decimal=2)
sf_out.field("method", "C", size=40)
sf_out.field("management", "C", size=40)
sf_out.field("levee_code", "C", size=10)
sf_out.field("distance", "F", decimal=2)

for tree in [t for t in trees if t.levee_code != ""]:
    sf_out.point(tree.x_rd, tree.y_rd)
    sf_out.record(
        tree.id,
        tree.stem_id,
        tree.height_cr,
        tree.method,
        tree.management,
        tree.levee_code,
        tree.distance_to_referenceline,
    )
