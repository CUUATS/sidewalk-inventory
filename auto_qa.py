"""
Automatic quality assurance for Sidewalk Inventory and Assessment data.
"""

import argparse
from cuuats.datamodel import DataSource
from datamodel import Sidewalk, CurbRamp, Crosswalk, PedestrianSignal, \
    SidewalkSegment
from production import DATA_PATH, SW_NAME, CR_NAME, CW_NAME, PS_NAME, SS_NAME

PREFETCH_RELS = {
    'CurbRamp': ['attachments'],
}

# Parse command line arguments.
parser = argparse.ArgumentParser('Automatic QA for sidewalk inventory data.')
parser.add_argument('--no-rels', action='store_true', dest='no_rels',
                    help='skip updating relationship fields')
args = parser.parse_args()

# Register feature classes.
ds = DataSource(DATA_PATH)
Sidewalk.register(ds, SW_NAME)
CurbRamp.register(ds, CR_NAME)
Crosswalk.register(ds, CW_NAME)
PedestrianSignal.register(ds, PS_NAME)
SidewalkSegment.register(ds, SS_NAME)

feature_classes = [
    Sidewalk,
    CurbRamp,
    Crosswalk,
    PedestrianSignal
]

print 'Performing auto QA...'
# Don't update deferred features or those requiring staff review.
staff_review = ds.get_coded_value('QAStatus', 'Needs Staff Review')
deferred = ds.get_coded_value('QAStatus', 'Deferred')

for feature_class in feature_classes:
    update_count = 0
    features = feature_class.objects.exclude(
        QAStatus__in=[staff_review, deferred])

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
    ds.set_nearest('SidewalkNearestSegment', 25, update=True)

    # Update segment fields based on the nearest segment relationship.
    print 'Updating sidewalk segment statistics...'
    update_count = 0
    for segment in SidewalkSegment.objects.prefetch_related('sidewalk_set'):
        segment.update_sidewalk_fields()
        update_count += int(segment.save())
    print '%s: Updated %i rows' % (SidewalkSegment.name, update_count)
