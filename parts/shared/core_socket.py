import math
from dataclasses import dataclass

from cadquery import Workplane


@dataclass
class CoreSocket:
    height: float
    inner_diameter: float
    outer_diameter: float
    vent_count: int = 8

    def stop_ring(self, wall_thickness: float):
        # we don't want any melty boys
        ring_thickness=wall_thickness*2
        return (
            Workplane()
            .cylinder(height=ring_thickness, radius=self.outer_diameter / 2)
            .cut(
                Workplane()
                .cylinder(height=wall_thickness*2, radius=self.inner_diameter/2 - wall_thickness)
            )
            .translate((0, 0, -((self.height - ring_thickness)/2)))
        )

    def build(self, wall_thickness):
        circumference = math.pi * self.inner_diameter
        vent_angle = 360 / self.vent_count
        vent_width = circumference / self.vent_count / 2
        tube = (
            Workplane()
            .cylinder(height=self.height, radius=self.outer_diameter / 2)
            .faces('>Z')
            .workplane()
            .hole(diameter=self.inner_diameter, depth=self.height)
        )
        tube.add(self.stop_ring(wall_thickness))
        for i in range(self.vent_count):
            tube = tube.cut(
                Workplane()
                .box(length=wall_thickness*2.5, width=vent_width, height=self.height)
                .translate((self.inner_diameter/2, 0))
                .rotate((0,0,0), (0,0,1), vent_angle * i)
            )
        return tube
