import argparse
from copy import copy
from dataclasses import dataclass
from cadquery import Workplane
from cadquery.vis import show_object


# This function takes a float and returns it as a string. If the number is a whole number, 
# it outputs without decimal places. Otherwise, it rounds to two decimal places.
def nice(number: float) -> str:
    return f"{int(number)}" if number.is_integer() else f"{number:.2f}"


@dataclass
class WireSizer:
    wire_length: float
    wire_diameter: float
    wall_thickness: float
    wiggle: float
    # Set text_depth to 0 to turn off text
    text_depth: float
    font: str
    label: str | None

    def build(self) -> Workplane:
        outside_width = self.wire_diameter + self.wall_thickness * 2
        outside_height = self.wire_diameter + self.wall_thickness
        with_wiggle=self.wire_diameter * (1 + self.wiggle)
        return (
            Workplane()
            .box(self.wire_length+self.wall_thickness, outside_width, outside_height)
            .faces(">Z")
            .workplane(offset=-self.text_depth)
            .text(f"{self.label} - {nice(self.wire_length)}mm x {nice(self.wire_diameter)}mm",
                  fontsize=outside_width * 0.9,
                  kind='bold',
                  distance=self.text_depth)
            .cut(
                Workplane()
                .box(length=self.wire_length, width=with_wiggle, height=with_wiggle)
                .translate((-self.wall_thickness/2, 0, -self.wall_thickness/2))
            )
        )


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        usage="This tool can be used to create a re-usable wire sizer to quickly cut many wires of the same length and diameter. After printing, cover one with with a finger, stick the wire in, cut, and dump the wire out.")
    parser.add_argument("--wall_thickness", type=float, default=2, help="The wall thickness of the sizer")
    parser.add_argument("--wiggle", type=float, default=0.1,
                        help="The percentage of wiggle room to add to the wire diameter to make it fit easier")
    parser.add_argument("--text_depth", type=float, default=0.65, help='The depth to cut the label into the top')
    parser.add_argument('--font', type=str, default='mono', help='The font to use for the label')
    parser.add_argument('--label', type=str, default='',
                        help='The label to print on the wire sizer, if not specified it defaults to wire_length x wire_diameter')
    parser.add_argument('--show_wires', default=False, action='store_true',
                        help='Whether to show the wire sizer wireframe after it is created')
    parser.add_argument("wire_length", type=float, help="The length of the wire to size")
    parser.add_argument("wire_diameter", type=float, help="The diameter of the wire to size")
    args = parser.parse_args()
    sizer_args = copy(vars(args))
    del sizer_args['show_wires']

    filename = f'{args.label.replace(' ', '_')}{'_' if args.label else ''}{args.wire_length}mm_{args.wire_diameter}mm_{args.wall_thickness}-wall_{args.wiggle}-wiggle_wire_sizer.stl'
    wire_sizer = WireSizer(**sizer_args)
    sizer = wire_sizer.build()
    sizer.export(filename)
    if args.show_wires:
        show_object(sizer.wires())

# sizer(100, 1).export('10cm_wire_sizer.stl')
# sizer(95, 1).export('95mm_wire_sizer.stl')
# sizer(100, 2).export('1mm_fiberglass_sleeve_sizer.stl')
# sizer(140, 3.5).export('2mm_fiberglass_sleeve_sizer.stl')
