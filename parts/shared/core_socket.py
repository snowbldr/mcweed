import math
from dataclasses import dataclass

from cadquery import Workplane

from parts.shapes.oring import Oring


@dataclass
class CoreSocket:
    height: float
    inner_diameter: float
    fin_depth: float
    oring: Oring

    def outer_diameter(self, wall_thickness):
        return self.inner_diameter + wall_thickness * 2 + self.fin_depth * 2

    def fin_width(self, wall_thickness):
        return self.outer_diameter(wall_thickness) - wall_thickness * 2

    def cooling_fin(self, wall_thickness: float):
        return (
            Workplane()
            .box(wall_thickness, self.outer_diameter(wall_thickness) - self.fin_depth, self.height, centered=True)
        )

    def build(self, wall_thickness):
        fin_count = math.floor(((self.fin_width(wall_thickness) * math.pi) / (wall_thickness * 2)) / 2)
        fin_angle = 360 / fin_count

        tube = (
            Workplane()
            .cylinder(height=self.height, radius=self.outer_diameter(wall_thickness) / 2)
            .faces('>Z')
            .workplane()
            .hole(diameter=self.inner_diameter, depth=self.height)
        )
        for i in range(fin_count):
            tube = tube.cut(self.cooling_fin(wall_thickness)
                            .rotate((0, 0, 0), (0, 0, 1), i * fin_angle)
                            .translate((0, 0, -self.oring.thickness - wall_thickness))
                            )
        tube = tube.cut(
            self.oring.build()
            .add(
                Workplane()
                .cylinder(height=self.oring.thickness, radius=self.oring.outer_diameter / 2 + wall_thickness * 0.75)
                .translate((0, 0, self.oring.thickness * .1))
            )
            .translate((0, 0, (self.height - self.oring.thickness) / 2))
        )
        return tube
