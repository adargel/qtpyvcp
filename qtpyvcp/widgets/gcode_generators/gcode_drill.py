import math


def write_to_file(path, output, mode="w"):
    file_out = open(path, mode)
    try:
        file_out.write(output)
    finally:
        file_out.close()


def append_to_file(path, output):
    write_to_file(path, output, "a")


class GCodeGenerator(object):
    def __init__(self):
        self.title_ = ''
        self.wcs_ = ''
        self.speed_ = 0
        self.feed_ = 0
        self.z_clear_ = 0.1
        self.tool_ = 0
        self.coolant_ = ''
        self.preamble_ = ''
        self.epilog_ = ''

    @property
    def title(self):
        return self.title_

    @title.setter
    def title(self, value):
        self.title_ = value

    @property
    def wcs(self):
        return self.wcs_

    @wcs.setter
    def wcs(self, value):
        self.wcs_ = value

    @property
    def speed(self):
        return self.speed_

    @speed.setter
    def speed(self, value):
        self.speed_ = value

    @property
    def feed(self):
        return self.feed_

    @feed.setter
    def feed(self, value):
        self.feed_ = value

    @property
    def z_clear(self):
        return self.z_clear_

    @z_clear.setter
    def z_clear(self, value):
        self.z_clear_ = value

    @property
    def tool(self):
        return self.tool_

    @tool.setter
    def tool(self, value):
        self.tool_ = value

    @property
    def coolant(self):
        return self.coolant_

    @coolant.setter
    def coolant(self, value):
        self.coolant_ = value

    @property
    def preamble(self):
        self.preamble_ = []
        self.preamble_.append('G90 G94 G17 G91.1\n')
        self.preamble_.append('G20\n')
        self.preamble_.append('G53 G0 Z0\n')
        self.preamble_.append('T%i M6 G43\n' % self.tool)
        self.preamble_.append('S%i M3\n' % self.speed)
        self.preamble_.append('%s\n' % self.wcs)
        return self.preamble_

    @property
    def epilog(self):
        output = ["G53 G0 Z0\n", "M30"]
        return ''.join(output)

    def write_to_file(self, path, mode="w"):
        file_out = open(path, mode)
        try:
            file_out.write(self.gcode_())
        finally:
            file_out.close()


class GCodeDrillCycle(GCodeGenerator):
    def __init__(self):
        super(GCodeDrillCycle, self).__init__()
        self.canned_cycle_ = 'G81'
        self.holes_xy_ = []
        self.z_start_ = 0
        self.z_end_ = self.z_start_

    @property
    def z_start(self):
        return self.z_start_

    @z_start.setter
    def z_start(self, value):
        self.z_start_ = value

    @property
    def z_end(self):
        return self.z_end_

    @z_end.setter
    def z_end(self, value):
        self.z_end_ = value

    @property
    def holes_xy(self):
        return self.holes_xy_

    @holes_xy.setter
    def holes_xy(self, value):
        self.holes_xy_ = value

    @property
    def canned_cycle(self):
        return self.canned_cycle_

    @canned_cycle.setter
    def canned_cycle(self, value):
        self.canned_cycle_ = value

    def gcode_(self):
        output = []
        output.extend(self.preamble)

        output.append("F%.4f\n" % self.feed)
        output.append("G0 Z%.4f\n" % self.z_clear_)
        output.append("G98 G81 R%.4f Z%.4f" % (self.z_start_,  self.z_end_ - self.z_start_))
        for hole in self.holes_xy_:
            output.append("X%.4f Y%.4f\n" % (hole[0], hole[1]))

        output.append("G80\n")
        output.append(self.epilog)

        return ''.join(output)


class GCodeBoltHoleCircle(GCodeDrillCycle):
    def __init__(self):
        super(GCodeBoltHoleCircle, self).__init__()
        self.bolt_hole_center_ = (0, 0)
        self.bolt_hole_diameter_ = 0
        self.num_holes_ = 0
        self.start_angle_ = 0

    @property
    def num_holes(self):
        return self.num_holes_

    @num_holes.setter
    def num_holes(self, value):
        self.num_holes_ = value

    @property
    def bolt_hole_diameter(self):
        return self.bolt_hole_diameter_

    @bolt_hole_diameter.setter
    def bolt_hole_diameter(self, value):
        self.bolt_hole_diameter_ = value

    @property
    def bolt_hole_center(self):
        return self.bolt_hole_center_

    @bolt_hole_center.setter
    def bolt_hole_center(self, value):
        self.bolt_hole_center_ = value

    @property
    def start_angle(self):
        return self.start_angle_

    @start_angle.setter
    def start_angle(self, value):
        self.start_angle_ = value

    def gcode_(self):
        curr_angle = self.start_angle_
        angle_step = (360/self.num_holes_)

        holes = []
        for _ in range(0, self.num_holes_):
            x = math.cos(math.radians(curr_angle)) * (self.bolt_hole_diameter_/2)
            y = math.sin(math.radians(curr_angle)) * (self.bolt_hole_diameter_/2)
            x += self.bolt_hole_center_[0]
            y += self.bolt_hole_center_[1]

            holes.append((x, y))
            curr_angle += angle_step

        self.holes_xy = holes
        return super(GCodeBoltHoleCircle, self).gcode_()


if __name__ == "__main__":
    cycle = GCodeBoltHoleCircle()
    cycle.wcs = 'G55'
    cycle.tool = 6
    cycle.feed = 40
    cycle.set_speed = 1200
    cycle.z_clear_ = 1
    cycle.z_start = 0.02
    cycle.z_end = -0.5
    cycle.num_holes = 5
    cycle.start_angle = 0
    cycle.bolt_hole_diameter = 2
    cycle.bolt_hole_center = (2.5, 2.5)

    cycle.write_to_file('/tmp/output.nc')
