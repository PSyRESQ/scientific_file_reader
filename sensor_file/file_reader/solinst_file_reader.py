#!/usr/bin/env python
# -*- coding: utf-8 -*-
__author__ = 'Laptop$'
__date__ = '2017-07-16$'
__description__ = " "
__version__ = '1.0'

import datetime
import warnings
import re
from sensor_file.file_reader.abstract_file_reader import PlateformReaderFile
from collections import defaultdict

class SolinstFileReader(PlateformReaderFile):
    def __init__(self, file_name: str = None, header_length: int = 10):
        super().__init__(file_name, header_length)
        self.__main_reader = None

    def __set_reader(self):
        """
        set the correct file reader for the solinst file
        :return:
        """
        file_ext = self.file_extension

        if file_ext in self.CSV_FILES_TYPES:
            self.__main_reader = CSVSolinstFileReader(self._file)
        elif file_ext == 'lev':
            self.__main_reader = LEVSolinstFileReader(self._file)
        elif file_ext == 'xle':
            self.__main_reader = XLESolinstFileReader(self._file)
        else:
            warnings.warn("Unknown file extension for this compagny")
        print(self.__main_reader)
        self._site_of_interest = self.__main_reader._site_of_interest

    def read_file(self):
        self.__set_reader()
        self.__main_reader.read_file()


class LEVSolinstFileReader(PlateformReaderFile):
    DATA_CHANNEL_STRING = ".*CHANNEL {} from data header.*"

    def __init__(self, file_name: str = None, header_length: int = 10):
        super().__init__(file_name, header_length)
        self._update_header_lentgh()
        self._date_list = self._get_date_list()

    def _read_file_header(self):
        """
        implementation of the base class abstract method
        """
        self._update_plateform_attributes()

    def _read_file_data(self):
        """
        implementation of the base class abstract method
        """
        self._get_data()

    def _read_file_data_header(self):
        """
        implementation of the base class abstract method
        """
        pass

    def _update_plateform_attributes(self):
        self._site_of_interest.visit_date = self._create_visited_date()
        self._site_of_interest.site_name = self._get_site_name()
        self._site_of_interest.instrument_serial_number = self._get_serial_number()
        self._site_of_interest.project_name = self._get_project_name()
        self._site_of_interest.batterie_level = None
        self._site_of_interest.model_number = None

    def _create_visited_date(self) -> datetime:
        _date = None
        _time = None
        for lines in self.file_content[:self._header_length]:
            if re.search("^date.*", lines.lower()):
                _date = lines.split(":")[1].replace(" ", "")
            if re.search(r"^time.*", lines.lower()):
                _time = lines.split(" :")[1].replace(" ", "")
        to_datetime = datetime.datetime.strptime("{} {}".format(_date, _time), '%m/%d/%y %H:%M:%S')
        return to_datetime

    def _update_header_lentgh(self):
        for i, lines in enumerate(self.file_content):
            if re.search('^.data.*', lines.lower()):
                self._header_length = i + 1
                break

    def _get_instrument_info(self, regex_: str) -> str:
        str_to_find = None
        for lines in self.file_content:
            if re.search(regex_, lines):
                str_to_find = lines.split("=")[1]
                break
        return str_to_find

    def _get_site_name(self) -> str:
        return self._get_instrument_info(r".*[lL]ocation.*")

    def _get_serial_number(self):
        serial_string = self._get_instrument_info(r".*(S|s)erial.number.*")
        serial_numb = re.split(r"[ -]", serial_string)[1]
        return serial_numb

    def _get_project_name(self):
        return self._get_instrument_info(r".*(I|i)nstrument.number.*")

    def _get_number_of_channels(self) -> int:
        return int(self._get_instrument_info(r" *Channel *=.*"))

    def _get_date_list(self) -> list:
        datetime_list = []
        for lines in self.file_content[self._header_length + 1:-1]:
            sep_line = lines.split(" ")
            _date_time = datetime.datetime.strptime("{} {}".format(sep_line[0], sep_line[1]), '%Y/%m/%d %H:%M:%S.%f')
            datetime_list.append(_date_time)
        return datetime_list

    def _get_data(self):
        for channel_num in range(self._get_number_of_channels()):
            parameter = None
            parametere_unit = None

            for row_num, row in enumerate(self.file_content[:self._header_length]):
                if re.search(self.DATA_CHANNEL_STRING.format(channel_num + 1), row):
                    row_offset = 1
                    while not (re.search(self.DATA_CHANNEL_STRING.format(channel_num + 2),
                                         self.file_content[row_num + row_offset]) or
                                   re.search(r".*data.*", self.file_content[row_num + row_offset].lower())):
                        row_with_offset = str(self.file_content[row_num + row_offset])
                        if re.search(r".*identification.*", row_with_offset.lower()):
                            parameter = row_with_offset.split("=")[1]
                        if re.search(r".*unit.*", row_with_offset.lower()):
                            parametere_unit = row_with_offset.split("=")[1]
                        row_offset += 1

            values = []
            for lines in self.file_content[self._header_length + 1:-1]:
                sep_line = [data for data in list(lines.split(" ")) if data != '']
                values.append(sep_line[channel_num + 2])
            self._site_of_interest.create_time_serie(parameter, parametere_unit, self._date_list, values)


