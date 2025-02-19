from dataclasses import dataclass

from cadquery import Workplane

from parts.shapes.dome import dome


@dataclass
class ThermalCutoffSocket:
    height: float
    fuse_radius: float = 2.5
    wire_radius: float = 0.6

    def build(self):
        return (
            Workplane()
            # cutoff body
            .cylinder(radius=self.fuse_radius, height=self.height)
            # dome top
            .cut(
                dome(self.fuse_radius * 2, self.fuse_radius * 4)
                .translate((0, 0, (self.height - self.fuse_radius * 2) / 2))
            )
            # wire cut
            .add(
                Workplane()
                .cylinder(radius=self.wire_radius, height=self.height )
                .translate((self.fuse_radius+self.wire_radius/2, -self.wire_radius/2, -self.wire_radius/2))
            )
            # connect wire cut to fuse body
            .add(
                Workplane()
                .box(length=self.fuse_radius, width=self.wire_radius*2, height=self.height, centered=(False, True, True))
                .translate((self.wire_radius/2, -self.wire_radius/2, -self.wire_radius/2))
            )
        )


@dataclass
class ThermalCutoffHolder:
    socket: ThermalCutoffSocket
    height: float

    def build(self, wall_thickness):
        return (
            Workplane()
            .cylinder(radius=self.socket.fuse_radius + wall_thickness + self.socket.wire_radius, height=self.height)
            .cut(
                self.socket.build()
                .translate((0, 0, -wall_thickness/2))
            )
            # cut a channel to tuck the lower wire into and avoid contact
            .cut(
                Workplane()
                .box(length=self.socket.wire_radius*2, width=self.socket.fuse_radius*2, height=9)
                .translate((self.socket.fuse_radius+self.socket.wire_radius-0.3, 2.25, -(self.height/2 - 8)))
            )
        )
