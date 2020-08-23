from drill_circle import DrillCircle
from qtpyvcp.widgets.qtdesigner import _DesignerPlugin

class DrillCirclePlugin(_DesignerPlugin):
    def pluginClass(self):
        return DrillCircle
