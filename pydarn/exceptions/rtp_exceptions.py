# Authors: Marina Schmidt
import logging
import datetime
pydarn_log = logging.getLogger('pydarn')


class RTPIncorrectPlotMethodError(Exception):
    """
    This error is raised when the incorrect plotting
    method is called for a given parameter
    """
    def __init__(self, parameter: str, data_type: str):
        self.parameter = parameter
        self.data_type = data_type
        self.message = "Error: Incorrect RTP method is being called for"\
            " {parameter} of type {data_type}. plot_range_time is for"\
            " array data types, and plot_time_series is for scalar"\
            " data types.".format(parameter=self.parameter,
                                  data_type=self.data_type)
        super().__init__(self.message)
        pydarn_log.error(self.message)


class RTPNoDataFoundError(Exception):
    """
    This error is raised when the incorrect plotting
    method is called for a given parameter
    """
    def __init__(self, parameter: str, beam_num: int, start_time: int,
                 end_time: datetime.datetime, opt_beam_num: int):
        self.parameter = parameter
        self.beam_num = beam_num
        self.start_time = start_time
        self.end_time = end_time
        self.message = "There is no Data for beam number {beam_num}"\
            " for the parameter type {parameter} between the"\
            " time range {start_time} to"\
            " {end_time}. Try another beam, for example: {opt_beam}"\
            " or another parameter for the given time range."\
            "".format(parameter=self.parameter,
                      beam_num=self.beam_num,
                      opt_beam=opt_beam_num,
                      start_time=self.start_time.strftime("%Y %m"
                                                          " %d %H"
                                                          ":%M"),
                      end_time=self.end_time.strftime("%Y %m"
                                                      " %d %H:%M"))
        super().__init__(self.message)
        pydarn_log.error(self.message)


class RTPInfinityError(Exception):
    """
    This error is raised when zmin or zmax is set to infinity causing
    the colorbar scale to break
    """
    def __init__(self, parameter: str, beam_num: int, boundary: str,
                 boundary_value: float):
        self.parameter = parameter
        self.beam_num = beam_num
        self.boundary = boundary
        self.boundary_value = boundary_value
        self.message = "{boundary} is set to {value} for parameter {param}"\
                " and beam number {beam}, please use zmin or zmax"\
                " options to set lower or upper"\
                " boundary.".format(boundary=self.boundary,
                                    value=self.boundary_value,
                                    param=self.parameter,
                                    beam=self.beam_num)
        super().__init__(self.message)
        pydarn_log.error(self.message)


class RTPZeroError(Exception):
    """
    Error raised when a ZeroDivisionError is raised due to minimum - maximum
    range cause mathematical errors in the plotting. An example of this is
    when pwr0 is plotted, some files will have a pwr0=0 which will cause
    a ZeroDivisionError using logNorm as the normalization method. This
    cannot be avoided and challenging to detect which normalization method
    is passed in. Thus error will be raised to let the user know to change
    the range or normalization method to fix the problem.
    """
    def __init__(self, parameter: str, beam_num: int, zmin: float, zmax: float,
                 norm):
        self.parameter = parameter
        self.beam_num = beam_num
        self.zmin = zmin
        self.zmax = zmax
        self.norm = norm
        self.message = "ZeroDivisionError or ValueError is raised "\
            "due to trying to normalize {zmin} to {zmax} using the {norm} "\
            "method for the parameter {param} at beam {num}. "\
            "This can be an issue with the data file, fields meaning"\
            " something different. To resolve this error, please set the "\
            "zmin or zmax parameter or try another normalization"\
            " method.".format(zmin=zmin, zmax=zmax, norm=norm,
                             num=beam_num, param=parameter)
        super().__init__(self.message)
        pydarn_log.error(self.message)


class RTPUnknownParameter(Exception):
    """
    Error raised when the parameter is not found in the data passed in
    """
    def __init__(self, parameter: str):
        self.parameter = parameter
        self.message = "Error: The following parameter was not found in the"\
            " data set. Please make sure it is typed correctly or"\
            " you are using the correct data."
        super().__init__(self.message)
        pydarn_log.error(self.message)
