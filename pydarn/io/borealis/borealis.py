# Copyright 2019 SuperDARN Canada, University of Saskatchewan
# Author: Marci Detwiller
"""
This file contains classes for reading, writing, and
converting of Borealis file types. The file types that are supported.

Classes
-------
BorealisUtilities: utilites class that contains static methods for
SuperDARN file type checking
BorealisRead: Reads Borealis SuperDARN file types (hdf5)
BorealisWrite: Writes Borealis SuperDARN file types (hdf5)
BorealisConvert: Writes Borealis SuperDARN files types to
SuperDARN DARN files with DMap record structure

Exceptions
----------
BorealisFileTypeError
BorealisFieldMissingError
BorealisExtraFieldError
BorealisDataFormatTypeError
BorealisConversionTypesError
BorealisConvert2IqdatError
BorealisConvert2RawacfError
ConvertFileOverWriteError

Future work
-----------
Update to convert a restructured Borealis file into DMap directly
when Borealis files become restructured to save storage space.

Notes
-----
BorealisConvert makes use of DarnWrite to write to SuperDARN file types

See Also
--------

For more information on Borealis data files and how they convert to dmap,
see: https://borealis.readthedocs.io/en/latest/ 

"""
import deepdish as dd
import h5py
import logging
import math
import numpy as np
import os

from collections import OrderedDict
from datetime import datetime
from typing import Union, List

from pydarn import borealis_exceptions, DarnWrite, borealis_formats
from pydarn.utils.conversions import dict2dmap

pydarn_log = logging.getLogger('pydarn')

# 3 letter radar code, mapped to station id for DARN files conversion.
# TODO: when merged with plotting, remove this dictionary and call the 
#    one in the plotting folder... also move Radars.py to a more 
#    central location.
code_to_stid = {
    "tst": 0,
    "gbr": 1,
    "sch": 2,
    "kap": 3,
    "hal": 4,
    "sas": 5,
    "pgr": 6,
    "kod": 7,
    "sto": 8,
    "pyk": 9,
    "han": 10,
    "san": 11,
    "sys": 12,
    "sye": 13,
    "tig": 14,
    "ker": 15,
    "ksr": 16,
    "unw": 18,
    "zho": 19,
    "mcm": 20,
    "fir": 21,
    "sps": 22,
    "bpk": 24,
    "wal": 32,
    "bks": 33,
    "hok": 40,
    "hkw": 41,
    "inv": 64,
    "rkn": 65,
    "cly": 66,
    "dce": 96,
    "svb": 128,
    "fhw": 204,
    "fhe": 205,
    "cvw": 206,
    "cve": 207,
    "adw": 208,
    "ade": 209,
    "azw": 210,
    "aze": 211,
    "sve": 501,
    "svw": 502,
    "ire": 504,
    "irw": 505,
    "kae": 506,
    "kaw": 507,
    "eje": 508,
    "ejw": 509,
    "she": 510,
    "shw": 511,
    "ekb": 512,
}


class BorealisUtilities():
    """
    Utility class containing static methods used by other classes.

    Contains static methods that do dictionary set calculations 
    used for determining if there is any missing or extra
    fields in Borealis file types. Also does data format type checks
    for Borealis file types.

    Static Methods
    --------------
    dict_key_diff(dict1, dict2)
        Returns a set of the difference between dict1 and dict2 keys
    dict_list2set(dict_list)
        Converts a list of dictionaries to a set containing their keys
    missing_field_check(file_struct_list, record, record_name)
        Checks if there is any missing fields in the record from
        a list of possible file fields
    extra_field_check(file_struct_list, record, record_name)
        Checks if there is any extra fields in the record from
        a list of possible file fields
    incorrect_types_check(file_struct_list, record_name)
        Checks if there is any incorrect types in the record from
        a list of possible file fields and their data type formats
    """

    @staticmethod
    def dict_key_diff(dict1: Union[dict, set],
                      dict2: Union[dict, set]) -> set:
        """
        Determines the difference in the key set from the
        first dictionary to the second dictionary.
        ex) Let A = {a, b, c} and B = {d, a, b}
        Then A - B = {c}

        Parameters
        ----------
        dict1: dict or set
            dictionary or set to subtract from
        dict2: dict or set
            dictionary or set subtracting from dict1

        Returns
        -------
        dict_diff: set
            difference between dict1 and dict2 keys or the sets
        """
        diff_dict = set(dict1) - set(dict2)
        return diff_dict

    @staticmethod
    def dict_list2set(dict_list: List[dict]) -> set:
        """
        Converts a list of dictionaries to list of sets

        Parameters
        ----------
        dict_list: list
            list of dictionaries

        Returns
        -------
        complete_set: set
            set containing all dictionary key from the list of dicts
        """
        # convert dictionaries to set to do some set magic
        sets = [set(dic) for dic in dict_list]
        # create a complete set list
        # * - expands the list out into multiple set arguments
        # then the union operator creates it into a full unique set
        # example:
        # s = [{'a','v'}, {'v','x'}] => set.union(*s) = {'a', 'v', 'x'}
        complete_set = set.union(*sets)
        return complete_set

    @staticmethod
    def missing_field_check(file_struct_list: List[dict],
                            record: dict, record_name: int):
        """
        Checks if any fields are missing from the record compared to the file
        structure.

        Parameters
        ----------
        file_struct_list: List[dict]
            List of dictionaries for the possible file structure fields
        record: dict
            Dictionary representing the DMap record
        record_name: int
            The name of the record (first sequence start time)

        Raises
        -------
        BorealisFieldMissing
        
        Notes
        -----
        Checks sets and subsets. Any missing fields are a problem because
        Borealis field names are well-defined.
        """
        missing_fields = set()
        for file_struct in file_struct_list:
            diff_fields = BorealisUtilities.dict_key_diff(file_struct, record)
            if len(diff_fields) != 0:
                missing_fields = missing_fields.union(diff_fields)

        if len(missing_fields) > 0:
            raise borealis_exceptions.BorealisFieldMissingError(record_name,
                                                                missing_fields)

    @staticmethod
    def extra_field_check(file_struct_list: List[dict],
                          record: dict, record_name: int):
        """
        Check if there is an extra field in the file structure list and record.

        Parameters
        ----------
        file_struct_list: List[dict]
            List of dictionaries for the possible file structure fields
        record: dict
            DMap record
        record_name: int
            Record name for better error message information

        Raises
        ------
        BorealisExtraField
        """
        file_struct = BorealisUtilities.dict_list2set(file_struct_list)
        extra_fields = BorealisUtilities.dict_key_diff(record, file_struct)

        if len(extra_fields) > 0:
            raise borealis_exceptions.BorealisExtraFieldError(record_name,
                                                              extra_fields)

    @staticmethod
    def incorrect_types_check(attributes_type_dict: dict,
                              datasets_type_dict: dict,
                              record: dict,
                              record_name: int):
        """
        Checks if the file structure fields data type formats are correct
        in the record.

        Checks both single element types and numpy array dtypes separately.

        Parameters
        ----------
        attributes_type_dict: dict
            Dictionary with the required types for the attributes in the file.
        datasets_type_dict: dict
            Dictionary with the require dtypes for the numpy
            arrays in the file.
        record: dict
            DMap record
        record_name: int
            Record name for a better error message information

        Raises
        ------
        BorealisFileFormatError
        """
        incorrect_types_check = {param: str(attributes_type_dict[param])
                                 for param in attributes_type_dict.keys()
                                 if type(record[param]) !=
                                 attributes_type_dict[param]}

        incorrect_types_check.update({param: 'np.ndarray of ' +
                                      str(datasets_type_dict[param])
                                      for param in datasets_type_dict.keys()
                                      if record[param].dtype.type !=
                                      datasets_type_dict[param]})
        if len(incorrect_types_check) > 0:
            raise borealis_exceptions.BorealisDataFormatTypeError(
                incorrect_types_check, record_name)


