import argparse
import csv
import json
import os
from cuuats.datamodel import D
from datamodel import CurbRamp, Crosswalk, PedestrianSignal, SidewalkSegment
from debug import CR_PATH, CW_PATH, PS_PATH, SS_PATH

CurbRamp.register(CR_PATH)
Crosswalk.register(CW_PATH)
PedestrianSignal.register(PS_PATH)
SidewalkSegment.register(SS_PATH)

SIDEWALK_SEGMENT_FIELDS = [
    ('ScoreMaxCrossSlope', 'Maximum Cross Slope'),
    ('ScoreLargestVerticalFault', 'Largest Vertical Fault'),
    ('ScoreObstructionTypes', 'Number of Obstruction Types'),
    ('ScoreWidth', 'Minimum Sidewalk Width'),
]

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
            '%.1f' % (level['length'],),
            '%.1f %%' % (100*level['length']/total_length,),
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

# Create the output file or files.
if args.format == 'json':
    with open(args.output, 'wb') as output_file:
        json.dump(results, output_file)
else:
    for (feature_type, tables) in results.items():
        for (var_name, table) in tables.items():
            output_path = os.path.join(
                args.output, feature_type + var_name + '.csv')
            with open(output_path, 'wb') as output_file:
                writer = csv.writer(output_file)
                writer.writerows(table)
