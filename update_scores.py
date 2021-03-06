"""
Update scores for Sidewalk Inventory and Assessment features.
"""

from datamodel import Sidewalk, CurbRamp, Crosswalk, PedestrianSignal, \
    SidewalkSegment, D
from config import SW_PATH, CR_PATH, CW_PATH, PS_PATH, SS_PATH
from utils import display_progress

# Register features.
Sidewalk.register(SW_PATH)
CurbRamp.register(CR_PATH)
Crosswalk.register(CW_PATH)
PedestrianSignal.register(PS_PATH)
SidewalkSegment.register(SS_PATH)

# Perform scoring.
print 'Scoring features...'
with SidewalkSegment.workspace.edit():
    sidewalk_segments = SidewalkSegment.objects.prefetch_related(
        'sidewalk_set')
    for feature in display_progress(sidewalk_segments, 'Sidewalks'):
        feature.update_sidewalk_fields()
        feature.save()

with CurbRamp.workspace.edit():
    curb_ramps = CurbRamp.objects.exclude(RampType=D('None'))
    for cr in display_progress(curb_ramps, 'Curb Ramps'):
        cr.save()

with Crosswalk.workspace.edit():
    for cw in display_progress(Crosswalk.objects.all(), 'Crosswalks'):
        cw.save()

with PedestrianSignal.workspace.edit():
    for ps in display_progress(
            PedestrianSignal.objects.all(), 'Pedestrian Signals'):
        ps.save()
