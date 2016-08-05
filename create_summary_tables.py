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

results = {
    'Sidewalk': {},
    'Crosswalk': {},
    'CurbRamp': {},
    'PedestrianSignal': {}
}

ss = SidewalkSegment.objects.filter(SummaryCount=1)
for (field, label) in SIDEWALK_SEGMENT_FIELDS:
    results['Sidewalk'][field] = sidewalk_table(ss, field, label)
