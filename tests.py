"""
Sidewalk Inventory and Assessment tests.
"""

import unittest
from cuuats.datamodel import D
from datamodel import Sidewalk, CurbRamp, Crosswalk, PedestrianSignal, \
    SidewalkSegment
from debug import SW_PATH, CR_PATH, CW_PATH, PS_PATH, SS_PATH

CROSS_SLOPE_VALUES = [
    (0, 2.0), (2.1, 4.0), (4.1, 6.0), (6.1, 8.0), (8.1, 10.0), (10.1, 100.0)]
CROSS_SLOPE_SCORES = [100, 80, 60, 40, 20, 0]

LARGEST_VFAULT_VALUES = [1, 2, 3, 100, 101]
LARGEST_VFAULT_SCORES = [50, 0, 100, 100, 100]

WIDTH_VALUES = [(48, 100), (45, 47), (42, 44), (39, 41), (36, 38), (35, 0)]
WIDTH_SCORES = [100, 80, 60, 40, 20, 0]

IN_MEDIAN_WIDTH_VALUES = [
    (60, 100), (57, 59), (54, 56), (51, 53), (48, 50), (47, 0)]
IN_MEDIAN_WIDTH_SCORES = [100, 80, 60, 40, 20, 0]

RAMP_RUNNING_SLOPE_VALUES = [(8.3, 0), (8.4, 9.3), (9.4, 10.3), (10.4, 50)]
RAMP_RUNNING_SLOPE_SCORES = [100, 67, 33, 0]

DWS_TYPE_VALUES = [
    D('Pavement Grooves'),
    D('Other'),
    D('None'),
    D('N/A'),
    D('Truncated Domes - YELLOW'),
    D('Truncated Domes - RED'),
    D('Truncated Domes - OTHER'),
]
DWS_TYPE_SCORES = [50, 50, 0, 0, 100, 100, 100]

Sidewalk.register(SW_PATH)
CurbRamp.register(CR_PATH)
Crosswalk.register(CW_PATH)
PedestrianSignal.register(PS_PATH)
SidewalkSegment.register(SS_PATH)


class BaseTestFeature(object):

    def _test_scores(self, value_field, score_field, values, scores):
        for value, score in zip(values, scores):
            if not isinstance(value, (list, tuple)):
                value = [value]
            for v in value:
                setattr(self.feature, value_field, v)
                actual_score = getattr(self.feature, score_field)
                self.assertEqual(
                    actual_score, score,
                    '%s: %s for %s = %s should be %s, not %s' % (
                        self.feature.__class__.__name__,
                        score_field, value_field, str(v),
                        str(score), str(actual_score)))


class TestSidewalkSegment(unittest.TestCase, BaseTestFeature):

    def setUp(self):
        self.feature = SidewalkSegment()
        self.feature.SummaryCount = 1

    def test_score_summary_cross_slope(self):
        self._test_scores(
            'CrossSlope', 'ScoreSummaryCrossSlope',
            CROSS_SLOPE_VALUES, CROSS_SLOPE_SCORES)

    def test_score_max_cross_slope(self):
        self._test_scores(
            'MaxCrossSlope', 'ScoreMaxCrossSlope',
            CROSS_SLOPE_VALUES, CROSS_SLOPE_SCORES)

    def test_score_cross_slope(self):
        self.feature.CrossSlope = 1.0
        self.feature.MaxCrossSlope = 12.0
        self.assertEqual(self.feature.ScoreCrossSlope, 50)

        self.feature.CrossSlope = 3.0
        self.feature.MaxCrossSlope = 7.0
        self.assertEqual(self.feature.ScoreCrossSlope, 60)

    def test_score_largest_vertical_fault(self):
        self._test_scores(
            'LargestVerticalFault', 'ScoreLargestVerticalFault',
            LARGEST_VFAULT_VALUES, LARGEST_VFAULT_SCORES)

    def test_score_obstruction_types(self):
        self._test_scores(
            'ObstructionTypes', 'ScoreObstructionTypes',
            [None, 'Pole or signpost', 'Pole or signpost; Grate',
                'Hydrant; Bollard; Grate'],
            [100, 50, 0, 0])

    def test_score_width(self):
        self._test_scores(
            'Width', 'ScoreWidth', WIDTH_VALUES, WIDTH_SCORES)

    def test_score_compliance(self):
        self.feature.CrossSlope = 1.0
        self.feature.MaxCrossSlope = 12.0
        self.feature.LargestVerticaFault = 2
        self.feature.ObstructionTypes = 'Bollard'
        self.feature.Width = 46
        self.assertEqual(
            self.feature.ScoreCompliance,
            self.feature.ScoreCrossSlope * 0.25 +
            self.feature.ScoreLargestVerticalFault * 0.25 +
            self.feature.ScoreObstructionTypes * 0.25 +
            self.feature.ScoreWidth * 0.25)


class TestCurbRamp(unittest.TestCase, BaseTestFeature):

    def setUp(self):
        self.feature = CurbRamp()
        self.feature.QAStatus = D('Complete')
        self.feature.RampType = D('Perpendicular')

    def test_score_ramp_width(self):
        self.feature.InMedian = D('No')
        self._test_scores(
            'RampWidth', 'ScoreRampWidth', WIDTH_VALUES, WIDTH_SCORES)

        self.feature.InMedian = D('Yes')
        self._test_scores(
            'RampWidth', 'ScoreRampWidth',
            IN_MEDIAN_WIDTH_VALUES, IN_MEDIAN_WIDTH_SCORES)

    def test_ramp_cross_slope(self):
        self._test_scores(
            'RampCrossSlope', 'ScoreRampCrossSlope',
            CROSS_SLOPE_VALUES, CROSS_SLOPE_SCORES)

    def test_ramp_running_slope(self):
        self.feature.RampLength = 10*12
        self._test_scores(
            'RampRunningSlope', 'ScoreRampRunningSlope',
            RAMP_RUNNING_SLOPE_VALUES, RAMP_RUNNING_SLOPE_SCORES)

        self.feature.RampLength = 20*12
        self._test_scores(
            'RampRunningSlope', 'ScoreRampRunningSlope',
            RAMP_RUNNING_SLOPE_VALUES, [100]*4)

    def test_detectable_warning_type(self):
        self.feature.GutterRunningSlope = 1.0
        self.feature.GutterCrossSlope = 3.0
        self._test_scores(
            'DetectableWarningType', 'ScoreDetectableWarningType',
            DWS_TYPE_VALUES, DWS_TYPE_SCORES)

if __name__ == '__main__':
    unittest.main()
