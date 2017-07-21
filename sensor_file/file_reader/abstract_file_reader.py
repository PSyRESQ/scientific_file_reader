#######################################################
# 
# deprec_abstract_file_reader.py
# Python implementation of the Class SensorFileReader
# Generated by Enterprise Architect
# Created on:      09-Jul-2017 21:09:12
# Original author: Laptop
# 
#######################################################
import datetime
from abc import abstractmethod
from collections import defaultdict

from typing import Dict, List

import sensor_file.file_parser.concrete_file_parser as file_parser
from sensor_file.domain.site import Sample, SensorPlateform

sample_ana_type = Dict[str, Sample]
sample_dict = Dict[str, sample_ana_type]
date_list = List[datetime.datetime]

class AbstractFileReader(object):
    """Interface permettant de lire un fichier provenant d'un datalogger quelconque
    classe permettant d'extraire des données d'un fichier quelconque.
    Un fichier de donnée est en général composé de :
    - Entete d'information sur l'environnement de prise de données
    - Entete d'information sur les colonnes de données
    - Les colonnes de données
    """
    TXT_FILE_TYPES = ['dat', 'lev']
    XLS_FILES_TYPES = ['xls', 'xlsx']
    CSV_FILES_TYPES = ['csv']
    XML_FILES_TYPES = ['xle']

    def __init__(self, file_name: str = None, header_length: int = 10):
        self._file = file_name
        self._header_length = header_length
        self._site_of_interest = None
        self.file_reader = None
        self._set_file_reader()

    @property
    def sites(self):
        return self._site_of_interest

    def _set_file_reader(self):
        """
        set the good file parser to open and read the provided file
        :return:
        """
        file_ext = self.file_extension
        if file_ext in self.TXT_FILE_TYPES:
            self.file_reader = file_parser.TXTFileParser(self._file, self._header_length)
        elif file_ext in self.XLS_FILES_TYPES:
            self.file_reader = file_parser.EXCELFileParser(self._file, self._header_length)
        elif file_ext in self.CSV_FILES_TYPES:
            self.file_reader = file_parser.CSVFileParser(self._file, self._header_length)
        elif file_ext in self.XML_FILES_TYPES:
            self.file_reader = file_parser.XMLFileParser(self._file)

        self.file_reader.read_file()

    def read_file(self):
        self._make_site()
        self._make_data()

    @property
    def file_extension(self):
        file_list = self._file.split(".")
        if len(file_list) == 1:
            raise ValueError("The path given doesn't point to a file name")
        if len(file_list) > 2:
            raise ValueError("The file name seems to be corrupted. Too much file extension in the current name")
        else:
            return file_list[-1].lower()

    @property
    def file_content(self):
        return self.file_reader.get_file_content

    def _make_site(self):
        """
        create a site object by reading the file header and the data header to know what
        was recorded by calling
        -   self._read_file_header()
        -   self._read_file_data_header()
        :return:
        """
        self._read_file_header()
        self._read_file_data_header()

    def _make_data(self):
        """
        read and classified the data by calling
        -   self._read_file_data()
        :return:
        """
        self._read_file_data()

    @abstractmethod
    def _read_file_header(self):
        """
        Read the file header
        :return:
        """
        pass

    @abstractmethod
    def _read_file_data_header(self):
        """
        read the data header (what was recorded)
        :return:
        """
        pass

    @abstractmethod
    def _read_file_data(self):
        """
        read and classified the data column
        :return:
        """
        pass


class PlateformReaderFile(AbstractFileReader):
    def __init__(self, file_name: str = None, header_length: int = 10):
        super().__init__(file_name, header_length)
        self._site_of_interest = SensorPlateform()
        self._date_list = None
    @abstractmethod
    def _get_date_list(self) -> date_list:
        pass


class GeochemistryFileReader(AbstractFileReader):
    def __init__(self, file_name: str = None,
                 header_length: int = 10,
                 _sites: sample_dict = None ):
        super().__init__(file_name, header_length)
        self._site_of_interest = defaultdict(dict)  # dict of Samples
        self.project = None
        self.report_date = None
        self.analysis_methode = None

    def create_sample(self, sample_name: str):
        sample = Sample(site_name=sample_name)
        self._site_of_interest[sample_name] = sample
        yield self._site_of_interest[sample_name]

    def create_complete_sample(self, site_name: str = None,
                               visit_date: datetime.datetime = None,
                               lab_sample_name: str = None,
                               sample_type: str = None,
                               project_name: str = None):
        sample = Sample(site_name, visit_date, lab_sample_name, sample_type, project_name)
        self._site_of_interest[site_name] = sample



