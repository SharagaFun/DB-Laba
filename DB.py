import json
import csv

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
            raise Exception('Record doesnt exist')

    def getRecordsByName(self, name):
        res = list()
        if not name in self.names:
            raise Exception('Record doesnt exist')
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
            if num >= 10 and first:
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
            raise Exception('Record doesnt exist')
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
            raise Exception('Record doesnt exist')
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

    def flushDB(self):
        self.tables = dict()
        self.names = dict()

    def importDBFromCSV(self, filename):
        self.flushDB()
        with open(filename, newline='') as csvfile:
            reader = csv.DictReader(csvfile)
            for row in reader:
                self.addRecord(row)

    def initDBFromFile(self, filename):
        with open(filename) as json_file:
            file = json.load(json_file, object_hook=lambda d: {int(k) if k.isdigit() else k: v for k, v in d.items()})
        self.tables = file[0]
        self.names = file[1]
