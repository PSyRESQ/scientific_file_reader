# -*- coding: utf-8 -*-
# -----------------------------------------------------------------------------
# Copyright © HydroSensorReader Project Contributors
# https://github.com/cgq-qgc/HydroSensorReader
#
# This file is part of HydroSensorReader.
# Licensed under the terms of the MIT License.
# -----------------------------------------------------------------------------

# ---- Standard imports
import os
import os.path as osp

# ---- Third party imports
import pytest
from pandas import Timestamp
import pandas as pd

# ---- Local imports
import hydsensread as hsr


# ---- Fixtures
@pytest.fixture(scope="module")
def test_files_dir():
    return osp.join(osp.dirname(__file__), 'files')


# ---- Tests
@pytest.mark.parametrize(
    'testfile',
    ["2XXXXXX_solinst_levelogger_edge.csv",
     "2XXXXXX_solinst_levelogger_edge.xle"])
def test_solinst_levelogger_edge(test_files_dir, testfile):
    """Test reading Solinst Edge Levelogger files."""
    solinst_file = hsr.SolinstFileReader(osp.join(test_files_dir, testfile))

    sites = solinst_file.sites
    assert sites.instrument_serial_number == "2010143"
    assert sites.project_name == "03040018"
    assert sites.site_name == "Sutton_PO22B"

    records = solinst_file.records
    assert len(records) == 200
    assert list(records.columns) == ["LEVEL_cm", "TEMPERATURE_degC"]

    assert records.index.tolist()[0] == Timestamp('2017-05-03 13:00:00')
    assert records.iloc[0].iloc[0] == 1919.32
    assert records.iloc[0].iloc[1] == 7.849

    assert records.index.tolist()[-1] == Timestamp('2017-05-05 14:45:00')
    assert records.iloc[-1].iloc[0] == 1920.85
    assert records.iloc[-1].iloc[1] == 7.872

    assert solinst_file.plot()


def test_solinst_levelogger_edge_lev(test_files_dir):
    """Test reading Solinst Edge Levelogger .lev files."""
    testfile = "2XXXXXX_solinst_levelogger_edge.lev"
    solinst_file = hsr.SolinstFileReader(osp.join(test_files_dir, testfile))

    sites = solinst_file.sites
    assert sites.instrument_serial_number == "2041929"
    assert sites.project_name == "McCully"
    assert sites.site_name == "PO-06_XM20170307"

    records = solinst_file.records
    assert len(records) == 200
    assert list(records.columns) == ["LEVEL_m", "TEMPERATURE_degC"]

    assert records.index.tolist()[0] == Timestamp('2017-03-07 19:00:00')
    assert records.iloc[0].iloc[0] == 14.6861
    assert records.iloc[0].iloc[1] == 7.626

    assert records.index.tolist()[-1] == Timestamp('2017-03-09 20:45:00')
    assert records.iloc[-1].iloc[0] == 14.5130
    assert records.iloc[-1].iloc[1] == 7.610

    assert solinst_file.plot()


@pytest.mark.parametrize(
    'testfile',
    ["1XXXXXX_solinst_levelogger_gold.csv",
     "1XXXXXX_solinst_levelogger_gold.lev"])
def test_solinst_levelogger_gold(test_files_dir, testfile):
    """
    Test reading Solinst Edge Levelogger files.

    Regression test for Issue #26.
    """
    solinst_file = hsr.SolinstFileReader(osp.join(test_files_dir, testfile))

    sites = solinst_file.sites
    assert sites.instrument_serial_number == "1062280"
    assert sites.project_name == "03030012"
    assert sites.site_name == "Saint-Guillaume_P14A"
    assert sites.other_attributes['altitude'] == 42

    records = solinst_file.records
    assert len(records) == 200
    assert list(records.columns) == ["LEVEL_cm", "TEMPERATURE_degC"]

    assert records.index[0] == Timestamp('2017-05-02 13:00:00')
    assert records.iloc[0].iloc[0] == 923.561
    assert records.iloc[0].iloc[1] == 8.936

    assert records.index[-1] == Timestamp('2017-05-04 14:45:00')
    assert records.iloc[-1].iloc[0] == 934.8801
    assert records.iloc[-1].iloc[1] == 8.914

    # Test undo altitude correction.
    solinst_file.undo_altitude_correction()
    assert records.iloc[-1].iloc[0] == 934.8801 - (0.12 * 42)
    assert records.iloc[-1].iloc[0] == 934.8801 - (0.12 * 42)

    # Test undo zero point offset.
    solinst_file.undo_zero_point_offset()
    assert records.iloc[0].iloc[0] == 923.561 - (0.12 * 42) + 950
    assert records.iloc[-1].iloc[0] == 934.8801 - (0.12 * 42) + 950

    assert solinst_file.plot()