class BorealisRead():
    """
    Class for reading Borealis filetypes.

    See Also
    --------
    BorealisRawacf
    BorealisBfiq
    BorealisAntennasIq
    BorealisRawrf

    Attributes
    ----------
    filename: str
        The filename of the Borealis HDF5 file being read.
    group_names: list(str)
    current_record_name: str
    records: OrderedDict{dict}
    """

    def __init__(self, filename: str):
        """
        Reads SuperDARN Borealis file types into a dictionary.

        Parameters
        ----------
        filename: str
            file name containing Borealis hdf5 data.

        Raises
        ------
        OSError
            Unable to open file
        """
        self.filename = filename

        with h5py.File(self.filename, 'r') as f:
            self._group_names = sorted(list(f.keys()))
            # list of group keys in the HDF5 file, to allow partial read.

        self._current_record_name = ''  # Current HDF5 record group name.

        # Records are private to avoid tampering.
        self._records = OrderedDict()

    def __repr__(self):
        """ for representation of the class object"""
        # __class__.__name__ allows to grab the class name such that
        # when a class inherits this one, the class name will be the child
        # class and not the parent class
        return "{class_name}({filename}, {current_record_name})"\
            "".format(class_name=self.__class__.__name__,
                      filename=self.filename,
                      current_record_name=self.current_record_name)

    def __str__(self):
        """ for printing of the class object"""

        return "Reading from {filename} at current record:"\
            " {current_record_name} a total number of"\
            " records: {total_records}"\
            "".format(filename=self.filename,
                      cursor=self.current_record_name,
                      total_records=len(list(self.records.keys())))

    @property
    def current_record_name(self):
        """
        The name of the current record being read, string.
        """
        return self._current_record_name

    @property
    def group_names(self):
        """
        A sorted list of the set of group names in the HDF5 file read. These 
        correspond to Borealis file record write times (in ms).
        """
        return self._group_names

    @property
    def records(self):
        """
        The dictionary of records read from the HDF5 file.
        """
        return self._records

    def read_file(self, borealis_filetype: str) -> dict:
        """
        Reads the specified Borealis file using the other functions for 
        the proper file type.

        Reads the entire file.

        See Also
        --------
        read_bfiq
        read_rawacf
        read_antennas_iq
        read_rawrf

        Returns
        -------
        records: OrderedDict{dict}
            records of borealis data. Keys are first sequence timestamp 
            (in ms since epoch).

        Raises
        ------
        BorealisFileTypeError
        """
        if borealis_filetype == 'bfiq':
            self.read_bfiq()
            return self._records
        elif borealis_filetype == 'rawacf':
            self.read_rawacf()
            return self._records
        elif borealis_filetype == 'antennas_iq':
            self.read_antennas_iq()
            return self._records
        elif borealis_filetype == 'rawrf':
            self.read_rawrf()
            return self._records
        else:
            raise borealis_exceptions.BorealisFileTypeError(
                self.filename, borealis_filetype)

    def read_bfiq(self) -> dict:
        """
        Reads Borealis bfiq file

        Returns
        -------
        records: OrderedDict{dict}
            records of beamformed iq data. Keys are first sequence timestamp
            (in ms since epoch).
        """
        pydarn_log.debug("Reading Borealis bfiq file: {}"
                         "".format(self.filename))
        attribute_types = borealis_formats.BorealisBfiq.single_element_types
        dataset_types = borealis_formats.BorealisBfiq.array_dtypes
        self._read_borealis_records(attribute_types, dataset_types)
        return self._records

    def read_rawacf(self) -> dict:
        """
        Reads Borealis rawacf file

        Returns
        -------
        records: OrderedDict{dict}
            records of borealis rawacf data. Keys are first sequence timestamp 
            (in ms since epoch).
        """
        pydarn_log.debug(
            "Reading Borealis rawacf file: {}".format(self.filename))
        attribute_types = borealis_formats.BorealisRawacf.single_element_types
        dataset_types = borealis_formats.BorealisRawacf.array_dtypes
        self._read_borealis_records(attribute_types, dataset_types)
        return self._records

    def read_antennas_iq(self) -> dict:
        """
        Reads Borealis antennas_iq file

        Returns
        -------
        records: OrderedDict{dict}
            records of borealis antennas iq data. Keys are first sequence
            timestamp (in ms since epoch).
        """
        pydarn_log.debug("Reading Borealis antennas_iq file: {}"
                         "".format(self.filename))
        attribute_types = \
            borealis_formats.BorealisAntennasIq.single_element_types
        dataset_types = borealis_formats.BorealisAntennasIq.array_dtypes
        self._read_borealis_records(attribute_types, dataset_types)
        return self._records

    def read_rawrf(self) -> dict:
        """
        Reads Borealis rawrf file

        Returns
        -------
        records: OrderedDict{dict}
            records of borealis rawrf data. Keys are first sequence timestamp
            (in ms since epoch).
        """
        pydarn_log.debug("Reading Borealis rawrf file: {}"
                         "".format(self.filename))
        attribute_types = borealis_formats.BorealisRawrf.single_element_types
        dataset_types = borealis_formats.BorealisRawrf.array_dtypes
        self._read_borealis_records(attribute_types, dataset_types)
        return self._records

    def _read_borealis_records(self, attribute_types: dict,
                               dataset_types: dict):
        """
        Read the entire file while checking all data fields.

        Parameters
        ----------
        attribute_types: dict
            Dictionary with the required types for the attributes in the file.
        dataset_types: dict
            Dictionary with the require dtypes for the numpy arrays in the 
            file.

        """
        for record_name in self._group_names:
            self._current_record_name = record_name
            self._read_borealis_record(attribute_types, dataset_types)

    def _read_borealis_record(self, attribute_types: dict,
                              dataset_types: dict):
        """
        Read a Borealis HDF5 record. 

        Several Borealis field checks are done to insure the integrity of the
        file. Appends to the records dictionary.

        Parameters
        ----------
        attribute_types: dict
            Dictionary with the required types for the attributes in the file.
        dataset_types: dict
            Dictionary with the require dtypes for the numpy arrays in the 
            file.

        Raises
        ------
        OSError: file does not exist
        BorealisFieldMissingError - when a field is missing from the Borealis
                                file/stream type
        BorealisExtraFieldError - when an extra field is present in the
                                Borealis file/stream type
        BorealisDataFormatTypeError - when a field has the incorrect
                                field type for the Borealis file/stream type

        See Also
        --------
        missing_field_check(format_fields, record, record_name) - checks
            for missing fields. See this method for information
            on why we use format_fields.
        extra_field_check(format_fields, record, record_name) - checks for
            extra fields in the record
        incorrect_types_check(attribute_types_dict, dataset_types_dict, record,
            record_name) - checks for incorrect data types for file fields
        """
        all_format_fields = [attribute_types, dataset_types]

        record = dd.io.load(self.filename, group='/' +
                            self._current_record_name)
        BorealisUtilities.missing_field_check(
            all_format_fields, record, self._current_record_name)
        BorealisUtilities.extra_field_check(
            all_format_fields, record, self._current_record_name)
        BorealisUtilities.incorrect_types_check(
            attribute_types, dataset_types, record, self._current_record_name)
        self._records[self._current_record_name] = record


