import sqlite3

con = sqlite3.connect('db.db')
cursorObj = con.cursor()

cursorObj.execute('SELECT * FROM unit')
all_units = cursorObj.fetchall()
print(all_units)

cursorObj.execute('SELECT * FROM stream')
all_streams = cursorObj.fetchall()
print(all_streams)

cursorObj.execute('SELECT * FROM unit_material ')
all_unit_materials = cursorObj.fetchall()
print(all_unit_materials)

cursorObj.execute('SELECT * FROM load_max  ')
all_load_max = cursorObj.fetchall()
print(all_load_max)


class Unit:
    def __init__(self, name: str, unit_id):
        self.name = name
        self.unit_id = unit_id
        self.__load_max = None
        self.input_stream = {}
        self.output_stream = {}

    def set_load_max(self, load_max):
        self.__load_max = load_max

    def add_input_stream(self, stream):
        self.input_stream[stream.name] = stream

    def add_output_stream(self, stream):
        self.output_stream[stream.name] = stream


class ABTUnit(Unit):
    pass


class SecondaryUnit(Unit):
    pass


class Stream:
    def __init__(self, name: str, stream_id: int):
        self.name = name
        self.id = stream_id
        self.where_from = []
        self.where_to = []

    def add_where_from(self, unit: Unit):
        self.where_from.append(unit.unit_id)

    def add_where_to(self, unit: Unit):
        self.where_to.append(unit.unit_id)
