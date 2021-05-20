import sqlite3
import json
import openpyxl as opx


class Unit:
    def __init__(self, name: str, unit_id):
        self.name = name
        self.unit_id = unit_id
        self.__load_max = None
        self.input_stream = {}
        self.output_stream = {}

    def set_load_max(self, load_max_value):
        self.__load_max = load_max_value

    @property
    def load_max(self):
        return self.__load_max

    def __repr__(self):
        return f"Unit_{self.name}"


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
        self.where_from.append(unit)

    def add_where_to(self, unit: Unit):
        self.where_to.append(unit)

    def __repr__(self):
        return f"Stream_{self.name}"


con = sqlite3.connect("db.db")
cursorObj = con.cursor()

cursorObj.execute("SELECT * FROM unit")
all_units = cursorObj.fetchall()

units = {
    unit_id: SecondaryUnit(name, unit_id) if unit_type else ABTUnit(name, unit_id)
    for unit_id, name, unit_type in all_units
}


cursorObj.execute("SELECT * FROM stream")
all_streams = cursorObj.fetchall()

streams = {stream_id: Stream(name, stream_id) for stream_id, name in all_streams}


cursorObj.execute("SELECT * FROM unit_material ")
all_unit_materials = cursorObj.fetchall()

for unit_id, stream_id, feed_flag in all_unit_materials:
    if feed_flag:
        units[unit_id].input_stream[stream_id] = streams[stream_id]
        streams[stream_id].add_where_to(units[unit_id])
    else:
        units[unit_id].output_stream[stream_id] = streams[stream_id]
        streams[stream_id].add_where_from(units[unit_id])


cursorObj.execute("SELECT * FROM load_max  ")
all_load_max = cursorObj.fetchall()
cursorObj.close()

for unit_id, load_max in all_load_max:
    units[unit_id].set_load_max(load_max)


with open("unused_streams.csv", "w") as f:
    for stream in streams.values():
        if not stream.where_from and not stream.where_to:
            f.write(f"{stream.id}, {stream.name}\n")


with open("multiple_streams.json", "w") as f:
    multiple_streams = {}
    for stream in streams.values():
        if len(stream.where_to) > 1:
            multiple_streams[stream.name] = [unit.name for unit in stream.where_to]
    json.dump(multiple_streams, f, indent=4)


wb = opx.Workbook()
wb.remove(wb.active)
for unit in units.values():

    ws = wb.create_sheet(unit.name)
    for index, input_stream in enumerate(unit.input_stream.values(), 1):
        print(input_stream.name)
        ws[f"A{index}"] = input_stream.name
    for index, output_stream in enumerate(unit.output_stream.values(), 1):
        ws[f"B{index}"] = output_stream.name

wb.save("all_units.xlsx")
