import os

from qtpy import uic
from qtpy.QtCore import Slot
from qtpy.QtWidgets import QWidget, QComboBox, QFrame

from qtpyvcp.plugins import getPlugin
from qtpyvcp.utilities.logger import getLogger
from qtpyvcp.actions.program_actions import load as loadProgram

from generators.gcode import GCode, Drill

LOG = getLogger(__name__)
TOOLTABLE = getPlugin('tooltable')
STATUS = getPlugin('status')


def to_float(value):
    try:
        value = float(value)
        return value
    except ValueError:
        LOG.exception("%s is not a valid number.", value)

        return None


class WCSComboBox(QComboBox):
    def __init__(self, parent=None):
        super(WCSComboBox, self).__init__(parent)

    @property
    def wcs(self):
        if self.currentText().lower() == "current":
            return self.items[STATUS.g5x_index() + 1]

        return self.currentText()

class DrillCircle(QWidget):
    def __init__(self, parent=None):
        super(DrillCircle, self).__init__(parent)
        uic.loadUi(os.path.join(os.path.dirname(__file__), 'drill_circle.ui'), self)

        self.gcode = GCode()
        self.drill = Drill(self.gcode)

        self.bolt_hole_wcs.addItem("G54")
        self.bolt_hole_wcs.addItem("G55")
        self.bolt_hole_wcs.addItem("G56")
        self.bolt_hole_wcs.addItem("G57")
        self.bolt_hole_wcs.addItem("G58")
        self.bolt_hole_wcs.addItem("G59")
        self.bolt_hole_wcs.addItem("G59.1")
        self.bolt_hole_wcs.addItem("G59.2")
        self.bolt_hole_wcs.addItem("G59.3")

        self.bolt_hole_drill_type.addItem("DRILL")
        self.bolt_hole_drill_type.addItem("SPOT")
        self.bolt_hole_drill_type.addItem("BREAK")
        self.bolt_hole_drill_type.addItem("DWELL")
        self.bolt_hole_drill_type.addItem("PECK")
        self.bolt_hole_drill_type.addItem("TAP")
        self.bolt_hole_drill_type.addItem("RIGID TAP")

        self.drill_type_param_value.setVisible(False)
        self.drill_type_param_label.setVisible(False)

        self.bolt_hole_spindle_direction.addItem("CW")
        self.bolt_hole_spindle_direction.addItem("CCW")

        self.coolant_combo_box.addItem("OFF")
        self.coolant_combo_box.addItem("MIST")
        self.coolant_combo_box.addItem("FLOOD")

        self._tool_table = TOOLTABLE.getToolTable()
        self.tool_diameter = 0.
        self.tool = None

    @Slot(int)
    def on_bolt_hole_drill_type_currentIndexChanged(self, i):
        if self.bolt_hole_drill_type.currentText() == 'DWELL':
            self.drill_type_param_label.setText("DWELL TIME (SEC.)")
            self.drill_type_param_value.setText("0.00")
            self.drill_type_param_value.setVisible(True)
            self.drill_type_param_label.setVisible(True)
        elif self.bolt_hole_drill_type.currentText() == 'PECK':
            self.drill_type_param_label.setText("PECK DEPTH")
            self.drill_type_param_value.setText("0.0000")
            self.drill_type_param_value.setVisible(True)
            self.drill_type_param_label.setVisible(True)
        elif self.bolt_hole_drill_type.currentText() == 'BREAK':
            self.drill_type_param_label.setText("BREAK DEPTH")
            self.drill_type_param_value.setText("0.0000")
            self.drill_type_param_value.setVisible(True)
            self.drill_type_param_label.setVisible(True)
        elif self.bolt_hole_drill_type.currentText() in ['TAP', 'RIGID TAP']:
            self.bolt_hole_z_feed_rate.setEnabled(False)
            self.drill_type_param_label.setText("PITCH")
            self.drill_type_param_value.setText("0.00")
            self.drill_type_param_value.setVisible(True)
            self.drill_type_param_label.setVisible(True)
        else:
            self.drill_type_param_value.setVisible(False)
            self.drill_type_param_label.setVisible(False)

    @Slot()
    def on_bolt_hole_tool_number_editingFinished(self):
        try:
            index = int(self.bolt_hole_tool_number.text())
        except Exception:
            LOG.exception("Tool number %s is not a valid number" % self.bolt_hole_tool_number.text())
            self.tool_desc_label.setText("INVALID TOOL SELECTED")
            self.tool = None
            return

        try:
            tool = self._tool_table[index]
            self.tool = tool
        except KeyError:
            LOG.exception("Tool number %i is not a valid tool in the tool table." % index)
            self.tool_desc_label.setText("INVALID TOOL SELECTED")
            self.tool = None
            return

        if not self.tool["T"] == 0:
            desc = self.tool["R"]
            self.tool_desc_label.setToolTip(desc)
            self.tool_desc_label.setText((desc[:40] + '...') if len(desc) > 40 else desc)
        else:
            self.tool_desc_label.setText("NO TOOL SELECTED")

    @Slot()
    def on_bolt_hole_post_file_clicked(self):
        self.on_bolt_hole_add_to_file_clicked()
        print self.gcode.to_string()
        self.gcode.write_to_file('/tmp/testing.ngc')
        loadProgram('/tmp/testing.ngc')
        self.gcode = GCode()
        self.drill = Drill(self.gcode)

    @Slot()
    def on_bolt_hole_add_to_file_clicked(self):
        self.setup_wcs()
        self.setup_spindle()
        self.setup_coolant()
        self.setup_tool_change()
        self.setup_feed()
        self.drill.zstart = to_float(self.bolt_hole_start.text())
        self.drill.zend = to_float(self.bolt_hole_end.text())
        self.drill.zclear = to_float(self.bolt_hole_clearance_height.text())
        self.drill.retract = to_float(self.bolt_hole_retract.text())
        self.drill.zfeed = to_float(self.bolt_hole_z_feed_rate.text())

        self.drill.bolt_hole_circle(num_holes=int(self.bolt_hole_num_holes.text()),
                                    circle_diam=to_float(self.bolt_hole_diameter.text()),
                                    circle_center=(to_float(self.bolt_hole_center_x.text()),
                                                   to_float(self.bolt_hole_center_y.text())),
                                    start_angle=to_float(self.bolt_hole_start_angle.text()))

        if self.bolt_hole_drill_type.currentText() == "DRILL":
            self.drill.drill()

        #elif type == "SPOT":
            #d.dwell(z_end=float(self.bolt_hole_end.text()), r=float(self.bolt_hole_retract.text()))

    def setup_wcs(self):
        self.gcode.set_wcs(self.bolt_hole_wcs.currentText().upper())

    def setup_spindle(self):
        try:
            value = float(self.bolt_hole_spindle_rpm.text())
            if self.bolt_hole_spindle_direction.currentText().lower() == 'ccw':
                value = -value
            self.gcode.spindle_on(value)
        except ValueError:
            LOG.exception("Could not set spindle RPM. Invalid value %s.", self.bolt_hole_spindle_rpm.text())

    def setup_coolant(self):
        if self.coolant_combo_box.currentText().lower() == 'mist':
            self.gcode.coolant_mist_on()
        elif self.coolant_combo_box.currentText().lower() == 'flood':
            self.gcode.coolant_flood_on()
        else:
            self.gcode.coolant_off()

    def setup_tool_change(self):
        if self.tool:
            self.gcode.tool_change(self.tool["T"])

    def setup_feed(self):
        value = to_float(self.bolt_hole_xy_feed_rate.text())
        if value:
            self.gcode.set_feed(value)

