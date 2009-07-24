"""setup all things exported from FCM
"""

from core import FCMdata
from core import Gate, points_in_poly
from core import BadFCMPointDataTypeError, UnimplementedFcsDataMode
from core import CompensationError
from io import FCSreader, loadFCS
from core  import logicle, hyperlog

__all__ == [
            #Objects
            'FCMdata',
            'Gate',
            'FCSreader',
            #Exceptions
            'BadFCMPointDataTypeError',
            'UnimplementedFcsDataMode',
            'CompensationError',
            #functions
            'logicle',
            'hyperlog',
            'points_in_poly',
            'loadFCS'
            ]