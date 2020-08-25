from qtpyvcp.gcode.base_op import BaseOp


class BaseDrillOp(BaseOp):
    def __init__(self):
        super(BaseDrillOp, self).__init__()
        self.holes = []

    def _create_gcode(self, op):
        gcode = self.start_op()
        if len(self.holes) > 0:
            gcode.append('G0 X%.3f Y%.3f' % (self.holes[0][0], self.holes[0][1]))
            gcode.append(op)
            for h in self.holes[1:]:
                gcode.append('X%.3f Y%.3f' % (h[0], h[1]))

        gcode.append('G80')
        gcode.extend(self.end_op())

        return gcode

