class BaseOp(object):
    def __init__(self):
        self.z_start = 0.
        self.z_end = 0.
        self.retract = 0.
        self.z_feed = 0.
        self.z_clear = 0.
        self.tool_number = 0
        self.spindle_rpm = 0.
        self.spindle_dir = 'cw'
        self.wcs = ''
        self.coolant = ''

    def start_op(self):
        gcode = [
            'T%i M6 G43' % self.tool_number,
            'S%.3f' % self.spindle_rpm,
            'M4' if self.spindle_dir.lower() == 'ccw' else 'M3',
            self.wcs.upper(),
        ]
        if self.coolant.lower() == 'mist':
            gcode.append('M7')
        elif self.coolant.lower() == 'flood':
            gcode.append('M8')

        return gcode

    def end_op(self):
        gcode = []
        if self.coolant.strip() != '':
            gcode.append('M9')
        gcode.append('G0 Z%.3f' % self.z_clear)
        return gcode