@pytest.mark.parametrize(
    'testfile',
    ["XXXX_solinst_levelogger_M5.csv",
     "XXXX_solinst_levelogger_M5.lev"])
def test_solinst_levelogger_M5(test_files_dir, testfile):
    """
    Test reading Solinst Levelogger M5 files (older than the Gold series).
    """
    solinst_file = hsr.SolinstFileReader(osp.join(test_files_dir, testfile))

    sites = solinst_file.sites
    assert sites.instrument_serial_number == "5741"
    assert sites.project_name == "04040001"
    assert sites.site_name == "St-Andre-Avellin"
    assert sites.other_attributes['altitude'] == 170

    records = solinst_file.records
    assert len(records) == 200
    assert list(records.columns) == ["LEVEL_cm"]

    assert records.index[0] == Timestamp('2016-11-04 13:00:00')
    assert records.iloc[0].iloc[0] == 314.0

    assert records.index[-1] == Timestamp('2016-11-06 14:45:00')
    assert records.iloc[-1].iloc[0] == 317.5

    # Test undo altitude correction.
    solinst_file.undo_altitude_correction()
    assert records.iloc[0].iloc[0] == 314.0 - (0.12 * 170)
    assert records.iloc[-1].iloc[0] == 317.5 - (0.12 * 170)

    # Test undo zero point offset.
    solinst_file.undo_zero_point_offset()
    assert records.iloc[0].iloc[0] == 314.0 - (0.12 * 170) + 950
    assert records.iloc[-1].iloc[0] == 317.5 - (0.12 * 170) + 950

    assert solinst_file.plot()


@pytest.mark.parametrize(
    'testfile',
    ["2XXXXXX_solinst_colon_as_decimalsep.csv",
     "2XXXXXX_solinst_colon_as_decimalsep.xle"])
def test_solinst_colon_decimalsep(test_files_dir, testfile):
    """
    Test that level data can be read correctly from the Solinst data files when
    a colon is used as decimal separator instead of the dot.

    Regression test for cgq-qgc/HydroSensorReader#33.
    """
    solinst_file = hsr.SolinstFileReader(osp.join(test_files_dir, testfile))

    sites = solinst_file.sites
    assert sites.instrument_serial_number == "2048469"
    assert sites.project_name == "03040008"
    assert sites.site_name == "Rougemont_Plus profond"

    records = solinst_file.records
    assert len(records) == 10
    assert list(records.columns) == ["LEVEL_cm", "TEMPERATURE_degC"]

    assert records.index.tolist()[0] == Timestamp('2016-11-23 19:00:00')
    assert records.iloc[0].iloc[0] == 1813.03
    assert records.iloc[0].iloc[1] == 9.182

    assert records.index.tolist()[-1] == Timestamp('2016-11-23 21:15:00')
    assert records.iloc[-1].iloc[0] == 1812.59
    assert records.iloc[-1].iloc[1] == 9.179

    assert solinst_file.plot()


def test_missing_data(test_files_dir):
    """
    Test that file with missing data in a given channel can be read as
    expected.

    Regression test for cgq-qgc/HydroSensorReader#58.
    """
    testfile = 'solinst_missing_data.csv'
    solinst_file = hsr.SolinstFileReader(osp.join(test_files_dir, testfile))

    records = solinst_file.records
    assert len(records) == 10
    assert list(records.columns) == ["LEVEL_cm", "TEMPERATURE_degC"]
    assert pd.isnull(records.iloc[0]["TEMPERATURE_degC"])


def test_filename_with_dot_in_path(test_files_dir):
    """
    Test that a file with a dot in its path is read without raising any error.

    Regression rest for cgq-qgc/HydroSensorReader#57
    """
    testfile = 'solinst_file_with_._in_name.csv'
    solinst_file = hsr.SolinstFileReader(osp.join(test_files_dir, testfile))

    records = solinst_file.records
    assert len(records) == 10


if __name__ == "__main__":
    pytest.main(['-x', os.path.basename(__file__), '-v', '-rw'])
