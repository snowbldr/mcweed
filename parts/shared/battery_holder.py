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
                .box(self.width * 2, self.width * 2, tab_wall_thickness)
                .rotate((0, 0, 0), (1, 0, 0), 30)
                .translate((0, -self.height / 2 + self.width / 2, 0))
            )
            .cut(
                Workplane()
                .box(self.width * 2, self.width * 2, tab_wall_thickness)
                .rotate((0, 0, 0), (1, 0, 0), -30)
                .translate((0, self.height / 2 - self.width / 2, 0))
            )
            .cut(
                Workplane()
                .box(self.width * 2, self.height * 2, tab_wall_thickness)
                .rotate((0, 0, 0), (0, 1, 0), -30)
                .translate((-self.width, 0, 0))
            )
            .cut(
                Workplane()
                .box(self.width * 2, self.height * 2, tab_wall_thickness)
                .rotate((0, 0, 0), (0, 1, 0), 30)
                .translate((self.width, 0, 0))
            )
        )


# 10A BMS https://www.amazon.com/dp/B08MPXHFJB?ref_=ppx_hzsearch_conn_dt_b_fed_asin_title_1
@dataclass
class BMSHolder:
    width: float = 6.5
    length: float = 35.15
    thickness: float = 3
    window_height: float = 3.5

    def solder_window(self, wall_thickness):
        return (
            Workplane()
            .box(self.thickness * 2, self.width + wall_thickness * 2, self.window_height)
            .translate((self.thickness/2 + wall_thickness/2, -wall_thickness))
        )

    def solder_windows(self, wall_thickness):
        return (
            Workplane()
            .add(self.solder_window(wall_thickness).translate((0, 0, self.length / 2 - self.window_height / 2)))
            .add(self.solder_window(wall_thickness).translate((0, 0, -self.length / 2 + self.window_height / 2)))
            .add(self.solder_window(wall_thickness).translate((0, 0, -(self.length / 2 - 10.5))))
        )

    def bms_hole(self, wall_thickness):
        return (
            Workplane()
            .box(
                self.thickness,
                self.width + wall_thickness * 2,
                self.length
            )
            .translate((0, -wall_thickness/2 - wall_thickness, 0))
        )

    def build(self, wall_thickness):
        return (
            Workplane()
            .box(self.thickness + wall_thickness, self.width + wall_thickness, self.length + wall_thickness)
            .translate((0,-wall_thickness))
        )


# Single strip spring contacts https://www.amazon.com/dp/B07N2F5W2D?ref_=ppx_hzsearch_conn_dt_b_fed_asin_title_2
single_strip_spring_contact = BatteryTab(
    thickness=0.6,
    width=5.3,
    height=24.25,
    spring_height=9.25,
    spring_center=6,
    spring_compressed_depth=4.5,
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
                piece
                .translate((holder_od / 2 - 0.125, - bms_holder.width / 2 - wall_thickness / 2,
                            -wall_thickness / 2))
                .rotateAboutCenter((0, 0, 1), -27)
                # .translate((-wall_thickness * .66, -wall_thickness * .66))
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
            # square bottom bit to help with stability and hold stuff
            .add(
                Workplane()
                .box(length=holder_od / 2, width=holder_od / 2,
                     height=bms_holder.length + cutoff_holder.socket.fuse_radius * 4)
                .translate((holder_od / 4, -holder_od / 4, wall_thickness * 3))
            )
            # battery cavity
            .cut(
                Workplane()
                .cylinder(height=inner_height, radius=holder_id / 2)
            )
            # battery tabs
            .add(self.tab.build()
                 .translate(
                (0, 0, (outer_height + wall_thickness + self.tab.thickness * 2) / 2 - self.tab.thickness / 2))
                 .rotateAboutCenter((0, 0, 1), 45)
                 )
            .add(
                self.tab.build()
                .rotateAboutCenter((0, 1, 0), 180)
                .translate((0, 0, -(outer_height + wall_thickness + self.tab.thickness) / 2))
                .rotateAboutCenter((0, 0, 1), 45)
            )
            # Cut into the sides to let the tabs get far enough in and hit the center
            .cut(
                Workplane()
                .box(length=holder_od, width=holder_od / 4 + 1.75, height=outer_height + wall_thickness * 2)
                # inset 2.25mm as that's where it fits nice
                .translate((0, (holder_od / 2 + self.tab.width / 2) - 2.5, 0))
                .rotate((0, 0, 0), (0, 0, 1), 45)
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
            .cut(place_bms(bms_holder.bms_hole(wall_thickness)))
            # Cut solder windows through main body
            .cut(place_bms(bms_holder.solder_windows(wall_thickness)))
            # Cut some of the main body off to allow a finger to get in and pop the battery out
            .cut(
                Workplane()
                .box(length=holder_od, width=holder_od, height=outer_height + wall_thickness * 2)
                .rotateAboutCenter((0, 0, 1), 45)
                .translate((holder_od * .3, holder_od * .71))
            )
            .cut(
                Workplane()
                .box(length=holder_od, width=holder_od, height=outer_height + wall_thickness * 2)
                .translate((holder_od * .8, holder_od * .5))
            )
        )


def battery_holder_21700():
    return BatteryHolder(21, 70)
