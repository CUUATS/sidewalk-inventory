"""
Analysis for Sidewalk Inventory and Assessment data.
"""

from datamodel import Sidewalk, CurbRamp, Crosswalk, PedestrianSignal, \
    SidewalkSegment, TrafficAnalysisZone, SidewalkTAZSummary, D
from production import SW_PATH, CR_PATH, CW_PATH, PS_PATH, SS_PATH, TAZ_PATH, \
    STAZS_PATH
from utils import display_progress

TAZ_VINTAGE = 2011

# Register features.
Sidewalk.register(SW_PATH)
CurbRamp.register(CR_PATH)
Crosswalk.register(CW_PATH)
PedestrianSignal.register(PS_PATH)
SidewalkSegment.register(SS_PATH)
TrafficAnalysisZone.register(TAZ_PATH)
SidewalkTAZSummary.register(STAZS_PATH)

# Perform scoring.
print 'Scoring features...'
sidewalk_segments = SidewalkSegment.objects.prefetch_related('sidewalk_set')
for feature in display_progress(sidewalk_segments, 'Sidewalks'):
    feature.update_sidewalk_fields()
    feature.save()

curb_ramps = CurbRamp.objects.exclude(RampType=D('None'))
for cr in display_progress(curb_ramps, 'Curb Ramps'):
    cr.save()

for cw in display_progress(Crosswalk.objects.all(), 'Crosswalks'):
    cw.save()

for ps in display_progress(
        PedestrianSignal.objects.all(), 'Pedestrian Signals'):
    ps.save()

# Update TAZ relationships.
print 'Updating TAZ relationships...'
workspace = Sidewalk.workspace
workspace.update_spatial_relationship(
    'SidewalkSegmentTAZ', 'HAVE_THEIR_CENTER_IN')
workspace.update_spatial_relationship('CurbRampTAZ', 'WITHIN')
workspace.update_spatial_relationship('CrosswalkTAZ', 'WITHIN')
workspace.update_spatial_relationship('PedestrianSignalTAZ', 'WITHIN')

# Summarize results by TAZ.
print 'Summarizing results by TAZ...'
tazs = TrafficAnalysisZone.objects.filter(
    Vintage=TAZ_VINTAGE).prefetch_related(
        'sidewalksegment_set', 'curbramp_set', 'crosswalk_set',
        'pedestriansignal_set')
for taz in display_progress(tazs, 'TAZs'):
    summary = taz.summary
    summary.update_sidewalk_segments(taz)
    summary.update_curb_ramps(taz)
    summary.update_crosswalks(taz)
    summary.update_pedestrian_signals(taz)
    summary.save()
