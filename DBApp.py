from PyQt5.QtCore    import *
from PyQt5.QtGui     import *
from PyQt5.QtWidgets import *
from PyQt5 import *
import design
from DB import DB

class DBApp(QtWidgets.QMainWindow, design.Ui_MainWindow):
    def __init__(self):
        self.db = DB()
        super().__init__()
        self.setupUi(self)
        self.addButton.clicked.connect(self.addRecord)
        self.searchButton.clicked.connect(self.search)
        self.deleteButton.clicked.connect(self.delByName)
        self.actionOpen.triggered.connect(self.showOpenDialog)
        self.actionSave.triggered.connect(self.showSaveDialog)
        self.tableWidget.itemChanged.connect(self.updateData)
        self.actionSave_as.triggered.connect(lambda: self.showSaveDialog(True))
        self.actionExport_to_CSV.triggered.connect(self.CSVExport)
        self.actionImport_from_CSV.triggered.connect(self.CSVImport)
        self.columns = ['id', 'name', 'amount', 'price']
        self.tableWidget.setColumnCount(4)
        self.tableWidget.setHorizontalHeaderLabels(self.columns)
        self.setDataToTable(self.db.getRecords())
        self.saved = True
        self.fname = False

    def checkAndSave(self, quit_msg):
        if not self.saved:
            reply = QMessageBox.question(self, 'Save?',
                                         quit_msg, QMessageBox.No, QMessageBox.Yes)
            if reply == QMessageBox.Yes:
                self.showSaveDialog()
            else:
                return True
        return self.saved

    def showOpenDialog(self):
        if self.checkAndSave("Do u wanna save changes before opening another file?"):
            fname = QFileDialog.getOpenFileName(self, 'Open file', '', 'json(*.json)')[0]
            if not fname: return
            try:
                self.db.initDBFromFile(fname)
            except Exception:
                self.errorMessage("Can't open this file")
                return
            self.setDataToTable(self.db.getRecords())
            self.saved = True
            self.fname = fname


    def CSVExport(self):
        fname = QFileDialog.getSaveFileName(self, 'Save file', '', 'csv(*.csv)')[0]
        if not fname: return
        try:
            self.db.saveDBToCSV(fname)
        except Exception:
            self.errorMessage("Can't export to this file")

    def CSVImport(self):
        if self.checkAndSave("Do u wanna save changes before importing file?"):
            fname = QFileDialog.getOpenFileName(self, 'Open file', '', 'csv(*.csv)')[0]
            if not fname: return
            try:
                self.db.importDBFromCSV(fname)
            except Exception:
                self.errorMessage("Can't import this file")
                return
            self.setDataToTable(self.db.getRecords())
            self.fname = False

    def showSaveDialog(self, saveas = False):
        if not self.fname or saveas:
            fname = QFileDialog.getSaveFileName(self, 'Save file', '', 'json(*.json)')[0]
            if not fname: return
        else:
            fname = self.fname
        try:
            self.db.saveDBToFile(fname)
        except Exception:
            self.errorMessage("Can't save to this file")
            return
        self.saved = True

    def updateData(self, item):
        if not self.settingdata:
            try:
                newdata = self.tabledata[item.row()].copy()
                id = newdata['id']
                newdata[self.columns[item.column()]] = item.text()
                rewritedata = newdata.copy()
                self.db.editRecord(id, newdata)
            except None as error:
                self.errorMessage(str(error))
                self.setDataToTable(self.tabledata)
                return
            self.tabledata[item.row()] = rewritedata
            self.saved = False

    def setDataToTable(self, data):
        self.tabledata = data
        self.settingdata = True
        self.tableWidget.setRowCount(len(data))
        for rownum, row in enumerate(data):
            for colnum, col in enumerate(self.columns):
                self.tableWidget.setItem(rownum, colnum, QTableWidgetItem(str(row[col])))
        self.settingdata = False


    def errorMessage(self, error):
        dialog = QMessageBox()
        dialog.setIcon(QMessageBox.Critical)
        dialog.setText(error)
        dialog.addButton(QMessageBox.Ok)
        dialog.exec()

    def addRecord(self):
        id = self.id.text()
        price = self.price.text()
        amount = self.amount.text()
        name = self.name.text()
        if id.isnumeric() and price and amount and name:
            try:
                self.db.addRecord({"id": int(id), "name": name, "amount": amount, "price": price})
            except Exception as error:
                self.errorMessage(str(error))
        self.settingdata = True
        self.setDataToTable(self.db.getRecords())
        self.settingdata = False
        self.saved = False

    def search(self):
        text = self.nameSD.text()
        if not text:
            self.setDataToTable(self.db.getRecords())
            return
        try:
            self.setDataToTable(self.db.getRecordsByName(text))
        except Exception as error:
            self.errorMessage(str(error))

    def delByName(self):
        name = self.nameSD.text()
        try:
            self.db.delRecordsByName(name)
        except Exception as error:
            self.errorMessage(str(error))
        self.setDataToTable(self.db.getRecords())
        self.saved = False

    def closeEvent(self, event):
        if self.checkAndSave("Do u wanna save changes before exiting?"):
            event.accept()
        else:
            event.ignore()
