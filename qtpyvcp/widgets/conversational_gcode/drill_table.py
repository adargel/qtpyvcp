import sys

from qtpy.QtCore import QAbstractTableModel, Qt
from qtpy.QtWidgets import QTableView, QApplication

from generators.drill import Drill


class DrillTableModel(QAbstractTableModel):
    def __init__(self, parent=None):
        super(DrillTableModel, self).__init__(parent)
        self._drill = Drill()
        self._drill.hole_locations.append((12.34, 56.78))
        self._columns = ('X', 'Y')

    def rowCount(self, parent=None, **kwargs):
        return len(self._drill.hole_locations)

    def columnCount(self, parent=None, **kwargs):
        return len(self._columns)

    def refreshModel(self):
        self.beginResetModel()
        self.endResetModel()

    def updateModel(self, value):
        self.beginResetModel()
        self._drill.hole_locations = value
        self.endResetModel()

    def data(self, index, role=Qt.DisplayRole):
        if role in (Qt.DisplayRole, Qt.EditRole):
            return self._drill.hole_locations[index.row()][index.column()]
        return super(DrillTableModel, self).data(index, role)


class DrillTable(QTableView):
    def __init__(self, parent=None):
        super(DrillTable, self).__init__(parent)

        self.setEnabled(True)

        self._drill_model = DrillTableModel()
        self.setModel(self._drill_model)

        self.setSortingEnabled(False)
        self.setAlternatingRowColors(True)
        self.setSelectionBehavior(QTableView.SelectRows)
        #self.setSelectionMode(QTableView.SingleSelection)
        self.horizontalHeader().setStretchLastSection(False)
        #self.horizontalHeader().setSortIndicator(0, Qt.AscendingOrder)


if __name__ == "__main__":
    drill_generator = Drill()
    app = QApplication(sys.argv)
    drill = DrillTable()
    drill.show()
    app.exec_()
