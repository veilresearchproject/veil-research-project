"""Update 1: validated configuration for the demo."""
from dataclasses import dataclass
from typing import Mapping
CHANNELS=('temperature_c','humidity_pct','sound_db')
@dataclass(frozen=True)
class Profile:
    name:str
    thresholds:Mapping[str,tuple[float,float]]
    interval_seconds:int=10
    def __post_init__(self):
        if not self.name.strip() or not 1<=self.interval_seconds<=3600: raise ValueError('Invalid profile')
        if set(self.thresholds)!=set(CHANNELS): raise ValueError('Unexpected channels')
        for lo,hi in self.thresholds.values():
            if not -10000<lo<hi<10000: raise ValueError('Invalid range')
DEFAULT=Profile('synthetic-lab-v0.2',{'temperature_c':(18,26),'humidity_pct':(25,65),'sound_db':(0,65)})