class BorealisWrite():
    """
    Class for writing Borealis filetypes.

    See Also
    --------
    BorealisRawacf
    BorealisBfiq
    BorealisAntennasIq
    BorealisRawrf

    Attributes
    ----------
    filename: str
        The filename of the Borealis HDF5 file being read.
    borealis_records: OrderedDict{dict}
        The dictionary of Borealis records to write to HDF5 file.
    group_names: list(str)
        The list of record names of the Borealis data. These values 
        are the write time of the record in ms since epoch.
    current_record_name: str
    """

    def __init__(self, filename: str, 
                 borealis_records: OrderedDict = OrderedDict()):
        """
        Write borealis records to a file.

        Parameters
        ----------
        filename: str
            Name of the file the user wants to write to
        borealis_records: OrderedDict{dict}
            OrderedDict of borealis records

        """
        self.borealis_records = borealis_records
        self.filename = filename
        self._group_names = sorted(list(borealis_records.keys()))
        # list of group keys for partial write
        self._current_record_name = ''

    def __repr__(self):
        """For representation of the class object"""

        return "{class_name}({filename}, {current_record_name})"\
               "".format(class_name=self.__class__.__name__,
                         filename=self.filename,
                         current_record_name=self.current_record_name)

    def __str__(self):
        """For printing of the class object"""

        return "Writing to filename: {filename} at record name: "\
               "{current_record_name}".format(filename=self.filename,
                    current_record_name=self.current_record_name)

    @property
    def current_record_name(self):
        """
        The current record name, str, represented by ms since epoch.
        """
        return self._current_record_name

    def write_file(self, borealis_filetype) -> str:
        """
        Write Borealis records to a file given filetype.

        Parameters
        ----------
        borealis_filetype
            filetype to write as. Currently supported:
                - bfiq
                - rawacf
                - antennas_iq
                - rawrf

        Raises
        ------
        BorealisFileTypeError
        """

        if borealis_filetype == 'bfiq':
            self.write_bfiq()
        elif borealis_filetype == 'rawacf':
            self.write_rawacf()
        elif borealis_filetype == 'antennas_iq':
            self.write_antennas_iq()
        elif borealis_filetype == 'rawrf':
            self.write_rawrf()
        else:
            raise borealis_exceptions.BorealisFileTypeError(self.filename,
                                                            borealis_filetype)

    def write_bfiq(self) -> str:
        """
        Writes Borealis bfiq file

        Returns
        -------
        filename: str
            Filename of written file.
        """
        pydarn_log.debug(
            "Writing Borealis bfiq file: {}".format(self.filename))
        attribute_types = borealis_formats.BorealisBfiq.single_element_types
        dataset_types = borealis_formats.BorealisBfiq.array_dtypes
        self._write_borealis_records(attribute_types, dataset_types)
        return self.filename

    def write_rawacf(self) -> str:
        """
        Writes Borealis rawacf file

        Returns
        -------
        filename: str
            Filename of written file.
        """
        pydarn_log.debug(
            "Writing Borealis rawacf file: {}".format(self.filename))
        attribute_types = borealis_formats.BorealisRawacf.single_element_types
        dataset_types = borealis_formats.BorealisRawacf.array_dtypes
        self._write_borealis_records(attribute_types, dataset_types)
        return self.filename

    def write_antennas_iq(self) -> str:
        """
        Writes Borealis antennas_iq file

        Returns
        -------
        filename: str
            Filename of written file.
        """
        pydarn_log.debug(
            "Writing Borealis antennas_iq file: {}".format(self.filename))
        attribute_types = \
            borealis_formats.BorealisAntennasIq.single_element_types
        dataset_types = borealis_formats.BorealisAntennasIq.array_dtypes
        self._write_borealis_records(attribute_types, dataset_types)
        return self.filename

    def write_rawrf(self) -> str:
        """
        Writes Borealis rawrf file

        Returns
        -------
        filename: str
            Filename of written file.
        """
        pydarn_log.debug(
            "Writing Borealis rawrf file: {}".format(self.filename))
        attribute_types = borealis_formats.BorealisRawrf.single_element_types
        dataset_types = borealis_formats.BorealisRawrf.array_dtypes
        self._write_borealis_records(attribute_types, dataset_types)
        return self.filename

    def _write_borealis_records(self, attribute_types: dict,
                                dataset_types: dict):
        """
        Write the file record by record checking each record as we go.

        Parameters
        ----------
        attributes_type_dict: dict
            Dictionary with the required types for the attributes in the file.
        datasets_type_dict: dict
            Dictionary with the require dtypes for the numpy arrays in the 
            file.

        Raises
        ------
        OSError: file does not exist

        """
        for record_name in self._group_names:
            self._current_record_name = record_name
            self._write_borealis_record(attribute_types, dataset_types)

    def _write_borealis_record(self, attribute_types: dict,
                               dataset_types: dict):
        """
        Writes a Borealis HDF5 record. 

        Several Borealis field checks are done to insure the integrity of the 
        file. Appends to the file.

        Parameters
        ----------
        attributes_type_dict: dict
            Dictionary with the required types for the attributes in the file.
        datasets_type_dict: dict
            Dictionary with the require dtypes for the numpy arrays in the 
            file.

        Raises:
        -------
        BorealisFieldMissingError - when a field is missing from the Borealis
                                file/stream type
        BorealisExtraFieldError - when an extra field is present in the
                                Borealis file/stream type
        BorealisDataFormatTypeError - when a field has the incorrect
                                field type for the Borealis file/stream type

        See Also
        --------
        missing_field_check(format_fields, record, record_name) - checks
                        for missing fields. See this method for information
                        on why we use format_fields.
        extra_field_check(format_fields, record, record_name) - checks for
                        extra fields in the record
        incorrect_types_check(attribute_types_dict, dataset_types_dict,
                        record, record_name) - checks
                        for incorrect data types for file fields
        """

        all_format_fields = [attribute_types, dataset_types]
        record = self.borealis_records[self._current_record_name]
        BorealisUtilities.missing_field_check(all_format_fields, record,
                                              self._current_record_name)
        BorealisUtilities.extra_field_check(all_format_fields, record,
                                            self._current_record_name)
        BorealisUtilities.incorrect_types_check(attribute_types, 
                                                dataset_types, record,
                                                self._current_record_name)
        dd.io.save(self.filename, {self._current_record_name: record},
                   compression=None)


