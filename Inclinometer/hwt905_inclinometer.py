import os.path
import re
import pandas as pd
from datetime import datetime
from typing import List
from pandas.errors import EmptyDataError
from Inclinometer.inclinometer import Inclinometer
from Inclinometer.inclinometer_record import InclinometerRecord
from config import HWT905_INCLINOMETER_FILE_REGEX


class Hwt905Inclinometer(Inclinometer):

    def load(self, path) -> (List[InclinometerRecord]):
        file_name = os.path.basename(path)
        result = re.search(HWT905_INCLINOMETER_FILE_REGEX, file_name)
        year = int(result.group(1)) + 2000
        month = int(result.group(2))
        day = int(result.group(3))
        try:
            data = pd.read_csv(path, sep="\t", skiprows=1)
        except EmptyDataError:
            return []
        records = []
        for idx, row in data.iterrows():
            try:
                time_str = datetime.strptime(str(row["Time(s)"]).strip(), "%H:%M:%S.%f")
                record_datetime = time_str.replace(year=year, month=month, day=day)
                angle_x = row["AngleX(deg)"] if not self.swap_x_y else row["AngleY(deg)"]
                angle_y = row["AngleY(deg)"] if not self.swap_x_y else row["AngleX(deg)"]
                angle_z = row["AngleZ(deg)"]
                if self.invert_x:
                    angle_x *= -1
                if self.invert_y:
                    angle_y *= -1
                if self.invert_z:
                    angle_z *= -1
                records.append(InclinometerRecord(
                    datetime=record_datetime,
                    temp=row["T(°)"],
                    acceleration_x=row["ax(g)"],
                    acceleration_y=row["ay(g)"],
                    acceleration_z=row["az(g)"],
                    angular_velocity_x=row["wx(deg/s)"],
                    angular_velocity_y=row["wy(deg/s)"],
                    angular_velocity_z=row["wz(deg/s)"],
                    angle_x=angle_x,
                    angle_y=angle_y,
                    angle_z=angle_z,
                    hx=row["hx"],
                    hy=row["hy"],
                    hz=row["hz"]
                ))
            except Exception as ex:
                print(f"Error loading inclinometer record: {ex}")
        return records
