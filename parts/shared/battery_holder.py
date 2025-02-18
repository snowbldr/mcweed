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
        return (
            Workplane()
            .box(self.width * 2, self.height - self.post_length, self.thickness * 3)
            .cut(
                Workplane()
                .box(self.width, self.height, self.thickness)
            )
            .cut(
                Workplane()
                .box(self.width * 2, self.width, self.thickness * 4)
                .rotate((0, 0, 0), (1, 0, 0), 30)
                .translate((0, -self.height / 2 + self.width / 2, 0))
            )
            .cut(
                Workplane()
                .box(self.width * 2, self.width, self.thickness * 4)
                .rotate((0, 0, 0), (1, 0, 0), -30)
                .translate((0, self.height / 2 - self.width / 2, 0))
            )
            .cut(
                Workplane()
                .box(self.width * 2, self.height, self.thickness * 4)
                .rotate((0, 0, 0), (0, 1, 0), -30)
                .translate((-self.width, 0, 0))
            )
            .cut(
                Workplane()
                .box(self.width * 2, self.height, self.thickness * 4)
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
    tab=single_strip_spring_contact


    def build(self, wall_thickness: float):
        holder_id = self.battery_diameter + 1
        holder_od = holder_id + self.thickness * 2
        inner_height = self.battery_height + self.tab.spring_compressed_depth * 2
        outer_height = inner_height + self.thickness * 2
        return (
            Workplane()
            .cylinder(height=outer_height, radius=holder_od / 2)
            .add(
                Workplane()
                .box(length=holder_od, width=holder_od / 2, height=outer_height)
                .translate((0, -holder_od / 4, 0))
            )
            .cut(
                Workplane()
                .cylinder(height=inner_height, radius=holder_id / 2)
            )
            .cut(
                Workplane()
                .cylinder(height=inner_height, radius=holder_od / 2)
                .translate((0, holder_od / 4, 0))
            )
            .add(self.tab.build().translate((0, 0, (outer_height + self.tab.thickness * 1.5) / 2)))
            .add(
                self.tab.build()
                .rotateAboutCenter((0, 1, 0), 180)
                .translate((0, 0, -(outer_height + self.tab.thickness * 1.5) / 2))
            )
            .add(
                ThermalCutoffHolder(ThermalCutoffSocket(15), 17).build(wall_thickness)
                .translate((holder_od / 2 + wall_thickness + 0.5, 0, 25))
                .rotateAboutCenter((0, 0, 1), -120)
                .rotate((0, 0, 0), (0, 0, 1), -33)
            )
            .add(
                BMSHolder().build(wall_thickness)
                .rotateAboutCenter((1, 0, 0), 90)
                .rotateAboutCenter((0, 1, 0), 180)
                .translate((0, -holder_od / 2 - wall_thickness / 2, -20))
                .rotate((0, 0, 0), (0, 0, 1), 60)
            )
        )


def battery_holder_21700():
    return BatteryHolder(22, 71)
