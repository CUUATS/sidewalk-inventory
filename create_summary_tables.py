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
]

CROSSWALK_FIELDS = [
    ('ScoreWidth', 'Crosswalk Width'),
    ('ScoreCrossSlope', 'Cross Slope'),
    ('ScoreCompliance', 'Compliance Score'),
]

def is_excluded(level):
    return ('exclude' in level and level['exclude'])

def is_hidden(level):
    return ('hidden' in level and level['hidden'])

def feature_table(query_set, summary_field, column_label, feature_label):
    levels = query_set.summarize(summary_field)
    total = sum([l['count'] for l in levels if not is_excluded(l)])

    results = [
        [
            column_label,
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

        results.append([
            level['label'],
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
        results.append([
            level['label'],
            str(level['value']),
            '{:.1f}'.format(level['length']),
            '{:.1f} %'.format(100*level['length']/total_length),
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
ss = SidewalkSegment.objects.filter(SummaryCount=1)
for (field, label) in SIDEWALK_SEGMENT_FIELDS:
    results['Sidewalk'][field] = sidewalk_table(ss, field, label)

# Create curb ramp tables.
cr = CurbRamp.objects.filter(QAStatus=D('Complete')).exclude(RampType=D('None'))
for (field, label) in CURB_RAMP_FIELDS:
    results['CurbRamp'][field] = feature_table(cr, field, label, 'Curb Ramps')

# Create crosswalk tables.
cw = Crosswalk.objects.filter(QAStatus=D('Complete'))
for (field, label) in CROSSWALK_FIELDS:
    results['Crosswalk'][field] = feature_table(cw, field, label, 'Crosswalks')

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
