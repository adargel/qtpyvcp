import os
from qtpy.QtGui import QIntValidator, QDoubleValidator

from qtpy import uic
from qtpy.QtCore import Slot
from qtpy.QtGui import QIntValidator, QValidator
from qtpy.QtWidgets import QWidget, QComboBox, QLineEdit

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
        self.addItem("G54")
        self.addItem("G55")
        self.addItem("G56")
        self.addItem("G57")
        self.addItem("G58")
        self.addItem("G59")
        self.addItem("G59.1")
        self.addItem("G59.2")
        self.addItem("G59.3")

    def get_wcs(self):
        return self.currentText()


class DrillTypeComboBox(QComboBox):
    def __init__(self, parent=None):
        super(DrillTypeComboBox, self).__init__(parent)

        self.addItem("DRILL")
        self.addItem("SPOT")
        self.addItem("BREAK")
        self.addItem("DWELL")
        self.addItem("PECK")
        self.addItem("TAP")
        self.addItem("RIGID TAP")

    def get_drill_type(self):
        return self.currentText()


class SpindleDirectionComboBox(QComboBox):
    def __init__(self, parent=None):
        super(SpindleDirectionComboBox, self).__init__(parent)

        self.addItem("CW")
        self.addItem("CCW")

    def get_spindle_direction(self):
        return self.currentText()


class CoolantComboBox(QComboBox):
    def __init__(self, parent=None):
        super(CoolantComboBox, self).__init__(parent)

        self.addItem("OFF")
        self.addItem("MIST")
        self.addItem("FLOOD")


class ToolNumberLineEdit(QLineEdit):
    def __init__(self, parent=None):
        super(ToolNumberLineEdit, self).__init__(parent)
        self.setValidator(QIntValidator())


class DrillCircle(QWidget):
    def __init__(self, parent=None):
        super(DrillCircle, self).__init__(parent)
        uic.loadUi(os.path.join(os.path.dirname(__file__), 'drill_circle.ui'), self)

        self.gcode = GCode()
        self.drill = Drill(self.gcode)
        self.tool_number.setValidator(QIntValidator())
        self.num_holes.setValidator(QIntValidator())
        self.spindle_rpm.setValidator(QDoubleValidator())
        self.xy_feed_rate.setValidator(QDoubleValidator())
        self.z_feed_rate.setValidator(QDoubleValidator())
        self.clearance_height.setValidator(QDoubleValidator())
        self.retract.setValidator(QDoubleValidator())
        self.center_x.setValidator(QDoubleValidator())
        self.center_y.setValidator(QDoubleValidator())
        self.start_angle.setValidator(QDoubleValidator())
        self.diameter.setValidator(QDoubleValidator())
        self.hole_start.setValidator(QDoubleValidator())
        self.hole_end.setValidator(QDoubleValidator())

        self.drill_type_param_value.setVisible(False)
        self.drill_type_param_label.setVisible(False)

        self._tool_table = TOOLTABLE.getToolTable()
        self._tool = None

    @Slot(int)
    def on_drill_type_currentIndexChanged(self, i):
        if self.drill_type.currentText() == 'DWELL':
            self.drill_type_param_label.setText("DWELL TIME (SEC.)")
            self.drill_type_param_value.setText("0.00")
            self.drill_type_param_value.setVisible(True)
            self.drill_type_param_label.setVisible(True)
        elif self.drill_type.currentText() == 'PECK':
            self.drill_type_param_label.setText("PECK DEPTH")
            self.drill_type_param_value.setText("0.0000")
            self.drill_type_param_value.setVisible(True)
            self.drill_type_param_label.setVisible(True)
        elif self.drill_type.currentText() == 'BREAK':
            self.drill_type_param_label.setText("BREAK DEPTH")
            self.drill_type_param_value.setText("0.0000")
            self.drill_type_param_value.setVisible(True)
            self.drill_type_param_label.setVisible(True)
        elif self.drill_type.currentText() in ['TAP', 'RIGID TAP']:
            self.z_feed_rate.setEnabled(False)
            self.drill_type_param_label.setText("PITCH")
            self.drill_type_param_value.setText("0.00")
            self.drill_type_param_value.setVisible(True)
            self.drill_type_param_label.setVisible(True)
        else:
            self.drill_type_param_value.setVisible(False)
            self.drill_type_param_label.setVisible(False)

    @Slot()
    def on_tool_number_editingFinished(self):
        try:
            index = int(self.tool_number.text())
        except Exception:
            LOG.exception("Tool number %s is not a valid number" % self.tool_number.text())
            self.tool_desc_label.setText("INVALID TOOL SELECTED")
            self._tool = None
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
    def on_post_file_clicked(self):
        self.on_add_to_file_clicked()
        print self.gcode.to_string()
        self.gcode.write_to_file('/tmp/testing.ngc')
        loadProgram('/tmp/testing.ngc')
        self.gcode = GCode()
        self.drill = Drill(self.gcode)

    @Slot()
    def on_add_to_file_clicked(self):
        self.setup_wcs()
        self.setup_spindle()
        self.setup_coolant()
        self.setup_tool_change()
        self.setup_feed()
        self.drill.zstart = to_float(self.start.text())
        self.drill.zend = to_float(self.end.text())
        self.drill.zclear = to_float(self.clearance_height.text())
        self.drill.retract = to_float(self.retract.text())
        self.drill.zfeed = to_float(self.z_feed_rate.text())

        self.drill.circle(num_holes=int(self.num_holes.text()),
                                    circle_diam=to_float(self.diameter.text()),
                                    circle_center=(to_float(self.center_x.text()),
                                                   to_float(self.center_y.text())),
                                    start_angle=to_float(self.start_angle.text()))

        if self.drill_type.currentText() == "DRILL":
            self.drill.drill()

        #elif type == "SPOT":
            #d.dwell(z_end=float(self.end.text()), r=float(self.retract.text()))

    def setup_wcs(self):
        self.gcode.set_wcs(self.wcs.currentText().upper())

    def setup_spindle(self):
        try:
            value = float(self.spindle_rpm.text())
            if self.spindle_direction.currentText().lower() == 'ccw':
                value = -value
            self.gcode.spindle_on(value)
        except ValueError:
            LOG.exception("Could not set spindle RPM. Invalid value %s.", self.spindle_rpm.text())

    def setup_coolant(self):
        if self.coolant_setting.currentText().lower() == 'mist':
            self.gcode.coolant_mist_on()
        elif self.coolant_setting.currentText().lower() == 'flood':
            self.gcode.coolant_flood_on()
        else:
            self.gcode.coolant_off()

    def setup_tool_change(self):
        if self._tool:
            self.gcode.tool_change(self.tool["T"])

    def setup_feed(self):
        value = to_float(self.xy_feed_rate.text())
        if value:
            self.gcode.set_feed(value)

