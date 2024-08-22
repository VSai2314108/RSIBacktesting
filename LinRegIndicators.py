from AlgorithmImports import *
import numpy as np
import math
from typing import List, Optional

class LinReg(PythonIndicator):
    def __init__(self, period: int):
        self.Period: int = period
        self.Slope: Optional[float] = None
        self.Intercept: Optional[float] = None
        self.Values: List[float] = []
        self.Value = 0

    @property
    def IsReady(self) -> bool:
        return self.Slope is not None and self.Intercept is not None

    def update(self, input: IBaseData) -> bool:  # Changed parameter type to IBaseData
        self.Values.append(input.value)  # Assuming input has a Value attribute
        if len(self.Values) > self.Period:
            del self.Values[0]
            
        if len(self.Values) == self.Period:
            x = np.arange(1, self.Period + 1)
            y = np.array(self.Values)

            slope, intercept = np.polyfit(x, y, 1)
            self.Slope = slope
            self.Intercept = intercept
            
            self.Value: float = intercept + (slope * (self.Period-1))
            
        return True
        
class SlopeIndicator(PythonIndicator):
    def __init__(self, linRegPer: int, slopePer: int, longThresh: float, shortThresh: float):
        self.linReg: LinReg = LinReg(linRegPer)
        self.warm_up_period: int = linRegPer + slopePer
        self.slopePer: int = slopePer
        self.linRegValues: List[float] = []
        self.linRegPredValues: List[float] = []
        self.Slope: Optional[float] = None
        self.Deg: Optional[float] = None
        self.longThresh: float = longThresh
        self.shortThresh: float = shortThresh
        self.Signal: Optional[int] = None
        self.Value = 0
    
    @property
    def IsReady(self) -> bool:
        return self.Slope is not None
    
    def update(self, input: IBaseData) -> bool:  # Changed parameter type to IBaseData
        self.linReg.update(input)  # Pass IBaseData to LinReg
        if not self.linReg.IsReady:
            return False
        
        self.linRegValues.append(self.linReg.Slope)
        self.linRegPredValues.append(self.linReg.Value)
        if len(self.linRegValues) > self.slopePer:
            del self.linRegValues[0]

        if len(self.linRegValues) == self.slopePer:
            self.Slope = (self.linRegValues[-1] - self.linRegValues[0])/(self.slopePer-1)
            self.Deg = math.degrees(math.atan(self.Slope))
            self.Signal = 1 if self.Deg > self.longThresh else (-1 if self.Deg < self.shortThresh else 0)
            self.Value = self.Signal
        return True