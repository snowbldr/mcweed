from cadquery import Workplane, Wire
from cadquery.vis import show_object

bowl_height = 11
bowl_id = 15.5
bowl_od = 18
airway_id = 1.75
airway_offset = (bowl_id - airway_id) / 2
airway_turns = 0.33
airway_height = 19
airway_count = 8
airway_angle = 360 / airway_count
core_height = bowl_height + airway_height
wire_ring_depth=1.75


def airway_helix():
    height = airway_height + airway_id
    pitch = height / airway_turns
    return (
        Workplane()
        .center(airway_offset+0.6, 0)
        .ellipseArc(x_radius=airway_id*1.1, y_radius=airway_id/2, makeWire=True)
        .sweep(Workplane(
            Wire.makeHelix(pitch=pitch, height=height, radius=airway_offset*2)
        ), isFrenet=True)
        .translate((0, 0, -airway_id*3))
    )


def wire_ring():
    radius = airway_offset-(airway_id*1.15)/2 + 0.6
    return (
        Workplane()
        .cylinder(height=wire_ring_depth, radius=radius)
        .faces('>Z')
        .workplane()
        .hole(diameter=(radius - wire_ring_depth) * 2, depth=wire_ring_depth)
    )


def dome(id, od):
    return (
        Workplane()
        .sphere(radius=od / 2)
        .cut(Workplane().sphere(radius=id / 2))
        .cut(Workplane().box(od, od, od).translate((0, 0, -od / 2)))
    )


def thermal_fuse_hole():
    return (
        Workplane()
        .cylinder(radius=2.5, height=airway_height)
        .cut(
            dome(5, 8)
            .translate((0, 0, (airway_height - 5) / 2))
        )
        .add(
            Workplane()
            .cylinder(radius=0.6, height=airway_height - 1.25)
            .translate((2.25 + 0.6, 0, -1.25))
        )
        .add(
            Workplane()
            .box(length=2.5, width=1.2, height=airway_height - 1.25)
            .translate((2.25-0.6, 0, -1.25))
        )
    )


# Make the main body and cut the bowl hole
core = (
    Workplane()
    .cylinder(radius=bowl_od / 2, height=core_height)
    .cut(Workplane().cylinder(height=bowl_height, radius=bowl_id / 2).translate(
        (0, 0, -(core_height - bowl_height) / 2)))
)

# Cut the airways
for i in range(airway_count):
    core = core.cut(airway_helix().rotate((0, 0, 0), (0, 0, 1), i * airway_angle))

# Cut the bottom hole with a dome to stuff the thermal fuse in
core = core.cut(
    thermal_fuse_hole()
    .rotateAboutCenter((0, 1, 0), 180)
    .translate((-0.5, 0, (core_height - airway_height) / 2 + 3.25))
)

# Flip it over and cut countersinks for the wires
core = (
    core.rotateAboutCenter((0, 1, 0), 180)
    # bottom ring
    .cut(wire_ring().translate((0, 0, -(airway_height / 2) + wire_ring_depth*0.65)))
    # bowl side ring
    .cut(wire_ring().translate((0, 0, (airway_height/ 2) - wire_ring_depth*0.25)))
)

core.export('mvp_core.stl')
show_object(core.wires())
