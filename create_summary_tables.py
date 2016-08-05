from cuuats.datamodel import D
from datamodel import CurbRamp, Crosswalk, PedestrianSignal, SidewalkSegment
from debug import CR_PATH, CW_PATH, PS_PATH, SS_PATH

CurbRamp.register(CR_PATH)
Crosswalk.register(CW_PATH)
PedestrianSignal.register(PS_PATH)
SidewalkSegment.register(SS_PATH)

ss = SidewalkSegment.objects.filter(SummaryCount=1)
ss.summarize('ScoreWidth', length='Shape.getLength("PLANAR", "MILES")')
