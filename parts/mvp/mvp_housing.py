from dataclasses import dataclass

from cadquery import Workplane

from parts.shared.battery_holder import BatteryHolder
from parts.shared.core_socket import CoreSocket


@dataclass
class MVPHousing:
    core_socket: CoreSocket
    battery_holder: BatteryHolder

    def build(self, wall_thickness):
        housing = Workplane()
        housing.add(self.core_socket.build(wall_thickness))
        housing.add(
            self.battery_holder.build(wall_thickness)
            .translate((-self.core_socket.outer_diameter(wall_thickness), 0, 0))
        )
        return housing
