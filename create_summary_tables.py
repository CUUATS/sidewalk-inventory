import argparse
import csv
import json
import os
from cuuats.datamodel import D
from datamodel import CurbRamp, Crosswalk, PedestrianSignal, SidewalkSegment
from debug import CR_PATH, CW_PATH, PS_PATH, SS_PATH

SIDEWALK_SEGMENT_FIELDS = [
    ('ScoreMaxCrossSlope', 'Maximum Cross Slope'),
    ('ScoreLargestVerticalFault', 'Largest Vertical Fault'),
    ('ScoreObstructionTypes', 'Number of Obstruction Types'),
    ('ScoreWidth', 'Minimum Sidewalk Width'),
    ('ScoreCompliance', 'Compliance Score'),
    ('ScoreSurfaceCondition', 'Condition Issue'),
    ('ScoreVerticalFaultCount', 'Vertical Faults per Mile'),
    ('ScoreCrackedPanelCount', 'Percent Cracked Panels'),
    ('ScoreCondition', 'Condition Score'),
]

CURB_RAMP_FIELDS = [
    ('ScoreRampWidth', 'Ramp Width'),
    ('ScoreRampCrossSlope', 'Cross Slope'),
    ('ScoreRampRunningSlope', 'Running Slope'),
    ('ScoreDetectableWarningType', 'Surface Type'),
    ('ScoreDetectableWarningWidth', 'Percent of Ramp or Landing Width'),
    ('ScoreGutterCrossSlope', 'Cross Slope'),
    ('ScoreGutterRunningSlope', 'Running Slope'),
    ('ScoreLandingDimensions', 'Minimum Dimension'),
    ('ScoreLandingSlope', 'Maximum Slope'),
    ('ScoreApproachCrossSlope', 'Maximum Cross Slope'),
    ('ScoreFlareSlope', 'Flare Slope'),
    ('ScoreLargestPavementFault', 'Largest Vertical Fault'),
    ('ScoreObstruction', 'Presence of Obstruction'),
    ('ScoreCompliance', 'Compliance Score'),
    ('ScoreSurfaceCondition', 'Condition Issue'),
    ('ScorePavementFaultCount', 'Vertical Faults'),
    ('ScoreCrackedPanelCount', 'Cracked Panels'),
    ('ScoreCondition', 'Condition Score'),
]

CROSSWALK_FIELDS = [
    ('ScoreWidth', 'Crosswalk Width'),
    ('ScoreCrossSlope', ['Stop-Controlled', 'Uncontrolled']),
    ('ScoreCompliance', 'Compliance Score'),
]

PEDESTRIAN_SIGNAL_FIELDS = [
    ('ScoreButtonSize', 'Button Diameter'),
    ('ScoreButtonHeight', 'Button Height'),
    ('ScoreCompliance', 'Compliance Score'),
]

BUTTON_POSITION_APPEARANCE_FIELDS = [
    ('ButtonSpacing', 15, 'Pushbuttons at least 10 feet apart'),
    ('ButtonOffsetFCurb', 15, 'Pushbuttons within 10 feet of curb'),
    ('AllWeatherSurface', 15, 'All-weather surface adjacent to button'),
    ('HighContrastButton', 25, 'High contrast button'),
    ('LocatorTone', 30, 'Locator tone to find button'),
]

TACTILE_FEATURES_FIELDS = [
    ('TactileArrowPresent', 50, 'Tactile arrow'),
    ('VibrotactileSignal', 50, 'Vibrotactile signal or button'),
]

def is_excluded(level):
    return ('exclude' in level and level['exclude'])

def is_hidden(level):
    return ('hidden' in level and level['hidden'])

def merge_levels(levels, groups):
    included = [l for l in levels if not is_excluded(l)]
    excluded = [l for l in levels if is_excluded(l)]

    assert len(included) % groups == 0

    size = len(levels) / groups
    columns = [included[(size*i):(size*(i+1))] for i in xrange(groups)]
    new_levels = []

    for row in zip(*columns):
        new_level = {
            'value': row[0]['value'],
            'count': sum([l['count'] for l in row]),
            'label': [l['label'] for l in row],
        }

        for key in row[0].keys():
            if not key in new_level:
                new_level[key] = sum([l[key] for l in row])

        new_levels.append(new_level)

    for level in excluded:
        new_level = {}
        new_level.update(level)
        new_level['label'] = [level['label']] + ([''] * (groups - 1))
        new_levels.append(new_level)

    return new_levels

