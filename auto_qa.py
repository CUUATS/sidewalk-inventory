"""
Automatic quality assurance for Sidewalk Inventory and Assessment data.
"""

import argparse
from cuuats.datamodel import D
from datamodel import Sidewalk, CurbRamp, Crosswalk, PedestrianSignal, \
    SidewalkSegment
from production import SW_PATH, CR_PATH, CW_PATH, PS_PATH, SS_PATH

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

feature_classes = [
    Sidewalk,
    CurbRamp,
    Crosswalk,
    PedestrianSignal
]

print 'Performing auto QA...'
for feature_class in feature_classes:
    update_count = 0

    # Don't update deferred features or those requiring staff review.
    features = feature_class.objects.exclude(
        QAStatus__in=[D('Needs Staff Review'), D('Deferred')])

    if feature_class.__name__ in PREFETCH_RELS:
        rels = PREFETCH_RELS[feature_class.__name__]
        features = features.prefetch_related(*rels)

    for feature in features:
        feature.perform_qa()
        feature.assign_staticid()
        update_count += int(feature.save())

    print '%s: Updated %i rows' % (feature_class.name, update_count)

if not args.no_rels:
    # Update the nearest sidewalk segment relationship.
    print 'Updating nearest sidewalk segment...'
    SidewalkSegment.workspace.set_nearest(
        'SidewalkNearestSegment', 25, update=True)

    # Update segment fields based on the nearest segment relationship.
    print 'Updating sidewalk segment statistics...'
    update_count = 0
    for segment in SidewalkSegment.objects.prefetch_related('sidewalk_set'):
        segment.update_sidewalk_fields()
        update_count += int(segment.save())
    print '%s: Updated %i rows' % (SidewalkSegment.name, update_count)
