from cadquery import Workplane
from cadquery.vis import show_object

from core_press.mcweed_pressable_core import McWeedPressableCore, McWeedPressableCoreAirway
from parts.shared.mcweed_ceramic_filament_printable_core import McWeedBowl

core = McWeedPressableCore(
    bowl=McWeedBowl(height=11, inner_diameter=15.5, outer_diameter=18),
    airway=McWeedPressableCoreAirway(inner_diameter=1.75, turns=0.33, height=19, count=8),
    wire_ring_depth=1.75
)

mold_thickness = 2.5

press_bottom = (
    Workplane()
    .add(
        Workplane()
        .cylinder(radius=core.bowl.outer_diameter / 2 + mold_thickness, height=core.height() + mold_thickness * 2)
    )
    .add(
        core.build()
        .translate((0, 0, -(mold_thickness**2)))
    )
    .cut(
        Workplane()
        .cylinder(radius=core.bowl.outer_diameter / 2, height=core.height()+mold_thickness*2)
        .translate((0, 0, -0.390625 -mold_thickness - core.bowl.height - core.wire_ring_depth ))

    )
)

show_object(press_bottom.wires())