class XLESolinstFileReader(PlateformReaderFile):
    CHANNEL_DATA_HEADER = "Ch{}_data_header"

    def __init__(self, file_name: str = None, header_length: int = 10):
        super().__init__(file_name, header_length)

    def _read_file_header(self):
        """
        implementation of the base class abstract method
        """
        self._update_plateform_information()

    def _read_file_data(self):
        """
        implementation of the base class abstract method
        """

        self._date_list = self._get_date_list()
        self._get_data()

    def _read_file_data_header(self):
        """
        implementation of the base class abstract method
        """
        pass

    def _update_plateform_information(self):
        """
        update the SensorPlateform class (domain element) by setting its attributs
        :return:
        """
        self._site_of_interest.visit_date = self._create_visited_date()
        self._site_of_interest.site_name = self._get_site_name()
        self._site_of_interest.instrument_serial_number = self._get_serial_number()
        self._site_of_interest.project_name = self._get_project_name()
        self._site_of_interest.batterie_level = self._get_battery_level()
        self._site_of_interest.model_number = self._get_model_number()

    def _create_visited_date(self) -> datetime:
        """
        create a datetime object by reading the file header. The visited date is equal to
        the creation date of the file
        :return:
        """
        date_str = self.file_content.select_one('File_info').Date.string
        time_str = self.file_content.select_one('File_info').Time.string
        datetime_str = "{} {}".format(date_str, time_str)
        datetime_obj = datetime.datetime.strptime(datetime_str, '%Y/%m/%d %H:%M:%S')
        return datetime_obj

    def _get_site_name(self) -> str:
        return self.file_content.select_one('Instrument_info_data_header').Location.string

    def _get_serial_number(self):
        return self.file_content.select_one('Instrument_info').Serial_number.string

    def _get_project_name(self):
        return self.file_content.select_one('Instrument_info_data_header').Project_ID.string

    def _get_number_of_channels(self):
        return int(self.file_content.select_one('Instrument_info').Channel.string)

    def _get_model_number(self):
        return self.file_content.select_one('Instrument_info').Model_number.string

    def _get_battery_level(self):
        return self.file_content.select_one('Instrument_info').Battery_level.string

    def _get_date_list(self) -> list:
        """
        get a list of timestamp present in the file
        :return:
        """
        datetime_list = [datetime.datetime.strptime("{} {}:{}".format(_data.Date.string,
                                                                      _data.Time.string,
                                                                      _data.ms.string),
                                                    '%Y/%m/%d %H:%M:%S:%f')
                     for _data in self.file_content.find_all('Log')]
        return datetime_list


    def _get_data(self) -> None:
        """
        create time serie and update the SensorPlateform object
        :return:
        """
        for channels in range(self._get_number_of_channels()):
            channel_name = self.CHANNEL_DATA_HEADER.format(channels + 1)
            channel_parammeter = self.file_content.select_one(channel_name).Identification.string
            channel_unit = self.file_content.select_one(channel_name).Unit.string
            ch_selector = "ch{}"
            values = [d.text for d in self.file_content.find_all(ch_selector.format(channels + 1))]
            self._site_of_interest. \
                create_time_serie(channel_parammeter,
                                  channel_unit, self._date_list,
                                  values)


