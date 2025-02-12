from cadquery import Workplane


Workplane().cylinder(radius=14.5, height=30).faces(">Z").hole(diameter=25, depth=30, clean=True).export('tube.step')