class BorealisConvert():
    """
    Class for converting Borealis filetypes.

    See Also
    --------
    BorealisRawacf
    BorealisBfiq
    Rawacf
    Iqdat
    BorealisRead
    DarnWrite

    Attributes
    ----------
    filename: str
        The filename of the Borealis HDF5 file being read.
    origin_filetype: str
    borealis_records: OrderedDict{dict}
    group_names: list[str]
    dmap_records: list[dict]
    """


    def __init__(self, filename):
        """
        Convert HDF5 Borealis records to a given DARN file with DMap format.

        Parameters
        ----------
        filename: str
            Name of file to read records from
        """
        self.filename = filename
        borealis_reader = BorealisRead(self.filename)
        self._origin_filetype = os.path.basename(self.filename).split('.')[-2]
        self._borealis_records = borealis_reader.read_file(
            self.origin_filetype)
        self._group_names = sorted(list(self.borealis_records.keys()))
        self._dmap_records = {}

    def __repr__(self):
        """ for representation of the class object"""

        return "{class_name}({filename})"\
               "".format(class_name=self.__class__.__name__,
                         filename=self.filename)

    def __str__(self):
        """ for printing of the class object"""

        return "Reading filename to convert: {filename} with number of "\
               "records: {total_records}.".format(filename=self.filename,
                    total_records=len(self.borealis_records.keys()))

    @property
    def borealis_records(self):
        """
        The records of the Borealis file in a dictionary.
        """
        return self._borealis_records

    @property
    def group_names(self):
        """
        The list of sorted record names of the Borealis data. These values 
        are the write time of the record in ms since epoch.
        """
        return self._group_names

    @property
    def origin_filetype(self):
        """
        The origin filetype of the Borealis data. E.g. rawacf, bfiq.
        """
        return self._origin_filetype

    @property
    def dmap_records(self):
        """
        The converted DMap records to write to file.
        """
        return self._dmap_records

    def write_to_dmap(self, dmap_filetype, dmap_filename) -> str:
        """
        Write the Borealis records as dmap records to a dmap file using PyDARN
        IO.

        Parameters
        ----------
        dmap_filetype: str
            Intended DARN filetype to write to as DMap.
            The following DMap types are supported:
                                     - 'iqdat': Iqdat SuperDARN file type 
                                     (converted from Borealis bfiq)
                                     - 'rawacf': Rawacf SuperDARN file type
                                     (converted from Borealis rawacf)
        dmap_filename: str
            Filename with directory you want to write to.

        Raises
        ------
        BorealisConversionTypesError

        Returns
        -------
        dmap_filename, the name of the DARN file written.
        """
        self._dmap_records = self._convert_records_to_dmap(dmap_filetype)
        darn_writer = DarnWrite(self._dmap_records, dmap_filename)
        if dmap_filetype == 'iqdat':
            darn_writer.write_iqdat(dmap_filename)
        elif dmap_filetype == 'rawacf':
            darn_writer.write_rawacf(dmap_filename)
        else:
            raise borealis_exceptions.BorealisConversionTypesError(
                self.filename, self.origin_filetype, dmap_filetype)
        return dmap_filename

    def _convert_records_to_dmap(self, dmap_filetype):
        """
        Convert the Borealis records to the DMap filetype, if possible.

        Parameters
        ----------
        dmap_filetype: str
            Intended DARN filetype to write to as DMap.
            The following DMap types are supported:
                                     - 'iqdat': Iqdat SuperDARN file type
                                     - 'rawacf': Rawacf SuperDARN file type

        Raises
        ------
        BorealisConversionTypesError

        Returns
        -------
        dmap_records, the records converted to DMap format
        """
        if dmap_filetype == 'iqdat':
            if self._is_convertible_to_iqdat():
                dmap_records = self._convert_bfiq_to_iqdat()
        elif dmap_filetype == 'rawacf':
            if self._is_convertible_to_rawacf():
                dmap_records = self._convert_rawacf_to_rawacf()
        else:  # nothing else is currently supported
            raise borealis_exceptions.BorealisConversionTypesError(
                self.filename, self.origin_filetype, dmap_filetype)

        return dmap_records

    def _is_convertible_to_iqdat(self) -> bool:
        """
        Checks if the file is convertible to iqdat.

        The file is convertible if:
            - the origin filetype is bfiq
            - the blanked_samples array = pulses array for all records
            - the pulse_phase_offset array contains all zeroes for all records

        Raises
        ------
        BorealisConversionTypesError
        BorealisConvert2IqdatError

        Returns
        -------
        True if convertible
        """
        if self.origin_filetype != 'bfiq':
            raise borealis_exceptions.BorealisConversionTypesError(
                self.filename, self.origin_filetype, self.dmap_filetype)
        else:  # There are some specific things to check
            for k, v in self._borealis_records.items():
                if not np.array_equal(v['blanked_samples'],
                        v['pulses']*int(v['tau_spacing']/v['tx_pulse_len'])):
                    raise borealis_exceptions.BorealisConvert2IqdatError(
                        'Borealis bfiq file record {} blanked_samples {} '
                        'does not equal pulses array {}'
                        .format(k, v['blanked_samples'], v['pulses']))
                if not all([x == 0 for x in v['pulse_phase_offset']]):
                    raise borealis_exceptions.BorealisConvert2IqdatError(
                        'Borealis bfiq file record {} pulse_phase_offset {} '
                        'contains non-zero values.'
                        .format(k, v['pulse_phase_offset']))
        return True

    def _is_convertible_to_rawacf(self) -> bool:
        """
        Checks if the file is convertible to rawacf.

        The file is convertible if:
            - the origin filetype is rawacf
            - the blanked_samples array = pulses array for all records
            - the pulse_phase_offset array contains all zeroes for all records

        Raises
        ------
        BorealisConversionTypesError
        BorealisConvert2RawacfError

        Returns
        -------
        True if convertible
        """
        if self.origin_filetype != 'rawacf':
            raise borealis_exceptions.BorealisConversionTypesError(
                self.filename, self.origin_filetype, self.dmap_filetype)
        else:  # There are some specific things to check
            for k, v in self._borealis_records.items():
                if not np.array_equal(v['blanked_samples'], 
                        v['pulses']*int(v['tau_spacing']/v['tx_pulse_len'])):
                    raise borealis_exceptions.BorealisConvert2RawacfError(
                        'Borealis rawacf file record {} blanked_samples {} '
                        'does not equal pulses array {}'
                        .format(k, v['blanked_samples'], v['pulses']))

        return True

    def _convert_bfiq_to_iqdat(self):
        """
        Conversion for bfiq to iqdat DMap records.

        See Also
        --------
        https://superdarn.github.io/rst/superdarn/src.doc/rfc/0027.html
        https://borealis.readthedocs.io/en/latest/
        BorealisBfiq
        Iqdat

        Returns
        -------
        dmap_recs, the records converted to DMap format
        """
        recs = []
        for k, v in self._borealis_records.items():
            # data_descriptors (dimensions) are num_antenna_arrays, 
            # num_sequences, num_beams, num_samps
            # scale by normalization and then scale to integer max as per 
            # dmap style 
            data = v['data'].reshape(v['data_dimensions']).astype(
                np.complex128) / v['data_normalization_factor'] * \
                np.iinfo(np.int16).max

            # Borealis git tag version numbers. If not a tagged version,
            # then use 255.255
            if v['borealis_git_hash'][0] == 'v' and \
                    v['borealis_git_hash'][2] == '.':

                borealis_major_revision = v['borealis_git_hash'][1]
                borealis_minor_revision = v['borealis_git_hash'][3]
            else:
                borealis_major_revision = 255
                borealis_minor_revision = 255

            slice_id = os.path.basename(self.filename).split('.')[-3]
            # base offset for setting the toff field in DARN iqdat file.
            offset = 2 * v['antenna_arrays_order'].shape[0] * v['num_samps']

            for beam_index, beam in enumerate(v['beam_nums']):
                # grab this beam's data
                # shape is now num_antenna_arrays x num_sequences x num_samps
                this_data = data[:, :, beam_index, :]
                # iqdat shape is num_sequences x num_antennas_arrays x 
                # num_samps x 2 (real, imag), flattened
                reshaped_data = []
                for i in range(v['num_sequences']):
                    # get the samples for each array 1 after the other
                    arrays = [this_data[x, i, :]
                              for x in range(this_data.shape[0])]
                    reshaped_data.append(
                        np.ravel(np.column_stack(arrays)))  # append

                # (num_sequences x num_antenna_arrays x num_samps, flattened)
                flattened_data = np.array(reshaped_data).flatten()

                int_data = np.empty(flattened_data.size * 2, dtype=np.int16)
                int_data[0::2] = flattened_data.real
                int_data[1::2] = flattened_data.imag

                # flattening done in convert_to_dmap_datastructures
                record_dict = {
                    'radar.revision.major': np.int8(borealis_major_revision),
                    'radar.revision.minor': np.int8(borealis_minor_revision),
                    'origin.code': np.int8(100),  # indicating Borealis origin
                    'origin.time': datetime.utcfromtimestamp(
                        v['sqn_timestamps'][0]).strftime("%c"),
                    'origin.command': 'Borealis ' + v['borealis_git_hash'] + \
                        ' ' + v['experiment_name'],
                    'cp': np.int16(v['experiment_id']),
                    'stid': np.int16(code_to_stid[v['station']]),
                    'time.yr': np.int16(datetime.utcfromtimestamp(
                        v['sqn_timestamps'][0]).year),
                    'time.mo': np.int16(datetime.utcfromtimestamp(
                        v['sqn_timestamps'][0]).month),
                    'time.dy': np.int16(datetime.utcfromtimestamp(
                        v['sqn_timestamps'][0]).day),
                    'time.hr': np.int16(datetime.utcfromtimestamp(
                        v['sqn_timestamps'][0]).hour),
                    'time.mt': np.int16(datetime.utcfromtimestamp(
                        v['sqn_timestamps'][0]).minute),
                    'time.sc': np.int16(datetime.utcfromtimestamp(
                        v['sqn_timestamps'][0]).second),
                    'time.us': np.int32(datetime.utcfromtimestamp(
                        v['sqn_timestamps'][0]).microsecond),
                    'txpow': np.int16(-1),
                    'nave': np.int16(v['num_sequences']),
                    'atten': np.int16(0),
                    'lagfr': np.int16(v['first_range_rtt']),
                    # smsep is in us; conversion from seconds
                    'smsep': np.int16(1e6/v['rx_sample_rate']),
                    'ercod': np.int16(0),
                    # TODO: currently not implemented
                    'stat.agc': np.int16(0),
                    # TODO: currently not implemented
                    'stat.lopwr': np.int16(0),
                    # TODO: currently not implemented
                    'noise.search': np.float32(v['noise_at_freq'][0]),
                    # TODO: currently not implemented
                    'noise.mean': np.float32(0),
                    'channel': np.int16(slice_id),
                    'bmnum': np.int16(beam),
                    'bmazm': np.float32(v['beam_azms'][beam_index]),
                    'scan': np.int16(v['scan_start_marker']),
                    # no digital receiver offset or rxrise required in Borealis
                    'offset': np.int16(0),
                    'rxrise': np.int16(0),
                    'intt.sc': np.int16(math.floor(v['int_time'])),
                    'intt.us': np.int32(math.fmod(v['int_time'], 1.0) * 1e6),
                    'txpl': np.int16(v['tx_pulse_len']),
                    'mpinc': np.int16(v['tau_spacing']),
                    'mppul': np.int16(len(v['pulses'])),
                    # an alternate lag-zero will be given, so subtract 1.
                    'mplgs': np.int16(v['lags'].shape[0] - 1),
                    'nrang': np.int16(v['num_ranges']),
                    'frang': np.int16(round(v['first_range'])),
                    'rsep': np.int16(round(v['range_sep'])),
                    'xcf': np.int16('intf' in v['antenna_arrays_order']),
                    'tfreq': np.int16(v['freq']),
                    # mxpwr filler; cannot specify this information
                    'mxpwr': np.int32(-1),
                    # lvmax RST default
                    'lvmax': np.int32(20000),
                    'iqdata.revision.major': np.int32(1),
                    'iqdata.revision.minor': np.int32(0),
                    'combf': 'Converted from Borealis file: ' + \
                        self.filename  + ' record ' + k + \
                        ' ; Number of beams in record: ' + \
                        str(len(v['beam_nums'])) + ' ; ' + \
                        v['experiment_comment'] + ' ; ' + v['slice_comment'],
                    'seqnum': np.int32(v['num_sequences']),
                    'chnnum': np.int32(v['antenna_arrays_order'].shape[0]),
                    'smpnum': np.int32(v['num_samps']),
                    # NOTE: The following is a hack. This is currently how 
                    # iqdat files are being processed . RST make_raw does 
                    # not use first range information at all, only skip number.
                    # However ROS provides the number of ranges to the first 
                    # range as the skip number. Skip number was originally 
                    # intended to identify bad ranges due to digital receiver 
                    # rise time. Borealis skpnum should in theory =0 as the 
                    # first sample from Borealis decimated (prebfiq)
                    # data is centred on the first pulse.
                    'skpnum': np.int32(v['first_range']/v['range_sep']),
                    'ptab': v['pulses'].astype(np.int16),
                    'ltab': v['lags'].astype(np.int16),
                    # timestamps in ms, convert to seconds and us.
                    'tsc': np.array([math.floor(x/1e3) for x in 
                        v['sqn_timestamps']], dtype=np.int32),
                    'tus': np.array([math.fmod(x, 1000.0) * 1e3 for x in 
                        v['sqn_timestamps']], dtype=np.int32),
                    'tatten': np.array([0] * v['num_sequences'], 
                        dtype=np.int16),
                    'tnoise': v['noise_at_freq'].astype(np.float32),
                    'toff': np.array([i * offset for i in 
                        range(v['num_sequences'])], dtype=np.int32),
                    'tsze': np.array([offset] * v['num_sequences'], 
                        dtype=np.int32),
                    'data': int_data
                }
                recs.append(record_dict)

        dmap_recs = dict2dmap(recs)
        return dmap_recs

    def _convert_rawacf_to_rawacf(self):
        """
        Conversion for Borealis hdf5 rawacf to DARN DMap rawacf files.

        See Also
        --------
        https://superdarn.github.io/rst/superdarn/src.doc/rfc/0008.html
        https://borealis.readthedocs.io/en/latest/
        BorealisRawacf
        Rawacf

        Returns
        -------
        dmap_recs, the records converted to DMap format
        """

        recs = []
        for k, v in self._borealis_records.items():
            shaped_data = {}
            # correlation_descriptors are num_beams, num_ranges, num_lags
            # scale by the scale squared to make up for the multiply 
            # in correlation (integer max squared)
            shaped_data['main_acfs'] = v['main_acfs'].reshape(
                v['correlation_dimensions']).astype(
                np.complex128) * ((np.iinfo(np.int16).max**2) / \
                (v['data_normalization_factor']**2))

            if 'intf_acfs' in v.keys():
                shaped_data['intf_acfs'] = v['intf_acfs'].reshape(
                    v['correlation_dimensions']).astype(
                    np.complex128) * ((np.iinfo(np.int16).max**2) / \
                    (v['data_normalization_factor']**2))
            if 'xcfs' in v.keys():
                shaped_data['xcfs'] = v['xcfs'].reshape(
                    v['correlation_dimensions']).astype(
                    np.complex128) * ((np.iinfo(np.int16).max**2) / \
                    (v['data_normalization_factor']**2))

            # Borealis git tag version numbers. If not a tagged version,
            # then use 255.255
            if v['borealis_git_hash'][0] == 'v' and \
                    v['borealis_git_hash'][2] == '.':
                borealis_major_revision = v['borealis_git_hash'][1]
                borealis_minor_revision = v['borealis_git_hash'][3]
            else:
                borealis_major_revision = 255
                borealis_minor_revision = 255

            slice_id = os.path.basename(self.filename).split('.')[-3]

            for beam_index, beam in enumerate(v['beam_nums']):
                # this beam, all ranges lag 0
                lag_zero = shaped_data['main_acfs'][beam_index, :, 0]
                lag_zero[-10:] = shaped_data['main_acfs'][beam_index,-10:,-1] 
                lag_zero_power = (lag_zero.real**2 + lag_zero.imag**2)**0.5

                correlation_dict = {}
                for key in shaped_data:  
                    # num_ranges x num_lags (complex)
                    this_correlation = shaped_data[key][beam_index, :, :-1]
                    # set the lag0 to the alternate lag0 for the end of the 
                    # array (when interference of first pulse would occur)
                    this_correlation[-10:,0] = \
                        shaped_data[key][beam_index,-10:,-1] 
                    # shape num_beams x num_ranges x num_lags, now num_ranges 
                    # x num_lags-1 b/c alternate lag-0 combined with lag-0 
                    # (only used for last ranges)

                    # (num_ranges x num_lags, flattened)
                    flattened_data = np.array(this_correlation).flatten()

                    int_data = np.empty(
                        flattened_data.size * 2, dtype=np.float32)
                    int_data[0::2] = flattened_data.real
                    int_data[1::2] = flattened_data.imag
                    # num_ranges x num_lags x 2; num_lags is one less than 
                    # in Borealis file because Borealis keeps alternate lag0
                    new_data = int_data.reshape(
                        v['correlation_dimensions'][1], 
                        v['correlation_dimensions'][2]-1, 2)
                    # NOTE: Flattening happening in 
                    # convert_to_dmap_datastructures
                    # place the darn-style array in the dict
                    correlation_dict[key] = new_data

                record_dict = {
                    'radar.revision.major': np.int8(borealis_major_revision),
                    'radar.revision.minor': np.int8(borealis_minor_revision),
                    'origin.code': np.int8(100),  # indicating Borealis origin
                    'origin.time': datetime.utcfromtimestamp(
                        v['sqn_timestamps'][0]).strftime("%c"),
                    'origin.command': 'Borealis ' + v['borealis_git_hash'] + \
                        ' ' + v['experiment_name'],
                    'cp': np.int16(v['experiment_id']),
                    'stid': np.int16(code_to_stid[v['station']]),
                    'time.yr': np.int16(datetime.utcfromtimestamp(
                        v['sqn_timestamps'][0]).year),
                    'time.mo': np.int16(datetime.utcfromtimestamp(
                        v['sqn_timestamps'][0]).month),
                    'time.dy': np.int16(datetime.utcfromtimestamp(
                        v['sqn_timestamps'][0]).day),
                    'time.hr': np.int16(datetime.utcfromtimestamp(
                        v['sqn_timestamps'][0]).hour),
                    'time.mt': np.int16(datetime.utcfromtimestamp(
                        v['sqn_timestamps'][0]).minute),
                    'time.sc': np.int16(datetime.utcfromtimestamp(
                        v['sqn_timestamps'][0]).second),
                    'time.us': np.int32(datetime.utcfromtimestamp(
                        v['sqn_timestamps'][0]).microsecond),
                    'txpow': np.int16(-1),
                    'nave': np.int16(v['num_sequences']),
                    'atten': np.int16(0),
                    'lagfr': np.int16(v['first_range_rtt']),
                    'smsep': np.int16(1e6/v['rx_sample_rate']),
                    'ercod': np.int16(0),
                    # TODO: currently not implemented
                    'stat.agc': np.int16(0),
                    # TODO: currently not implemented
                    'stat.lopwr': np.int16(0),
                    # TODO: currently not implemented
                    'noise.search': np.float32(v['noise_at_freq'][0]),
                    # TODO: currently not implemented
                    'noise.mean': np.float32(0),
                    'channel': np.int16(slice_id),
                    'bmnum': np.int16(beam),
                    'bmazm': np.float32(v['beam_azms'][beam_index]),
                    'scan': np.int16(v['scan_start_marker']),
                    # no digital receiver offset or rxrise required in Borealis
                    'offset': np.int16(0),
                    'rxrise': np.int16(0),
                    'intt.sc': np.int16(math.floor(v['int_time'])),
                    'intt.us': np.int32(math.fmod(v['int_time'], 1.0) * 1e6),
                    'txpl': np.int16(v['tx_pulse_len']),
                    'mpinc': np.int16(v['tau_spacing']),
                    'mppul': np.int16(len(v['pulses'])),
                    # an alternate lag-zero will be given.
                    'mplgs': np.int16(v['lags'].shape[0] - 1),
                    'nrang': np.int16(v['correlation_dimensions'][1]),
                    'frang': np.int16(round(v['first_range'])),
                    'rsep': np.int16(round(v['range_sep'])),
                    # False is list is empty.
                    'xcf': np.int16(bool('xcfs' in v.keys())),
                    'tfreq': np.int16(v['freq']),
                    'mxpwr': np.int32(-1),
                    'lvmax': np.int32(20000),
                    'rawacf.revision.major': np.int32(1),
                    'rawacf.revision.minor': np.int32(0),
                    'combf': 'Converted from Borealis file: ' + \
                        self.filename + ' record ' + k + \
                        ' ; Number of beams in record: ' + \
                        str(len(v['beam_nums'])) + ' ; ' + \
                        v['experiment_comment'] + ' ; ' + v['slice_comment'],
                    'thr': np.float32(0),
                    'ptab': v['pulses'].astype(np.int16),
                    'ltab': v['lags'].astype(np.int16),
                    'pwr0': lag_zero_power.astype(np.float32),
                    # list from 0 to num_ranges
                    'slist': np.array(list(range(0, 
                        v['correlation_dimensions'][1]))).astype(np.int16),
                    'acfd': correlation_dict['main_acfs'],
                    'xcfd': correlation_dict['xcfs']
                }
                recs.append(record_dict)

        dmap_recs = dict2dmap(recs)
        return dmap_recs