class CSVSolinstFileReader(PlateformReaderFile):
    UNIT = 'unit'
    PARAMETER_COL_INDEX = 'col_index'
    def __init__(self, file_name: str = None, header_length: int = 12):
        super().__init__(file_name, header_length)
        self._params_dict = defaultdict(dict)
        self._start_of_data_row_index = 0
    def _read_file_header(self):
        """
        implementation of the base class abstract method
        """
        self._get_file_header_data()


    def _read_file_data(self):
        """
        implementation of the base class abstract method
        """
        self._get_data()

    def _read_file_data_header(self):
        """
        implementation of the base class abstract method
        """
        self._get_parameter_data()
        self._date_list = self._get_date_list()

    def _get_file_header_data(self):
        i = 0
        while i < self._header_length:
            current_line = self.file_content[i][0]
            if re.search(r"[sS]erial.number.*]",current_line):
                i += 1
                current_line = self.file_content[i][0]
                self._site_of_interest.instrument_serial_number = current_line
            if re.search(r"[pP]roject.[idID].*",current_line):
                i += 1
                current_line = self.file_content[i][0]
                self._site_of_interest.project_name = current_line
            if re.search(r"[lL]ocation.*",current_line):
                i += 1
                current_line = self.file_content[i][0]
                self._site_of_interest.site_name = current_line
            i += 1

    def _get_date_list(self) ->list :
        date_times = []
        cells_to_check = 2
        # "{} {}:{}".format(_data.Date.string,
        #                   _data.Time.string,
        #                   _data.ms.string),
        date_format_string = "{} {}"
        strptime_string = '%Y/%m/%d %H:%M:%S'
        if 'ms' in self.file_content[self._start_of_data_row_index]:
            cells_to_check +=1
            strptime_string += ".%f"
            date_format_string += ".{}"
        for i, line in zip(range(10),self.file_content[self._start_of_data_row_index+1:]):
            _date_datetime = None
            try:
                _date_datetime = datetime.datetime.strptime(date_format_string.format(*line[:cells_to_check]),
                                                                         strptime_string)
            except ValueError as e:
                # warnings.warn('bad datetime format string. date string = '+ str(line[:cells_to_check]), e)
                strptime_string = strptime_string.replace("/","-")
                _date_datetime = datetime.datetime.strptime(date_format_string.format(*line[:cells_to_check]),
                                                            strptime_string)

            date_times.append(_date_datetime)
        return date_times


    def _get_parameter_data(self):
        row = 0
        while row < self._header_length:
            current_row = self.file_content[row]
            if len(current_row) > 1 and (current_row[0].lower() == 'date'
                and current_row[1].lower() == 'time'):
                self._start_of_data_row_index = row
                for i, cells in enumerate(current_row):
                    if cells.lower() not in ['date','ms','time']:
                        parameter = cells
                        parameter_col_index = i
                        for i in range(self._header_length):
                            if self.file_content[i][0] == parameter:
                                parameter_unit = self.file_content[i+1][0].split(": ")[1]
                                self._params_dict[parameter][self.UNIT] = parameter_unit
                                self._params_dict[parameter][self.PARAMETER_COL_INDEX] = parameter_col_index
                                break
            row += 1

    def _get_data(self):
        for parameter in list(self._params_dict.keys()):
            param_unit = self._params_dict[parameter][self.UNIT]
            param_col_index = self._params_dict[parameter][self.PARAMETER_COL_INDEX]
            values = [val[param_col_index] for val in self.file_content[self._start_of_data_row_index+1:]]
            self._site_of_interest.create_time_serie(parameter,param_unit,self._date_list,values)





if __name__ == '__main__':
    import os

    path = os.getcwd()
    while os.path.split(path)[1] != "scientific_file_reader":
        path = os.path.split(path)[0]
    file_loc = os.path.join(path, 'file_example')

    teste_all = True

    if teste_all:
        # file_name = "F21_logger_20160224_20160621.csv"
        file_name = "slug_PO-05_20160729_1600.csv"
        # file_name = "2029499_F7_NordChamp_PL20150925_2015_09_25.xle"
        # file_name = "2041929_PO-06_XM20170307_2017_03_07.lev"
        # file_name = "2056794_PO-05_baro_CB20161109_2016_11_09.lev"
        file_location = os.path.join(file_loc, file_name)
        print(file_location)
        solinst_file = SolinstFileReader(file_location)
        print(solinst_file.file_reader)
        solinst_file.read_file()
        print(solinst_file.sites)
        for time_serie in solinst_file.sites.records:
            print(str(time_serie))
