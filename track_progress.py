import datetime
import re
from prettytable import PrettyTable
from cuuats.datamodel import DataSource
from datamodel import Sidewalk, CurbRamp, Crosswalk, PedestrianSignal, \
    SidewalkSegment
from production import DATA_PATH, SW_NAME, CR_NAME, CW_NAME, PS_NAME, SS_NAME, \
    SEGMENT_CSV, QASTATUS_CSV

date_string = datetime.date.today().strftime('%m/%d/%Y')

ds = DataSource(DATA_PATH)
Sidewalk.register(ds, SW_NAME)
CurbRamp.register(ds, CR_NAME)
Crosswalk.register(ds, CW_NAME)
PedestrianSignal.register(ds, PS_NAME)
SidewalkSegment.register(ds, SS_NAME)

# Calculate the percentage of segment length that is "complete."
length_sum = [('Shape.STLength()', 'SUM')]
sum_key = 'SUM_Shape_STLength__'
all_seg = SidewalkSegment.objects.all()
ft_total = all_seg.aggregate(length_sum)[sum_key]
ft_complete = all_seg.filter(summary_count=1).aggregate(length_sum)[sum_key]
pct_string = '%0.02f' % (100 * ft_complete / ft_total)
print '%s percent of sidewalk segments have been collected' % (pct_string,)

with open(SEGMENT_CSV, 'a') as progress:
    progress.write('%s,%s\n' % (date_string, pct_string))

# Calculate the QA Status breakdown for each feature type.
qastatus_cv = sorted(ds.get_domain('QAStatus').codedValues.items())
qastatus_keys = [cv[0] for cv in qastatus_cv]
qastatus_values = [cv[1] for cv in qastatus_cv]
qastatus_headers = [re.sub(r'[^A-Z]', '', s) for s in qastatus_values]
qastatus_table = PrettyTable(['Feature'] + qastatus_headers + ['Count'])
qastatus_row = [date_string]

for fc in [Sidewalk, CurbRamp, Crosswalk, PedestrianSignal]:
    counts = [fc.objects.filter(QAStatus=status).count() for status
              in qastatus_keys]
    total = fc.objects.all().count()
    pcts = ['%0.1f%%' % (100*float(c)/float(total),) for c in counts]
    qastatus_table.add_row([fc.name] + pcts + [total])
    qastatus_row.extend(counts + [total])

print qastatus_table

with open(QASTATUS_CSV, 'a') as progress:
    progress.write('%s\n' % (','.join([str(v) for v in qastatus_row]),))
