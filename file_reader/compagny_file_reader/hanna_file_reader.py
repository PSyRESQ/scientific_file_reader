#!/usr/bin/env python
# -*- coding: utf-8 -*-
__author__ = 'Laptop$'
__date__ = '2017-07-16$'
__description__ = " "
__version__ = '1.0'
import datetime
import re

import matplotlib.pyplot as plt
import pandas as pd

from file_reader.abstract_file_reader import TimeSeriesFileReader, date_list


class XLSHannaFileReader(TimeSeriesFileReader):
    def __init__(self, file_name: str = None, header_length: int = 10):
        super().__init__(file_name, header_length)
        self.header_content = {}

    def read_file(self):
        self._date_list = self._get_date_list()
        self._read_file_header()
        self._read_file_data_header()
        self._read_file_data()

    @property
    def header_info(self):
        return self.file_content[' Lot Info ']

    @property
    def data_sheet(self):
        return self.file_content[' Log data - 1']

    def _read_file_header(self):
        """
        implementation of the base class abstract method
        """
        for row in self.header_info:
            if row[0] is None or row[0] in ['GENERAL INFORMATION', 'LOT INFORMATION', 'SETTINGS']:
                pass
            else:
                key = re.sub('^ *', '', row[0])
                self.header_content[key] = row[1]

    def _get_date_list(self) -> date_list:
        date_list = [d[0] for d in hanna_file.data_sheet[1:]]
        time_list = [datetime.time(d[1].hour, d[1].minute, d[1].second) for d in hanna_file.data_sheet[1:]]
        date_time = [datetime.datetime(d.year, d.month, d.day, t.hour, t.minute, t.second)
                     for d, t in zip(date_list, time_list)]
        return date_time

    def _read_file_data(self):
        """
        implementation of the base class abstract method
        """
        values = [val[2:] for val in hanna_file.data_sheet[1:]]
        self._site_of_interest.records = pd.DataFrame(data=values, columns=hanna_file.data_sheet[0][2:],
                                                      index=self._get_date_list())


    def _read_file_data_header(self):
        """
        implementation of the base class abstract method
        """
        self.sites.site_name = self.header_content['Lot Name']
        self.sites.instrument_serial_number = self.header_content['Instrument Serial No.']
        self.sites.visit_date = self.header_content['Started Date and Time']

    def plot(self, *args, **kwargs):
        fig, temp_axe = plt.subplots(figsize=(20, 10))
        temp_axe.plot(self.records['Temp.[°C]'])
        temp_axe.set_ylabel('Temp.[°C]')
        ph_text = 'pH '
        ph_axe = temp_axe.twinx()
        ph_axe.plot(self.records[ph_text], color='orange', linestyle='--')
        ph_axe.set_ylabel(ph_text)

        do_text = 'D.O.[%]'
        cond_axe = temp_axe.twinx()
        cond_axe.plot(self.records[do_text], color='red')
        cond_axe.set_ylabel(do_text)
        cond_axe.spines["right"].set_position(("axes", 1.3))

        orp_text = 'ORP[mV]'
        orp_axe = temp_axe.twinx()
        orp_axe.plot(self.records[orp_text], color='red')
        orp_axe.set_ylabel(orp_text)
        orp_axe.spines["right"].set_position(("axes", 1.5))




if __name__ == '__main__':
    import os
    import pprint
    path = os.getcwd()
    while os.path.split(path)[1] != "scientific_file_reader":
        path = os.path.split(path)[0]
    file_loc = os.path.join(path, 'file_example')
    file_name = 'LOG006_0621113447.xls'
    file = os.path.join(file_loc, file_name)
    print(file)

    hanna_file = XLSHannaFileReader(file)
    hanna_file.read_file()
    pprint.pprint(hanna_file.header_content, width=250)

    print(hanna_file.records.head())
    print()
    hanna_file.plot(subplots=True, title=hanna_file.sites.site_name)
    plt.show(block=True)
