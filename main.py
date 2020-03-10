import json
import sys
import csv
from PyQt5.QtCore    import *
from PyQt5.QtGui     import *
from PyQt5.QtWidgets import *
from PyQt5 import *
import design


class DB:
    tables = dict()
    names = dict()

    def __init__(self):
        pass

    def addRecord(self, record):
        id = record['id']
        del record['id']
        if id in self.tables:
            raise Exception('Duplicate record')
            return
        self.tables[id] = record
        if record['name'] in self.names:
            self.names[record['name']].append(id)
        else:
            self.names[record['name']] = [id]

    def getRecordById(self, id):
        try:
            return self.tables[id]
        except KeyError:
            raise Exception('Record doesn’t exist')

    def getRecordsByName(self, name):
        res = list()
        if not name in self.names:
            raise Exception('Record doesn’t exist')
        for id in self.names[name]:
            record = self.getRecordById(id)
            record.update({'id': id})
            res.append(record)
        return res

    def getRecords(self, first=True):
        res = list()
        for num, id in enumerate(self.tables):
            record = self.tables[id]
            record.update({'id': id})
            res.append(record)
            if num > 10 and first:
                break
        return res

    def editRecord(self, oldid, record):
        record['id'] = int(record['id'])
        oldid = int(oldid)
        if record['id'] != oldid and record['id'] in self.tables:
            raise Exception('Duplicate record')
            return
        id = record['id']
        del record['id']
        if oldid not in self.tables:
            raise Exception('Record doesn’t exist')
            return
        del self.tables[oldid]
        self.tables[id] = record
        if record['name'] in self.names:
            if oldid in self.names[record['name']]:
                self.names[record['name']].remove(oldid)
            self.names[record['name']].append(id)
        else:
            self.names[record['name']] = [id]

    def delRecordById(self, id):
        self.names[self.tables[id]['name']].remove(id)
        del self.tables[id]

    def delRecordsByName(self, name):
        if not name in self.names:
            raise Exception('Record doesn’t exist')
        records = self.names[name][:]
        for id in records:
            self.delRecordById(id)

    def saveDBToFile(self, filename):
        file = list()
        file.append(self.tables)
        file.append(self.names)
        with open(filename, 'w') as outfile:
            json.dump(file, outfile)

    def saveDBToCSV(self, filename):
        records=self.getRecords(False)
        columns = ['id', 'name', 'amount', 'price']
        with open(filename, 'w') as csvfile:
            writer = csv.DictWriter(csvfile, fieldnames=columns)
            writer.writeheader()
            for data in records:
                writer.writerow(data)

    def initDBFromFile(self, filename):
        with open(filename) as json_file:
            file = json.load(json_file, object_hook=lambda d: {int(k) if k.isdigit() else k: v for k, v in d.items()})
        self.tables = file[0]
        self.names = file[1]


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
        self.saved = False


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
def main():
    app = QtWidgets.QApplication(sys.argv)
    window = DBApp()
    window.show()
    app.exec_()


if __name__ == '__main__':
    main()
