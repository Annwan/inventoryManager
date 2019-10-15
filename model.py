import sqlite3

class InventoryModel(object):
    def __init__(self):
        # Create a database in RAM
        self._db = sqlite3.connect('inventory.db')
        self._db.row_factory = sqlite3.Row
        # Create the basic part table.
        try:
            self._db.cursor().execute('''
                CREATE TABLE parts(
                    id INTEGER PRIMARY KEY,
                    name TEXT,
                    mcat TEXT,
                    scat1 TEXT,
                    scat2 TEXT,
                    amnt INT,
                    pos TEXT,
                    desc TEXT)
            ''')
            self._db.commit()
        except:
            pass
        self.current_id = None
        self.current_pos = None

    def add(self, part):
        self._db.cursor().execute('''
            INSERT INTO parts( name,  mcat,  scat1,  scat2,  amnt,  pos,  desc)
                       VALUES(:name, :mcat, :scat1, :scat2, :amnt, :pos, :desc)''', part)
        self._db.commit()

    def get_summary(self):
        return self._db.cursor().execute(
            "SELECT name, id FROM parts").fetchall()

    def get_part(self, part_id):
        return self._db.cursor().execute(
            "SELECT * FROM parts WHERE id=:id", {"id": part_id}).fetchone()

    def get_current_part(self):
        if self.current_id is None:
            return {
                "name": "",
                "mcat": "",
                "scat1": "",
                "scat2": "",
                "amnt": 0,
                "pos": "",
                "desc": ""
            }
        else:
            return self.get_part(self.current_id)

    def update_current_part(self, details):
        if self.current_id is None:
            self.add(details)
        else:
            self._db.cursor().execute('''
                UPDATE parts SET name=:name, mcat=:mcat, scat1=:scat1,
                scat2=:scat2, pos=:pos, amnt=:amnt, desc=:desc WHERE id=:id''', details)
            self._db.commit()

    def delete_part(self, part_id):
        self._db.cursor().execute('''
            DELETE FROM parts WHERE id=:id''', {"id": part_id})
        self._db.commit() 

    def count_empty(self, rack):
        count = 0
        for i in self._db.cursor().execute('SELECT amnt, pos FROM parts').fetchall():
            if i[0] == 0 and i[1][0] == rack:
                count+=1
        return count

    def list_empty(self, rack):
        lst = []
        for i in self._db.cursor().execute('SELECT amnt, pos, name FROM parts').fetchall():
            if i[0] == 0 and i[1][0] == rack:
                lst.append(i[2])
        return lst
