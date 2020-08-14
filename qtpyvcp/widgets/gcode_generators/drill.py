from __future__ import division
from base_generator import BaseGenerator

import math


class Drill(BaseGenerator):
    """This class generates GCode for drilling/tapping cycles.

    The canned drilling cycles G81 (drill), G74 (left hand tap),
    G84 (right hand tap), G82 (dwell), G83 (peck), and G73
    (chip-breaking), are all supported.

    The tapping cycle is intended for tapping with a floating chuck
    and dwell at the bottom of the hole.

    Tapping cycles will automatically set the z feed based on the
    given spindle rpm (speed), and thread pitch (1/TPI). If the
    spindle RPM is positive, a right hand tapping operation (G84)
    will be performed. If the spindle RPM is negative, a left hand
    tapping operation (G74) will be performed.

    The bolt_hole_circle_xy method will add the x, y positions for
    a bolt hole circle, Starting at a the given angle, it will calculate
    the x, y positions along a circle of a given diameter for the number
    of holes specified and add them to the list of hole locations.

    After the bolt hole locations have been added, you can elect to run
    a drill, tap, peck, dwell, or chip-breaking cycle.
    """

    def __init__(self):
        super(Drill, self).__init__()
        self.hole_locations = []

    def drill(self):
        output = self.preamble()
        output.append('G98 G81 R%.4f Z%.4f F%.4f ' % (self.z_start,  self.z_end, self.z_feed))
        output.extend(self.add_holes_())
        output.extend(self.epilog())

        return ''.join(output)

    def tap(self, pitch):
        self.z_feed = abs(self.speed * pitch)

        output = self.preamble()
        output.append('G98 G%i R%.4f Z%.4f F%.4f S%.4f ' %
                      (74 if self.speed < 0. else 84, self.z_start,  self.z_end, self.z_feed, abs(self.speed)))
        output.extend(self.add_holes_())
        output.extend(self.epilog())

        return ''.join(output)

    def dwell(self, dwell_time):
        output = self.preamble()
        output.append('G98 G82 R%.4f Z%.4f P%.4f F%.4f ' % (self.z_start,  self.z_end, dwell_time, self.z_feed))
        output.extend(self.add_holes_())
        output.extend(self.epilog())

        return ''.join(output)

    def peck(self, delta):
        output = self.preamble()
        output.append('G98 G83 R%.4f Z%.4f Q%.4f F%.4f ' % (self.z_start,  self.z_end, delta, self.z_feed))
        output.extend(self.add_holes_())
        output.extend(self.epilog())

        return ''.join(output)

    def chip_break(self, delta):
        output = self.preamble()
        output.append('G98 G73 R%.4f Z%.4f Q%.4f F%.4f ' % (self.z_start,  self.z_end, delta, self.z_feed))
        output.extend(self.add_holes_())
        output.extend(self.epilog())

        return ''.join(output)

    def bolt_hole_circle_xy(self, num_holes, circle_diam, circle_center, start_angle=0):
        curr_angle = start_angle
        angle_step = (360. / num_holes)

        for _ in range(0, num_holes):
            x = math.cos(math.radians(curr_angle)) * (circle_diam / 2.)
            y = math.sin(math.radians(curr_angle)) * (circle_diam / 2.)
            x += circle_center[0]
            y += circle_center[1]
            curr_angle += angle_step
            self.hole_locations.append((x, y))

    def add_holes_(self):
        output = []
        for hole in self.hole_locations:
            output.append('X%.4f Y%.4f\n' % (hole[0], hole[1]))

        output.append('G80\n')
        return output


if __name__ == "__main__":
    drill = Drill()
    drill.wcs = 'G55'
    drill.tool = 6
    drill.peck = 0.1
    drill.feed = 20
    drill.speed = -700
    drill.coolant = 'M7'
    drill.z_clear = 0.1
    drill.z_start = 0.02
    drill.z_end = -0.5
    drill.z_feed = 40
    drill.bolt_hole_circle_xy(10, 5, (2.5, 2.5), 0)

    def write_to_file(file_name, data, mode="w"):
        f = open(file_name, mode)
        try:
            f.write(data)
        finally:
            f.close()

    write_to_file('/tmp/op1.nc', drill.chip_break(0.1))
    write_to_file('/tmp/op2.nc', drill.tap(1/18))
