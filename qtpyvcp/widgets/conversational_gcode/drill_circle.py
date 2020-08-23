import os

from qtpy import uic
from qtpy.QtCore import Slot
from qtpy.QtWidgets import QWidget

from qtpyvcp.plugins import getPlugin
from qtpyvcp.utilities.logger import getLogger
from qtpyvcp.actions.program_actions import load as loadProgram


LOG = getLogger(__name__)
TOOLTABLE = getPlugin('tooltable')


class DrillCircle(QWidget):
    def __init__(self, parent=None):
        super(DrillCircle, self).__init__(parent)
        uic.loadUi(os.path.join(os.path.dirname(__file__), 'drill_circle.ui'), self)

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
        self.bolt_hole_drill_type.addItem("PECK")
        self.bolt_hole_drill_type.addItem("DWELL")
        self.bolt_hole_drill_type.addItem("BREAK")

        self.drill_type_param_value.setVisible(False)
        self.drill_type_param_label.setVisible(False)

        self.bolt_hole_spindle_direction.addItem("CW")
        self.bolt_hole_spindle_direction.addItem("CCW")

        self._tool_table = TOOLTABLE.getToolTable()
        self.tool_diameter = 0.
        self.spotting_tool_diameter = 0.

    @Slot()
    def on_bolt_hole_post_file_clicked(self):
        print('post file clicked')

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
        else:
            self.drill_type_param_value.setVisible(False)
            self.drill_type_param_label.setVisible(False)

    @Slot()
    def on_bolt_hole_tool_number_editingFinished(self):
        tool = self._get_tool(self.bolt_hole_tool_number.text())
        self.tool_number_label.setToolTip(tool["R"])
        self.bolt_hole_tool_number.setToolTip(tool["R"])
        self.tool_diameter = tool["D"]

    @Slot()
    def on_spotting_tool_value_editingFinished(self):
        tool = self._get_tool(self.spotting_tool_value.text())
        self.spotting_tool_label.setToolTip(tool["R"])
        self.spotting_tool_value.setToolTip(tool["R"])
        self.spotting_tool_diameter = tool["D"]

    def _get_tool(self, index):
        try:
            index = int(index)
        except Exception:
            LOG.exception("Tool number %s is not a valid number" % index)
            return

        try:
            tool = self._tool_table[index]
        except KeyError:
            LOG.exception("Tool number %i is not a valid tool in the tool table." % index)
            return

        return tool
