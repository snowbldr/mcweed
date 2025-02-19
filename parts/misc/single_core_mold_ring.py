from cadquery import Workplane

ring = (
    Workplane()
    .cylinder(height=45, radius=16.5)
    .faces('>Z')
    .hole(diameter=30, depth=45)
)

ring.export('single_core_mold_ring.stl')