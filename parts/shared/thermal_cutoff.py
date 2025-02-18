from dataclasses import dataclass

from cadquery import Workplane

from parts.shapes.dome import dome


@dataclass
class ThermalCutoffSocket:
    height: float
    fuse_radius: float = 2.5
    wire_radius: float = 0.6

    def build(self):
        # TODO I forgot what this number does and it's all fucked up when I change it hahaha
        height_shift = 1.25
        return (
            Workplane()
            .cylinder(radius=self.fuse_radius, height=self.height)
            .cut(
                dome(self.fuse_radius * 2, 8)
                .translate((0, 0, (self.height - self.fuse_radius * 2) / 2))
            )
            .add(
                Workplane()
                .cylinder(radius=self.wire_radius, height=self.height - height_shift)
                .translate((2.25 + self.wire_radius, 0, -height_shift))
            )
            .add(
                Workplane()
                .box(length=self.fuse_radius, width=1.2, height=self.height - height_shift)
                .translate((2.25 - self.wire_radius, 0, -height_shift))
            )
        )


@dataclass
class ThermalCutoffHolder:
    socket: ThermalCutoffSocket
    height: float

    def build(self, wall_thickness):
        return (
            Workplane()
            .cylinder(radius=self.socket.fuse_radius + wall_thickness, height=self.height)
            .cut(
                self.socket.build()
            )
        )
