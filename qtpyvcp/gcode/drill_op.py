from base_drill_op import BaseDrillOp


class GCodeOp:
    def __init__(self, name, gcode):
        self._name = name
        self._gcode = gcode

    def name(self):
        return self._name

    def gcode(self):
        return self._gcode


class Drilling(BaseDrillOp):
    def __init__(self):
        super(Drilling, self).__init__()
        self.holes = []

    def drill(self):
        gcode = self._create_gcode('G98 G81 R%.3f Z%.3f F%.3f' %
                                   (self.z_start + self.retract, self.z_end, self.z_feed))
        return GCodeOp('Drilling Operation', gcode)

    def dwell(self, dwell_time=0.):
        gcode = self._create_gcode('G98 G82 R%.3f Z%.3f P%.3f F%.3f' %
                                   (self.z_start + self.retract, self.z_end, dwell_time, self.z_feed))
        return GCodeOp('Dwell Drilling Operation', gcode)

    def peck(self, peck_dist=0.1):
        gcode = self._create_gcode('G98 G83 R%.3f Z%.3f Q%.3f F%.3f' %
                                   (self.z_start + self.retract, self.z_end, peck_dist, self.z_feed))
        return GCodeOp('Peck Drilling Operation', gcode)

    def chip_break(self, break_dist=0.1):
        gcode = self._create_gcode('G98 G73 R%.3f Z%.3f Q%.3f F%.3f' %
                                  (self.z_start + self.retract, self.z_end, break_dist, self.z_feed))
        return GCodeOp('Chip Break Drilling Operation', gcode)

    def tap(self, pitch):
        feed = abs(self.spindle_rpm * pitch)
        gcode = self._create_gcode('G98 %s R%.3f Z%.3f F%.3f S%.3f' %
                                  ('G74' if self.spindle_dir.lower() == 'ccw' else 'G84', self.z_start + self.retract,
                                   self.z_end, feed, abs(self.spindle_rpm)))

        return GCodeOp('%s Tap Operation (pitch=%.3f)' %
                       ('Left Hand' if self.spindle_dir.lower() == 'ccw' else 'Right Hand', pitch), gcode)
