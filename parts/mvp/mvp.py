from dataclasses import dataclass

from cadquery import Workplane
from cadquery.vis import show_object

from parts.mvp.mvp_housing import MVPHousing
from parts.shapes.oring import Oring
from parts.shared.battery_holder import battery_holder_21700
from parts.shared.core_socket import CoreSocket
from parts.shared.mcweed_core import McWeedBowl, McWeedCore, McWeedCoreAirway


@dataclass
class MVP:
    core: McWeedCore
    housing: MVPHousing
    wall_thickness: float

    def build(self):
        return (
            Workplane()
            .add(self.housing.build(self.wall_thickness))
            .add(self.core.build().translate((0, 50)))
        )


socket = CoreSocket(
    height=42,
    inner_diameter=18.25,
    fin_depth=5,
    oring=Oring(thickness=3, outer_diameter=23, inner_diameter=17)
)
housing = MVPHousing(core_socket=socket, battery_holder=battery_holder_21700())
core = McWeedCore(
    bowl=McWeedBowl(height=11, inner_diameter=15.5, outer_diameter=18),
    airway=McWeedCoreAirway(inner_diameter=1.75, turns=0.33, height=19, count=8),
    wire_ring_depth=1.75
)

mvp = MVP(
    core=core,
    housing=housing,
    wall_thickness=1.25
)


show_object(mvp.build())