def borealis_write_to_dmap(filename, dmap_filetype, dmap_filename):
    """
    Convert the borealis file to DARN dmap filetype.

    Parameters
    ----------
    filename: str
        Name of the file where Borealis hdf5 data is stored, to read from.
    dmap_filetype: str
        Type of DARN dmap filetype you would like to convert to. Possible
        types include 'iqdat' and 'rawacf'. Borealis 'bfiq' can be converted 
        to iqdat, and Borealis 'rawacf' can be converted to DARN rawacf.
    dmap_filename: str
        Name of the file that you want to save the DARN dmap file to. 

    Raises
    ------
    BorealisFileTypeError
    BorealisFieldMissingError
    BorealisExtraFieldError
    BorealisDataFormatTypeError
    BorealisConversionTypesError
    BorealisConvert2IqdatError
    BorealisConvert2RawacfError

    See Also
    --------
    BorealisConvert 
        Class that is used to convert
    BorealisRead
        BorealisConvert uses this
    DarnWrite
        BorealisConvert uses this
    """
    borealis_data = BorealisConvert(filename)
    pydarn_log.debug('Read the file {filename}'.format(filename=filename))
    dmap_filename = borealis_data.write_to_dmap(dmap_filetype, dmap_filename)

    pydarn_log.debug("Borealis file {filename} written to {dmap_filename} "
          "without errors.".format(filename=borealis_data.filename, 
                          dmap_filename=dmap_filename))    


