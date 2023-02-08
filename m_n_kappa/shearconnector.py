import abc

from .log import LoggerMethods

log = LoggerMethods(__name__)


class ShearConnector(abc.ABC):
    
    @abc.abstractproperty
    def load_slips(self):
        ...
        
        
class HeadedStuds(ShearConnector):
    pass 
    
