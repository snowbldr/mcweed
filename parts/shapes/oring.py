from dataclasses import dataclass

from cadquery import Workplane


@dataclass
class Oring:
    thickness: float
    outer_diameter: float
    inner_diameter: float

    def build(self):
        return (
            Workplane('XZ')
            .circle(radius=self.thickness / 2)
            .revolve(360, (-self.outer_diameter / 2, 0, 0), (-self.outer_diameter / 2, 1, 0))
            .translate((self.outer_diameter / 2, 0, 0))
        )