def feature_table(query_set, summary_field, column_labels, feature_label):
    levels = query_set.summarize(summary_field)
    total = sum([l['count'] for l in levels if not is_excluded(l)])

    if not isinstance(column_labels, (list, tuple)):
        column_labels = [column_labels]

    if len(column_labels) > 1:
        levels = merge_levels(levels, len(column_labels))

    results = [
        column_labels + [
            'Score',
            feature_label,
            'Percent of %s' % (feature_label,),
        ]
    ]

    for level in levels:
        if is_hidden(level):
            continue

        percent = unichr(2014)
        if not is_excluded(level):
            percent = '{:.1f} %'.format(100*float(level['count'])/total)

        label = level['label']
        if not isinstance(label, (list, tuple)):
            label = [label]

        results.append(label + [
            str(level['value']),
            '{:,d}'.format(level['count']),
            percent,
        ])

    if all(l['value'] is None for l in levels):
        results = [r[:1] + r[2:] for r in results]

    return results

def sidewalk_table(query_set, summary_field, column_label):
    levels = query_set.summarize(
        summary_field, length='Shape.getLength("PLANAR", "MILES")')
    total_length = sum([l['length'] for l in levels])

    results = [
        [column_label, 'Score', 'Miles of Sidewalk', 'Percent of Total Length']
    ]

    for level in levels:
        if is_hidden(level):
            continue

        results.append([
            level['label'],
            str(level['value']),
            '{:.1f}'.format(level['length']),
            '{:.1f} %'.format(100*level['length']/total_length),
        ])

    if all(l['value'] is None for l in levels):
        results = [r[:1] + r[2:] for r in results]

    return results

def yes_table(query_set, fields, column_label):
    total = query_set.count()

    results = [
        [
            column_label,
            'Score',
            'Pedestrian Signals',
            'Percent of Pedestrian Signals',
        ]
    ]

    for (field_name, value, label) in fields:
        count = sum(
            [int(getattr(f, field_name) == D('Yes')) for f in query_set])

        results.append([
            label,
            str(value),
            '{:,d}'.format(count),
            '{:.1f} %'.format(100*float(count)/total),
        ])

    return results

# Parse command line arguments.
parser = argparse.ArgumentParser(
    'Create summary tables for sidewalk network features.')
parser.add_argument('-f', '--format', dest='format', default='json',
                    choices=['csv', 'json'], help='format of outpot')
parser.add_argument('output', help='output file or location')
args = parser.parse_args()

# Verify the output location.
if args.format == 'csv':
    assert os.path.isdir(args.output), \
        'Output location must be a directory for CSV format'
else:
    assert os.path.isdir(os.path.dirname(args.output)), \
        'Invalid output location'

# Register feature classes
CurbRamp.register(CR_PATH)
Crosswalk.register(CW_PATH)
PedestrianSignal.register(PS_PATH)
SidewalkSegment.register(SS_PATH)

# Prepare the results dictionary.
results = {
    'Sidewalk': {},
    'Crosswalk': {},
    'CurbRamp': {},
    'PedestrianSignal': {}
}

# Create sidewalk tables.
print 'Creating sidewalk summary tables...'
ss = SidewalkSegment.objects.filter(SummaryCount=1)
for (field, label) in SIDEWALK_SEGMENT_FIELDS:
    results['Sidewalk'][field] = sidewalk_table(ss, field, label)

# Create curb ramp tables.
print 'Creating curb ramp summary tables...'
cr = CurbRamp.objects.filter(QAStatus=D('Complete')).exclude(RampType=D('None'))
for (field, label) in CURB_RAMP_FIELDS:
    results['CurbRamp'][field] = feature_table(cr, field, label, 'Curb Ramps')

# Create crosswalk tables.
print 'Creating crosswalk summary tables...'
cw = Crosswalk.objects.filter(QAStatus=D('Complete'))
for (field, label) in CROSSWALK_FIELDS:
    results['Crosswalk'][field] = feature_table(cw, field, label, 'Crosswalks')

# Create pedestrian signal tables.
print 'Creating pedestrian signal summary tables...'
ps = PedestrianSignal.objects.filter(QAStatus=D('Complete'))
for (field, label) in PEDESTRIAN_SIGNAL_FIELDS:
    results['PedestrianSignal'][field] = feature_table(
        ps, field, label, 'Pedestrian Signals')

results['PedestrianSignal']['ScoreButtonPositionAppearance'] = yes_table(
    ps, BUTTON_POSITION_APPEARANCE_FIELDS, 'Button Position and Appearance')

results['PedestrianSignal']['ScoreTactileFeatures'] = yes_table(
    ps, TACTILE_FEATURES_FIELDS, 'Tactile Features')

# Create the output file or files.
if args.format == 'json':
    with open(args.output, 'wb') as output_file:
        json.dump(results, output_file, indent=4)
else:
    for (feature_type, tables) in results.items():
        for (var_name, table) in tables.items():
            output_path = os.path.join(
                args.output, feature_type + var_name + '.csv')
            with open(output_path, 'wb') as output_file:
                writer = csv.writer(output_file)
                writer.writerows(table)
