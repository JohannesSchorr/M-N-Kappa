import abc


class ShearConnector(abc.ABC):
    
    @abc.abstractproperty
    def load_slips(self):
        ...
        
        
class HeadedStuds(ShearConnector):
    pass 
    
