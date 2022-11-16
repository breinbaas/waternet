from pydantic import BaseModel


class Tree(BaseModel):
    x_rd: float = 0.0
    y_rd: float = 0.0
    id: int = -1
    stem_id: int = -1
    height_cr: float = 0.0
    method: str = ""
    management: str = ""
