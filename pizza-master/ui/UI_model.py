# coding=utf-8

from PySide2.QtGui import QPixmap
from PySide2.QtCore import Qt, QAbstractTableModel, QModelIndex


class CustomTableModel(QAbstractTableModel):
    """
    task 선택하는 TableView의 모델
    """
    def __init__(self, table_data=None):
        QAbstractTableModel.__init__(self)
        if table_data is None:
            table_data = []
        self.asset_name = None
        self.row_count = None
        self.input_data = None
        self.column_count = None
        self.header_data = None
        self.load_data(table_data)

    def load_data(self, data):
        self.input_data = data
        self.row_count = len(data)

    def rowCount(self, parent=QModelIndex()):
        return self.row_count

    def columnCount(self, parent=QModelIndex()):
        return self.column_count

    def headerData(self, section, orientation, role):
        if role != Qt.DisplayRole:
            return None
        if orientation == Qt.Horizontal:
            if self.column_count == 3:
                return (self.header_data[0], self.header_data[1], self.header_data[2])[section]
            elif self.column_count == 2:
                return (self.header_data[0], self.header_data[1])[section]
        else:
            return str(section)

    def data(self, index, role=Qt.DisplayRole):
        row = index.row()

        if type(self.input_data[row][0]) == str:
            # 첫번째 인자가 png일 경우
            column = index.column()
            if role == Qt.DisplayRole:
                return str(self.input_data[row][column])

            elif role == Qt.DecorationRole:
                if column == 0:
                    pixmap = QPixmap()
                    pixmap.loadFromData(self.input_data[row][0])
                    pixmap_width = 100
                    scaled_width = min(pixmap.width(), pixmap_width)
                    pixmap_image = pixmap.scaledToWidth(scaled_width)
                    return pixmap_image

            elif role == Qt.TextAlignmentRole:
                return Qt.AlignCenter

            return None
        else:
            if role == Qt.DisplayRole:
                for column in range(len(self.input_data[row])):
                    if column == index.column():
                        return str(self.input_data[row][column])
                return None

            elif role == Qt.TextAlignmentRole:
                return Qt.AlignCenter

            return None

    def setData(self, index, value, role):
        if role == Qt.EditRole:
            self.input_data = value
            self.dataChanged.emit(index, index)
            return True

        return False

    def flags(self, index):
        if self.input_data[index.row()][0] is None:
            return Qt.ItemFlags(Qt.ItemIsEnabled)
        if self.asset_name and self.input_data[index.row()][1] == self.asset_name:
            return Qt.ItemFlags(Qt.ItemIsEnabled)
        return Qt.ItemFlags(Qt.ItemIsEnabled | Qt.ItemIsSelectable)
