from dataclasses import dataclass

from cadquery import Workplane
from cadquery.vis import show_object

from parts.mvp.mvp_housing import MVPHousing
from parts.shapes.oring import Oring
from parts.shared.battery_holder import battery_holder_21700
from parts.shared.core_socket import CoreSocket
from parts.shared.mcweed_ceramic_filament_printable_core import McWeedBowl, McWeedCeramicFilamentPrintableCore, McWeedCoreAirway


@dataclass
class MVP:
    core: McWeedCeramicFilamentPrintableCore
    housing: MVPHousing
    wall_thickness: float

    def build(self):
        return (
            Workplane()
            .add(self.housing.build(self.wall_thickness))
            .add(self.core.build().translate((0, 50)))
        )

wall_thickness=1.25

core = McWeedCeramicFilamentPrintableCore(
    bowl=McWeedBowl(height=11, inner_diameter=15.5, outer_diameter=18),
    airway=McWeedCoreAirway(inner_diameter=1.75, turns=0.33, height=19, count=8),
    wire_ring_depth=1.75
)
socket = CoreSocket(
    height=core.height() + wall_thickness,
    inner_diameter=core.bowl.outer_diameter + 0.25,
    outer_diameter=24
)
# housing = MVPHousing(core_socket=socket, battery_holder=battery_holder_21700())
#
# mvp = MVP(
#     core=core,
#     housing=housing,
#     wall_thickness=1.25
# )

# mvp.housing.core_socket.build(mvp.wall_thickness).export('core_socket.stl')
# show_object(mvp.build())
socket = socket.build(1.25)
socket.export('socket.stl')
show_object(socket)