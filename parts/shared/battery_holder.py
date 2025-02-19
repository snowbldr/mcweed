from dataclasses import dataclass

from cadquery import Workplane

from parts.shared.thermal_cutoff import ThermalCutoffHolder, ThermalCutoffSocket


@dataclass
class BatteryHolder:
    height: float
    diameter: float


battery_21700 = BatteryHolder(height=71, diameter=22)


@dataclass
class BatteryTab:
    thickness: float
    width: float
    height: float
    spring_height: float
    spring_center: float
    spring_compressed_depth: float
    post_length: float

    def build(self):
        tab_wall_thickness = 1.25 + self.thickness
        return (
            Workplane()
            .box(self.width * 2, self.height - self.post_length, tab_wall_thickness)
            .cut(
                Workplane()
                .box(self.width, self.height, self.thickness)
                .translate((0, 0, - tab_wall_thickness / 2 + self.thickness / 2))
            )
            .cut(
                Workplane()
                .box(self.width * 2, self.width, tab_wall_thickness)
                .rotate((0, 0, 0), (1, 0, 0), 30)
                .translate((0, -self.height / 2 + self.width / 2, 0))
            )
            .cut(
                Workplane()
                .box(self.width * 2, self.width, tab_wall_thickness)
                .rotate((0, 0, 0), (1, 0, 0), -30)
                .translate((0, self.height / 2 - self.width / 2, 0))
            )
            .cut(
                Workplane()
                .box(self.width * 2, self.height, tab_wall_thickness)
                .rotate((0, 0, 0), (0, 1, 0), -30)
                .translate((-self.width, 0, 0))
            )
            .cut(
                Workplane()
                .box(self.width * 2, self.height, tab_wall_thickness)
                .rotate((0, 0, 0), (0, 1, 0), 30)
                .translate((self.width, 0, 0))
            )
        )


# 10A BMS https://www.amazon.com/dp/B08MPXHFJB?ref_=ppx_hzsearch_conn_dt_b_fed_asin_title_1
@dataclass
class BMSHolder:
    width: float = 7.6
    length: float = 35.15
    thickness: float = 3

    def build(self, wall_thickness):
        center_translate = self.length / 2 - 3.5 / 2
        return (
            Workplane()
            .box(self.width + wall_thickness, self.length + wall_thickness, self.thickness + wall_thickness)
            .cut(
                Workplane()
                .box(self.width + wall_thickness, self.length, self.thickness)
                .translate((-wall_thickness / 2, 0, 0))
            )
            .cut(
                # cut for battery solder pad
                Workplane()
                .box(self.width, 3.5, self.thickness)
                .translate((0, center_translate, wall_thickness))
            )
            .cut(
                # cut for other battery solder pad
                Workplane()
                .box(self.width, 3.5, self.thickness)
                .translate((0, -center_translate, wall_thickness))
            )
            .cut(
                # cut for power solder pads
                Workplane()
                .box(self.width, 3.5, self.thickness)
                .translate((0, center_translate - 9.75, wall_thickness))
            )
        )


# Single strip spring contacts https://www.amazon.com/dp/B07N2F5W2D?ref_=ppx_hzsearch_conn_dt_b_fed_asin_title_2
single_strip_spring_contact = BatteryTab(
    thickness=0.3,
    width=5.08,
    height=24.25,
    spring_height=9.25,
    spring_center=6,
    spring_compressed_depth=6,
    post_length=5
)


@dataclass
class BatteryHolder:
    battery_diameter: float
    battery_height: float
    thickness: float = 1.25
    tab = single_strip_spring_contact

    def build(self, wall_thickness: float):
        holder_id = self.battery_diameter + 1
        holder_od = holder_id + self.thickness * 2
        inner_height = self.battery_height + self.tab.spring_compressed_depth * 2
        outer_height = inner_height + self.thickness * 2
        bms_holder = BMSHolder()

        def place_bms(piece):
            return (
                piece.rotateAboutCenter((1, 0, 0), 90)
                .rotateAboutCenter((0, 1, 0), 180)
                .translate((0, -holder_od / 2 - wall_thickness / 2))
                .rotate((0, 0, 0), (0, 0, 1), 63)
            )

        def place_thermal_cutoff(piece):
            return (
                piece.translate((-cutoff_holder.height / 2, 0))
                .rotateAboutCenter((1, 0, 0), 90)
                .translate((
                    holder_od - cutoff_holder.socket.fuse_radius - wall_thickness,
                    -(holder_od / 2 - cutoff_holder.height / 2) - wall_thickness / 2 + 0.203125,
                    bms_holder.length / 2 + wall_thickness + cutoff_holder.socket.fuse_radius
                ))
            )

        cutoff_holder_height = 15.91
        cutoff_holder = ThermalCutoffHolder(ThermalCutoffSocket(cutoff_holder_height), cutoff_holder_height)
        cutoff_holder_od = cutoff_holder.socket.fuse_radius * 2 + wall_thickness * 2
        return (
            Workplane()
            # main battery cylinder
            .cylinder(height=outer_height, radius=holder_od / 2)
            # square bottom
            .add(
                Workplane()
                .box(length=holder_od, width=holder_od / 2, height=outer_height)
                .translate((0, -holder_od / 4, 0))
            )
            # battery cavity
            .cut(
                Workplane()
                .cylinder(height=inner_height, radius=holder_id / 2)
            )
            # cut off top of battery cylinder
            .cut(
                Workplane()
                .cylinder(height=inner_height, radius=holder_od / 2)
                .translate((0, holder_od / 4, 0))
            )
            # battery tabs
            .add(self.tab.build()
                 .translate((0, 0, (outer_height + wall_thickness + self.tab.thickness * 2) / 2))
                 .rotateAboutCenter((0, 0, 1), 63)
                 )
            .add(
                self.tab.build()
                .rotateAboutCenter((0, 1, 0), 180)
                .translate((0, 0, -(outer_height + wall_thickness + self.tab.thickness) / 2))
                .rotateAboutCenter((0, 0, 1), 63)
            )
            # Add the Thermal cutoff holder
            .add(
                place_thermal_cutoff(
                    cutoff_holder.build(wall_thickness)
                    # cut the back bit of the holder off to allow close contact to battery
                    .cut(
                        Workplane()
                        .box(cutoff_holder_od, cutoff_holder_od, cutoff_holder.height)
                        .translate((-6.15, 0))
                    )
                )
            )
            # Cut thermal fuse hole through main body
            .cut(
                place_thermal_cutoff(
                    Workplane()
                    .cylinder(radius=cutoff_holder.socket.fuse_radius, height=cutoff_holder.height,
                              centered=(True, True, False))
                    .translate((0, wall_thickness, -cutoff_holder_od))
                )
            )
            # Add the bms holder
            .add(place_bms(bms_holder.build(wall_thickness)))
            # Cut bms hole through main body
            .cut(place_bms(
                Workplane()
                .box(bms_holder.width, bms_holder.length, bms_holder.thickness)
                .translate((wall_thickness - 0.05, -1.69 / 4, -1.69 / 4))
            ))
            # Place the holder on it's flat back, ready to print
            .rotateAboutCenter((0,1,0), 90)
            .rotateAboutCenter((1,0,0), 90)
        )


def battery_holder_21700():
    return BatteryHolder(22, 71)
