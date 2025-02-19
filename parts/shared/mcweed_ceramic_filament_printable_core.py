from dataclasses import dataclass

from cadquery import Workplane, Wire

from parts.shared.thermal_cutoff import ThermalCutoffSocket


@dataclass
class McWeedBowl:
    height: float
    inner_diameter: float
    outer_diameter: float


@dataclass
class McWeedCoreAirway:
    inner_diameter: float
    turns: float
    height: float
    count: int

    def offset(self, bowl_inner_diameter: float):
        return bowl_inner_diameter + self.inner_diameter

    def angle(self):
        return 360 / self.count

    def airway_helix(self, bowl: McWeedBowl):
        height = self.height + self.inner_diameter
        pitch = height / self.turns
        offset = self.offset(bowl.inner_diameter/2 - (bowl.outer_diameter-bowl.inner_diameter) - .35)
        return (
            Workplane()
            .center(offset + 0.6, 0)
            .ellipseArc(x_radius=self.inner_diameter * 1.1, y_radius=self.inner_diameter / 2, makeWire=True)
            .sweep(Workplane(
                Wire.makeHelix(pitch=pitch, height=height, radius=offset * 2)
            ), isFrenet=True)
            .translate((0, 0, -self.inner_diameter * 3))
        )


@dataclass
class McWeedCeramicFilamentPrintableCore:
    bowl: McWeedBowl
    airway: McWeedCoreAirway
    wire_ring_depth: float

    def height(self):
        return self.bowl.height + self.airway.height

    def build(self):
        # Make the main body and cut the bowl hole
        core = (
            Workplane()
            .cylinder(radius=self.bowl.outer_diameter / 2, height=self.height())
            .cut(Workplane().cylinder(height=self.bowl.height, radius=self.bowl.inner_diameter / 2).translate(
                (0, 0, -(self.height() - self.bowl.height) / 2)))
        )

        # Cut the airways
        for i in range(self.airway.count):
            core = core.cut(
                self.airway.airway_helix(self.bowl)
                .rotate((0, 0, 0), (0, 0, 1), i * self.airway.angle())
            )

        # Cut the bottom hole with a dome to stuff the thermal fuse in
        core = core.cut(
            ThermalCutoffSocket(height=self.airway.height, fuse_radius=2.5, wire_radius=0.6).build()
            .rotateAboutCenter((0, 1, 0), 180)
            .translate((-0.5, 0, (self.height() - self.airway.height) / 2 + 3.25))
        )

        # Flip it over and cut countersinks for the wires
        return (
            core.rotateAboutCenter((0, 1, 0), 180)
            # bottom ring
            .cut(wire_ring(self).translate((0, 0, -(self.airway.height / 2) + self.wire_ring_depth * 0.65)))
            # bowl side ring
            .cut(wire_ring(self).translate((0, 0, (self.airway.height / 2) - self.wire_ring_depth * 0.25)))
        )


def wire_ring(core: McWeedCeramicFilamentPrintableCore):
    radius = core.airway.offset(core.bowl.inner_diameter) - (core.airway.inner_diameter * 1.15) / 2 + 0.6
    return (
        Workplane()
        .cylinder(height=core.wire_ring_depth, radius=radius)
        .faces('>Z')
        .workplane()
        .hole(diameter=(radius - core.wire_ring_depth) * 2, depth=core.wire_ring_depth)
    )