def bfiq2darniqdat(filename, **kwargs):
    """
    Convert the borealis bfiq hdf5 file to DARN iqdat filetype.

    Parameters
    ----------
    filename: str
        Name of the file where Borealis bfiq hdf5 data is stored, to read from.
    dmap_filename: str
        Name of the file that you want to save the DARN dmap file to. 

    Raises
    ------
    BorealisFileTypeError
    BorealisFieldMissingError
    BorealisExtraFieldError
    BorealisDataFormatTypeError
    BorealisConversionTypesError
    BorealisConvert2IqdatError
    BorealisConvert2RawacfError
    ConvertFileOverWriteError

    See Also
    --------
    borealis_write_to_dmap
    """

    settings = {}

    # put dmap in place of hdf5 in each spot (usually just 1)
    dmap_filename = os.path.dirname(filename) + '/'
    basename_partials = os.path.basename(filename).split("hdf5")
    for num, basename_partial in enumerate(basename_partials):
        if num != len(basename_partials) - 1:
            dmap_filename += basename_partial + 'dmap'
        else: # last partial, no 'dmap' after.
            dmap_filename += basename_partial
    
    # set defaults
    settings['dmap_filename'] = dmap_filename
    settings.update(kwargs)

    # verify not converting to the same filename.
    if settings['dmap_filename'] == filename:
        raise ConvertFileOverWriteError(filename)
    
    borealis_write_to_dmap(filename, 'iqdat', settings['dmap_filename'])

    return settings['dmap_filename']


