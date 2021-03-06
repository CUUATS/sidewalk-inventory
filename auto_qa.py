"""
Automatic quality assurance for Sidewalk Inventory and Assessment data.
"""

import argparse
from cuuats.datamodel import D
from datamodel import Sidewalk, CurbRamp, Crosswalk, PedestrianSignal, \
    SidewalkSegment
from config import SW_PATH, CR_PATH, CW_PATH, PS_PATH, SS_PATH, \
    SS_REL_NAME
from utils import display_progress

PREFETCH_RELS = {
    'CurbRamp': ['attachments'],
}

# Parse command line arguments.
parser = argparse.ArgumentParser('Automatic QA for sidewalk inventory data.')
parser.add_argument('--no-rels', action='store_true', dest='no_rels',
                    help='skip updating relationship fields')
args = parser.parse_args()

# Register feature classes.
Sidewalk.register(SW_PATH)
CurbRamp.register(CR_PATH)
Crosswalk.register(CW_PATH)
PedestrianSignal.register(PS_PATH)
SidewalkSegment.register(SS_PATH)

feature_classes = {
    'Sidewalks': Sidewalk,
    'Curb Ramps': CurbRamp,
    'Crosswalks': Crosswalk,
    'Pedestrian Signals': PedestrianSignal,
}

results = []

print 'Performing auto QA...'
for label, feature_class in feature_classes.items():
    update_count = 0

    # Don't update deferred features or those requiring staff review.
    features = feature_class.objects.exclude(
        QAStatus__in=[D('Needs Staff Review'), D('Deferred')])

    if feature_class.__name__ in PREFETCH_RELS:
        rels = PREFETCH_RELS[feature_class.__name__]
        features = features.prefetch_related(*rels)

    with feature_class.workspace.edit():
        for feature in display_progress(features, label):
            feature.perform_qa()
            feature.assign_staticid()
            update_count += int(feature.save())

    results.append('%s: Updated %i rows' % (label, update_count))

if not args.no_rels:
    # Update the nearest sidewalk segment relationship.
    print 'Updating nearest sidewalk segment...'
    with SidewalkSegment.workspace.edit():
        SidewalkSegment.workspace.update_spatial_relationship(
            SS_REL_NAME, 'CLOSEST', 25)

    # Update segment fields based on the nearest segment relationship.
    print 'Updating sidewalk segment statistics...'
    update_count = 0
    segments = SidewalkSegment.objects.prefetch_related('sidewalk_set')
    with SidewalkSegment.workspace.edit():
        for segment in display_progress(segments, 'Sidewalk Segments'):
            segment.update_sidewalk_fields()
            update_count += int(segment.save())
    results.append('%s: Updated %i rows' % ('Sidewalk Segments', update_count))

# Print results.
for row in results:
    print row
