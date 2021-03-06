from __future__ import print_function

from .gotmtext import *
from .netcdf import *
from .hdf4 import *

def open(paths):
    store = None
    try:
        store = xmlplot.data.NetCDFStore.loadUnknownConvention(paths)
    except xmlplot.data.NetCDFError as e:
        try:
            store = xmlplot.data.HDF4Store(paths)
        except:
            raise e
    return store