def rawacf2darnrawacf(filename, **kwargs):
    """
    Convert the borealis rawacf hdf5 file to DARN rawacf filetype.

    Parameters
    ----------
    filename: str
        Name of the file where Borealis rawacf hdf5 data is stored, to read from.
    dmap_filename: str
        Name of the file that you want to save the DARN dmap file to. 

    Raises
    ------
    BorealisFileTypeError
    BorealisFieldMissingError
    BorealisExtraFieldError
    BorealisDataFormatTypeError
    BorealisConversionTypesError
    BorealisConvert2IqdatError
    BorealisConvert2RawacfError
    ConvertFileOverWriteError

    See Also
    --------
    borealis_write_to_dmap
    """

    settings = {}

    # put dmap in place of hdf5 in each spot (usually just 1)
    dmap_filename = os.path.dirname(filename) + '/'
    basename_partials = os.path.basename(filename).split("hdf5")
    for num, basename_partial in enumerate(basename_partials):
        if num != len(basename_partials) - 1:
            dmap_filename += basename_partial + 'dmap'
        else: # last partial, no 'dmap' after.
            dmap_filename += basename_partial
    
    # set defaults
    settings['dmap_filename'] = dmap_filename
    settings.update(kwargs)

    # verify not converting to the same filename.
    if settings['dmap_filename'] == filename:
        raise ConvertFileOverWriteError(filename)
    
    borealis_write_to_dmap(filename, 'rawacf', settings['dmap_filename'])

    return settings['dmap_filename']