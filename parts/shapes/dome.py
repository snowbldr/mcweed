from cadquery import Workplane


def dome(inner_diameter, outer_diameter):
    return (
        Workplane()
        .sphere(radius=outer_diameter / 2)
        .cut(Workplane().sphere(radius=inner_diameter / 2))
        .cut(
            Workplane()
            .box(outer_diameter, outer_diameter, outer_diameter)
            .translate((0, 0, -outer_diameter / 2))
        )
    )
