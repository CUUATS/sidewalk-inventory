"""
Sidewalk Inventory and Assessment data model.
"""

from cuuats.datamodel import D, BaseFeature, OIDField, GeometryField, \
    NumericField, StringField, GlobalIDField, ForeignKey, ScaleField, \
    WeightsField, MethodField, BreaksScale, DictScale, StaticScale, \
    ScaleLevel

# Scales
WIDTH_SCALE = BreaksScale([36, 39, 42, 45, 48], [
    ScaleLevel(0, '35 inches or less', 6),
    ScaleLevel(20, '36 to 38 inches', 5),
    ScaleLevel(40, '39 to 41 inches', 4),
    ScaleLevel(60, '42 to 44 inches', 3),
    ScaleLevel(80, '45 to 47 inches', 2),
    ScaleLevel(100, '48 inches or more', 1),
], False)

CROSS_SLOPE_SCALE = BreaksScale([2, 4, 6, 8, 10], [
    ScaleLevel(100, '2 % or less', 1),
    ScaleLevel(80, '2.1 % to 4.0 %', 2),
    ScaleLevel(60, '4.1 % to 6.0 %', 3),
    ScaleLevel(40, '6.1 % to 8.0 %', 4),
    ScaleLevel(20, '8.1 % to 10.0 %', 5),
    ScaleLevel(0, '10.1 % or more', 6),
], True)

RAMP_RUNNING_SLOPE_SCALE = BreaksScale([8.3, 9.3, 10.3], [
    ScaleLevel(100, '8.3 % or less', 1),
    ScaleLevel(67, '8.4 % to 9.3 %', 2),
    ScaleLevel(33, '9.4 % to 10.3 %', 3),
    ScaleLevel(0, '10.4 % or more', 4),
], True)

RAMP_RUNNING_SLOPE_MIN_SCALE = StaticScale(
    ScaleLevel(100, 'Running slope is 5.0 % or less', 1))

TRUNCATED_DOMES = ScaleLevel(100, 'Truncated domes', 1)
NO_DWS = ScaleLevel(0, 'None', 4)
DWS_TYPE_SCALE = DictScale({
    'Truncated Domes - YELLOW': TRUNCATED_DOMES,
    'Truncated Domes - RED': TRUNCATED_DOMES,
    'Truncated Domes - OTHER': TRUNCATED_DOMES,
    'Pavement Grooves': ScaleLevel(50, 'Pavement grooves', 2),
    'Other': ScaleLevel(50, 'Other', 3),
    'None': NO_DWS,
    'N/A': NO_DWS,
})

DWS_WIDTH_SCALE = BreaksScale([0.7, 0.8, 0.9, 1], [
    ScaleLevel(20, '69 % or less', 5),
    ScaleLevel(40, '70 % to 79 %', 4),
    ScaleLevel(60, '80 % to 89 %', 3),
    ScaleLevel(80, '90 % to 99 %', 2),
    ScaleLevel(100, '100 %', 1),
], False)

GUTTER_RUNNING_SLOPE_SCALE = BreaksScale([5, 7, 9, 11, 13], [
    ScaleLevel(100, '5.0 % or less', 1),
    ScaleLevel(80, '5.1 % to 7.0 %', 2),
    ScaleLevel(60, '7.1 % to 9.0 %', 3),
    ScaleLevel(40, '9.1 % to 11.0 %', 4),
    ScaleLevel(20, '11.1 % to 13.0 %', 5),
    ScaleLevel(0, '13.1 % or more', 6),
], True)

LANDING_DIMENSIONS_SCALE = BreaksScale([24, 30, 36, 42, 48], [
    ScaleLevel(0, 'Less than 24 inches', 6),
    ScaleLevel(20, '24 to 29 inches', 5),
    ScaleLevel(40, '30 to 35 inches', 4),
    ScaleLevel(60, '36 to 41 inches', 3),
    ScaleLevel(80, '42 to 47 inches', 2),
    ScaleLevel(100, '48 inches or more', 1),
], False)

NO_LANDING_SCALE = StaticScale(
    ScaleLevel(0, 'No landing', 1))

VERTICAL_FAULT_COMPLIANT = ScaleLevel(100, 'Less than 1/4 inch, or beveled', 1)
LARGEST_VFAULT_SCALE = DictScale({
    'Over 0.50 inch': ScaleLevel(0, 'More than 1/2 inch', 3),
    'Between 0.25 and 0.50 inch, no bevel':
        ScaleLevel(50, '1/4 inch to 1/2 inch, not beveled', 2),
    'All vertical discontinuities compliant': VERTICAL_FAULT_COMPLIANT,
    'None': VERTICAL_FAULT_COMPLIANT,
    'N/A': VERTICAL_FAULT_COMPLIANT,
})

NO_OBSTRUCTION = ScaleLevel(100, 'No obstructions present', 1)
HAS_OBSTRUCTION = ScaleLevel(0, 'Obstructions present', 2)
OBSTRUCTION_SCALE = DictScale({
    'Pole or signpost': HAS_OBSTRUCTION,
    'Hydrant': HAS_OBSTRUCTION,
    'Bollard': HAS_OBSTRUCTION,
    'Grate': HAS_OBSTRUCTION,
    'Tree roots': HAS_OBSTRUCTION,
    'Tree trunk or other vegetation': HAS_OBSTRUCTION,
    'Other': HAS_OBSTRUCTION,
    'None': NO_OBSTRUCTION,
    'N/A': NO_OBSTRUCTION,
})

FLARE_SLOPE_SCALE = BreaksScale([10, 12, 14, 16, 18], [
    ScaleLevel(100, '10.0 % or less', 1),
    ScaleLevel(80, '10.1 % to 12.0 %', 2),
    ScaleLevel(60, '12.1 % to 14.0 %', 3),
    ScaleLevel(40, '14.1 % to 16.0 %', 4),
    ScaleLevel(20, '16.1 % to 18.0 %', 5),
    ScaleLevel(0, '18.1 % or more', 6),
], True)

NO_CONDITION_ISSUE = ScaleLevel(100, 'None', 1)
SURFACE_CONDITION_SCALE = DictScale({
    'Spalled': ScaleLevel(20, 'Spalling', 6),
    'Grass': ScaleLevel(40, 'Grass', 5),
    'Dirt': ScaleLevel(60, 'Dirt', 4),
    'Cracked': ScaleLevel(80, 'Cracking', 3),
    'Other': ScaleLevel(80, 'Other condition issue', 2),
    'N/A': NO_CONDITION_ISSUE,
    'None': NO_CONDITION_ISSUE,
})

SIDEWALK_VERTICAL_FAULT_COUNT_SCALE = BreaksScale([50, 100, 150, 200], [
    ScaleLevel(100, '49 or fewer', 1),
    ScaleLevel(80, '50  to 99', 2),
    ScaleLevel(60, '100 to 149', 3),
    ScaleLevel(40, '150 to 199', 4),
    ScaleLevel(20, '200 or more', 5),
], False)

CURB_RAMP_VERTICAL_FAULT_COUNT_SCALE = BreaksScale([0, 1, 2, 3], [
    ScaleLevel(100, '0', 1),
    ScaleLevel(80, '1', 2),
    ScaleLevel(60, '2', 3),
    ScaleLevel(40, '3', 4),
    ScaleLevel(20, '4 or more', 5),
], True)

SIDEWALK_CRACKED_PANEL_SCALE = BreaksScale([0.025, 0.05, 0.075, 0.1], [
    ScaleLevel(100, '2.4 % or less', 1),
    ScaleLevel(80, '2.5 % to 4.9 %', 2),
    ScaleLevel(60, '5.0 % to 7.4 %', 3),
    ScaleLevel(40, '7.5 % to 9.9 %', 4),
    ScaleLevel(20, '10.0 % or greater', 5),
], False)

CURB_RAMP_CRACKED_PANEL_SCALE = BreaksScale([0, 1, 2, 3], [
    ScaleLevel(100, '0', 1),
    ScaleLevel(80, '1', 2),
    ScaleLevel(60, '2', 3),
    ScaleLevel(40, '3', 4),
    ScaleLevel(20, '4 or more', 5),
], True)

OBSTRUCTION_TYPES_SCALE = BreaksScale([0, 1], [
    ScaleLevel(100, 'No obstructions present', 1),
    ScaleLevel(50, 'One type present', 2),
    ScaleLevel(0, 'Two or more types present', 3),
], True)

SCORE_BUTTON_HEIGHT = BreaksScale([5, 10, 15, 49, 54, 59], [
    ScaleLevel(0, '4 inches or less', 1),
    ScaleLevel(20, '5 to 9 inches', 2),
    ScaleLevel(60, '10 to 14 inches', 3),
    ScaleLevel(100, '15 to 48 inches', 4),
    ScaleLevel(60, '49 to 53 inches', 5),
    ScaleLevel(20, '54 to 58 inches', 6),
    ScaleLevel(0, '59 inches or greater', 7),
], True)

SCORE_BUTTON_SIZE = DictScale({
    'Very Small - < 1/2 inch': ScaleLevel(33, '0.4 inches or less', 3),
    'Medium - roughly 1 inch': ScaleLevel(67, '0.5 to 1.9 inches', 2),
    'Accessible - 2 inches or greater': ScaleLevel(
        100, '2 inches or greater', 1),
})

CROSSWALK_UNCONTROLLED_CROSS_SLOPE_SCALE = BreaksScale([5, 6, 7, 8, 9], [
    ScaleLevel(100, '5.0 % or less', 1),
    ScaleLevel(80, '5.1 % to 6.0 %', 2),
    ScaleLevel(60, '6.1 % to 7.0 %', 3),
    ScaleLevel(40, '7.1 % to 8.0 %', 4),
    ScaleLevel(20, '8.1 % to 9.0 %', 5),
    ScaleLevel(0, '9.1 % or more', 6),
], True)


class SlopeField(NumericField):
    """
    Field for slopes collected with a smart tool.
    """

    def validate(self, value):
        messages = super(SlopeField, self).validate(value)
        if value is None:
            return messages

        value_parts = str(value).split('.')
        if len(value_parts) == 2 and len(value_parts[1]) > 1:
            # Our smart tools only report slopes to the tenth,
            # so hundredths or smaller places indicate a problem.
            messages.append('%s has invalid decimals' % (self.label,))
        return messages


class SidewalkSegment(BaseFeature):
    """
    A block of sidewalk.
    """

    SUMMARY_FIELDS_EXCLUDE = [
        'OBJECTID',
        'GlobalID',
        'StaticID',
        'QAStatus',
        'QAComment',
        'SHAPE',
        'Obstruction',
        'NearestSegmentOID',
    ]

    # Fields common to all of the sidewalk inventory features
    OBJECTID = OIDField(
        'OBJECTID')

    PathType = NumericField(
        'Path Type',
        db_name='path_type')

    Municipality = StringField(
        'Municipality',
        db_name='municipality')

    SummaryCount = NumericField(
        'Summary Count',
        storage={'field_type': 'SHORT'})

    DrivewayCount = NumericField(
        'Driveway Count',
        storage={'field_type': 'SHORT'})

    LocalIssueCount = NumericField(
        'Local Issue Count',
        storage={'field_type': 'SHORT'})

    Material = NumericField(
        'Material',
        storage={'field_type': 'LONG', 'field_domain': 'MaterialType'})

    Width = NumericField(
        'Width',
        storage={'field_type': 'DOUBLE'})

    CrossSlope = NumericField(
        'Summary Cross Slope',
        storage={'field_type': 'DOUBLE'})

    MaxCrossSlope = NumericField(
        'Maximum Cross Slope',
        storage={'field_type': 'DOUBLE'})

    SurfaceCondition = NumericField(
        'Surface Condition',
        storage={'field_type': 'LONG', 'field_domain': 'SurfaceCondition'})

    VerticalFaultCount = NumericField(
        'Vertical Faults',
        storage={'field_type': 'SHORT'})

    LargestVerticalFault = NumericField(
        'Largest Vertical Fault',
        storage={'field_type': 'LONG', 'field_domain': 'FaultSize'})

    CrackedPanelCount = NumericField(
        'Cracked Panels',
        storage={'field_type': 'SHORT'})

    ObstructionTypes = StringField(
        'Obstruction Types')

    Grade = SlopeField(
        'Grade',
        storage={'field_type': 'DOUBLE'})

    Comment = StringField(
        'Comment',
        storage={'field_length': 200})

    # Score fields
    ScoreSummaryCrossSlope = ScaleField(
        'Summary Cross Slope Score',
        condition='self.qa_complete',
        scale=CROSS_SLOPE_SCALE,
        value_field='CrossSlope')

    ScoreMaxCrossSlope = ScaleField(
        'Maximum Cross Slope Score',
        condition='self.qa_complete',
        scale=CROSS_SLOPE_SCALE,
        value_field='MaxCrossSlope')

    ScoreCrossSlope = WeightsField(
        'Cross Slope Score',
        condition='self.qa_complete',
        weights={
            'ScoreSummaryCrossSlope': 0.5,
            'ScoreMaxCrossSlope': 0.5,
        })

    ScoreLargestVerticalFault = ScaleField(
        'Largest Vertical Fault Score',
        condition='self.qa_complete',
        scale=LARGEST_VFAULT_SCALE,
        value_field='LargestVerticalFault',
        use_description=True)

    ScoreObstructionTypes = ScaleField(
        'Obstruction Types Score',
        condition='self.qa_complete',
        scale=OBSTRUCTION_TYPES_SCALE,
        value_field='self.obstruction_types_count')

    ScoreWidth = ScaleField(
        'Width Score',
        condition='self.qa_complete',
        scale=WIDTH_SCALE,
        value_field='Width')

    ScoreCompliance = WeightsField(
        'Compliance Score',
        condition='self.qa_complete',
        weights={
            'ScoreMaxCrossSlope': 0.25,
            'ScoreLargestVerticalFault': 0.25,
            'ScoreObstructionTypes': 0.25,
            'ScoreWidth': 0.25,
        })

    ScoreSurfaceCondition = ScaleField(
        'Surface Condition Score',
        condition='self.qa_complete',
        scale=SURFACE_CONDITION_SCALE,
        use_description=True,
        value_field='SurfaceCondition')

    ScoreVerticalFaultCount = ScaleField(
        'Vertical Fault Count Score',
        condition='self.qa_complete',
        scale=SIDEWALK_VERTICAL_FAULT_COUNT_SCALE,
        value_field='VerticalFaultCount/self.condition_length')

    ScoreCrackedPanelCount = ScaleField(
        'Cracked Panel Count Score',
        condition='self.qa_complete',
        scale=SIDEWALK_CRACKED_PANEL_SCALE,
        value_field='CrackedPanelCount/(self.condition_length*1056)')

    ScoreCondition = WeightsField(
        'Condition Score',
        condition='self.qa_complete',
        weights={
            'ScoreSurfaceCondition': 0.334,
            'ScoreVerticalFaultCount': 0.333,
            'ScoreCrackedPanelCount': 0.333,
        })

    Shape = GeometryField(
        'Shape',
        deferred=False)

    @property
    def obstruction_types_count(self):
        if self.ObstructionTypes is None:
            return 0
        return len(self.ObstructionTypes.split('; '))

    @property
    def condition_length(self):
        return self.Shape.length / 5280

    @property
    def qa_complete(self):
        return self.SummaryCount > 0

    @property
    def aggregate_scores(self):
        return self.qa_complete

    def _copy_sidewalk_summary_values(self, sidewalk):
        for field_name in sidewalk.fields.keys():
            if field_name not in self.SUMMARY_FIELDS_EXCLUDE and \
                    hasattr(self, field_name):
                setattr(self, field_name, getattr(sidewalk, field_name))

    def update_sidewalk_fields(self):
        self.SummaryCount = 0
        self.DrivewayCount = 0
        self.LocalIssueCount = 0
        self.MaxCrossSlope = 0
        obstruction_types = []

        for sw in self.sidewalk_set:
            if not sw.qa_complete:
                continue
            if sw.is_summary:
                self.SummaryCount += 1
                self._copy_sidewalk_summary_values(sw)
            elif sw.is_driveway:
                self.DrivewayCount += 1
            elif sw.is_localissue:
                self.LocalIssueCount += 1

            if sw.CrossSlope > self.MaxCrossSlope:
                self.MaxCrossSlope = sw.CrossSlope

            if sw.Obstruction not in (None, D('None'), D('N/A')):
                if sw.Obstruction not in obstruction_types:
                    obstruction_types.append(sw.Obstruction)

        self.ObstructionTypes = '; '.join(
            [ot.description for ot in obstruction_types]) or None


class InventoryFeature(BaseFeature):
    """
    A feature in the sidewalk inventory.
    """

    QASTATUS_FIELD = 'QAStatus'
    QACOMMENT_FIELD = 'QAComment'

    # Fields common to all of the sidewalk inventory features
    OBJECTID = OIDField('OBJECTID', order=-1)
    GlobalID = GlobalIDField('GlobalID', order=-1)
    StaticID = NumericField('Static ID', order=-1)
    QAStatus = NumericField('QA Status', order=1)
    QAComment = StringField('QA Comment', order=1)
    SHAPE = GeometryField('SHAPE', order=1)

    @property
    def aggregate_scores(self):
        return self.qa_complete

    @property
    def qa_complete(self):
        """
        Is the QA status complete?
        """

        return self.QAStatus == D('Complete')

    def perform_qa(self):
        """
        Perform automated quality assurance.
        """

        # Apply QA unless the current status is Needs Staff Review.
        if getattr(self, self.QASTATUS_FIELD) != D('Needs Staff Review'):
            # Perform cleaning and validation.
            self.clean()
            messages = self.validate()

            # Consolidate missing data messages.
            missing = [m[:-11] for m in messages if m.endswith(' is missing')]
            if missing:
                messages = ['Missing data: %s' % (', '. join(missing),)] + [
                    m for m in messages if not m.endswith(' is missing')]

            # Set QA status based on the number of messages.
            if len(messages) > 0:
                setattr(self, self.QASTATUS_FIELD, D('Needs Field Review'))
            else:
                setattr(self, self.QASTATUS_FIELD, D('Complete'))

            # Overwrite existing QA comments.
            qacomment = '; '.join(messages)
            if len(qacomment) > 200:
                qacomment = qacomment[:197] + '...'

            # Use a null value if there is no QA comment.
            qacomment = qacomment or None
            setattr(self, self.QACOMMENT_FIELD, qacomment)

    def assign_staticid(self):
        """
        Assign a static ID based on the OBJECTID.
        """

        if self.StaticID is None:
            self.StaticID = self.OBJECTID


class Sidewalk(InventoryFeature):

    PointType = NumericField('Point Type', required=True)
    Material = NumericField('Material', required_if='self.is_summary')
    Width = NumericField('Width', max=50*12, required_if='self.is_summary')
    CrossSlope = SlopeField('Cross Slope', max=25,
                            required_if='self.is_summary or self.is_driveway')
    SurfaceCondition = NumericField('Surface Condition',
                                    required_if='self.is_summary')
    VerticalFaultCount = NumericField('Vertical Faults',
                                      required_if='self.is_summary')
    LargestVerticalFault = NumericField('Largest Fault',
                                        required_if='self.is_summary')
    CrackedPanelCount = NumericField('Cracked Panels',
                                     required_if='self.is_summary')
    Obstruction = NumericField('Obstruction',
                               required_if='self.is_summary')
    Grade = SlopeField('Grade')
    Comment = StringField('Comment')
    NearestSegmentOID = ForeignKey(
        'Nearest Sidewalk Segment',
        origin_class=SidewalkSegment)

    @property
    def is_summary(self):
        return self.PointType == D('Summary')

    @property
    def is_driveway(self):
        return self.PointType == D('Driveway')

    @property
    def is_localissue(self):
        return self.PointType == D('Local Issue')

    def clean(self):
        # Replace N/As with Nones for summary points.
        if self.is_summary:
            for field_name in ('LargestVerticalFault', 'SurfaceCondition',
                               'Obstruction'):
                if getattr(self, field_name) == D('N/A'):
                    setattr(self, field_name, D('None'))

    def validate(self):
        messages = super(Sidewalk, self).validate()
        # Check that the largest vertical fault and number of vertical faults
        # are consistent.
        if self.is_summary and \
            (self.LargestVerticalFault == D('None')) != \
                (self.VerticalFaultCount == 0):
            messages.append('Vertical Faults does not match Largest Fault')
        return messages


class CurbRamp(InventoryFeature):

    QASTATUS_FIELD = 'AutoQAStatus'
    QACOMMENT_FIELD = 'AutoQAComment'

    RampType = NumericField(
        'Ramp Type',
        required=True)

    Material = NumericField(
        'Material',
        required_if='self.has_ramp')

    RampWidth = NumericField(
        'Ramp Width',
        required_if='self.has_ramp')

    RampLength = NumericField(
        'Ramp Length',
        required_if='self.has_ramp')

    RampRunningSlope = SlopeField(
        'Ramp Running Slope',
        max=25,
        required_if='self.has_ramp')

    RampCrossSlope = SlopeField(
        'Ramp Cross Slope',
        max=25,
        required_if='self.has_ramp')

    DetectableWarningType = NumericField(
        'DWS Type',
        required_if='self.has_ramp')

    DetectableWarningWidth = NumericField(
        'DWS Width',
        required_if='self.has_ramp')

    DetectableWarningLength = NumericField(
        'DWS Length',
        required_if='self.has_ramp')

    GutterRunningSlope = SlopeField(
        'Gutter Running Slope',
        max=25,
        required_if='self.has_ramp')

    GutterCrossSlope = SlopeField(
        'Gutter Cross Slope',
        max=25,
        required_if='self.has_ramp')

    LandingWidth = NumericField(
        'Landing Width',
        required_if='self.has_ramp')

    LandingLength = NumericField(
        'Landing Length',
        required_if='self.has_ramp')

    LandingRunningSlope = SlopeField(
        'Landing Running Slope',
        max=25,
        required_if='self.has_ramp')

    LandingCrossSlope = SlopeField(
        'Landing Cross Slope',
        max=25,
        required_if='self.has_ramp')

    LeftApproachWidth = NumericField(
        'Left Approach Width',
        required_if='self.has_ramp')

    LeftApproachRunningSlope = SlopeField(
        'Left Approach Running Slope',
        max=25,
        required_if='self.has_ramp')

    LeftApproachCrossSlope = SlopeField(
        'Left Approach Cross Slope',
        max=25,
        required_if='self.has_ramp')

    RightApproachWidth = NumericField(
        'Right Approach Width',
        required_if='self.has_ramp')

    RightApproachRunningSlope = SlopeField(
        'Right Approach Running Slope',
        max=25,
        required_if='self.has_ramp')

    RightApproachCrossSlope = SlopeField(
        'Right Approach Cross Slope',
        max=25,
        required_if='self.has_ramp')

    EdgeTreatment = NumericField(
        'Edge Treatment',
        required_if='self.has_ramp')

    FlareSlope = SlopeField(
        'Flare Slope',
        max=50,
        required_if='self.has_ramp')

    PavementFaultCount = NumericField(
        'Vertical Faults',
        required_if='self.has_ramp')

    LargestPavementFault = NumericField(
        'Largest Fault',
        required_if='self.has_ramp')

    CrackedPanelCount = NumericField(
        'Cracked Panels',
        required_if='self.has_ramp')

    SurfaceCondition = NumericField(
        'Surface Condition',
        required_if='self.has_ramp')

    Obstruction = NumericField(
        'Obstruction',
        required_if='self.has_ramp')

    InMedian = NumericField(
        'In Median',
        required_if='self.has_ramp')

    Comment = StringField(
        'Comment')

    AutoQAStatus = NumericField('Auto QA Status')
    AutoQAComment = StringField('Auto QA Comment')
    AutoQAOverride = NumericField('Override Auto QA Status')

    # Score fields
    ScoreRampWidth = ScaleField(
        'Ramp Width Score',
        condition='self.qa_complete and self.has_ramp',
        scale=WIDTH_SCALE,
        value_field='RampWidth')

    ScoreRampCrossSlope = ScaleField(
        'Ramp Cross Slope Score',
        condition='self.qa_complete and self.has_ramp',
        scale=CROSS_SLOPE_SCALE,
        value_field='RampCrossSlope')

    ScoreRampRunningSlope = ScaleField(
        'Ramp Running Slope Score',
        condition='self.qa_complete and self.has_ramp',
        scale=(
            ('self.RampLength > 15*12', StaticScale(
                ScaleLevel(100, 'Ramp length > 15 feet', 1)), 2),
            ('self.RampLength <= 15*12', RAMP_RUNNING_SLOPE_SCALE, 1),
        ),
        value_field='RampRunningSlope')

    ScoreDetectableWarningType = ScaleField(
        'DWS Type Score',
        condition='self.qa_complete and self.has_ramp',
        scale=(
            # Detectable warnings are only required on ramps adjacent
            # to the street.
            ('not self.has_gutter', StaticScale(
                ScaleLevel(100, 'Ramp not adjacent to the street', 1)), 3),
            ('self.has_dws', DWS_TYPE_SCALE, 1),
            ('not self.has_dws', StaticScale(
                ScaleLevel(0, 'None', 1)), 2),
        ),
        use_description=True,
        value_field='DetectableWarningType')

    ScoreDetectableWarningWidth = ScaleField(
        'DWS Width Score',
        condition='self.qa_complete and self.has_ramp',
        scale=(
            # Detectable warnings are only required on ramps adjacent
            # to the street.
            ('not self.has_gutter', StaticScale(
                ScaleLevel(100, 'Ramp not adjacent to the street', 1)), 3),
            ('self.has_dws', DWS_WIDTH_SCALE, 1),
            ('not self.has_dws', StaticScale(
                ScaleLevel(0, 'None', 1)), 2),
        ),
        value_field='self.dws_coverage')

    ScoreGutterCrossSlope = ScaleField(
        'Gutter Cross Slope Score',
        scale=CROSS_SLOPE_SCALE,
        condition='self.qa_complete and self.has_ramp',
        value_field='GutterCrossSlope')

    ScoreGutterRunningSlope = ScaleField(
        'Gutter Running Slope Score',
        scale=GUTTER_RUNNING_SLOPE_SCALE,
        condition='self.qa_complete and self.has_ramp',
        value_field='GutterRunningSlope')

    ScoreLandingDimensions = ScaleField(
        'Landing Dimensions Score',
        scale=(
            ('self.is_blended_transition', RAMP_RUNNING_SLOPE_MIN_SCALE, 3),
            ('not self.has_landing', NO_LANDING_SCALE, 2),
            ('not self.is_blended_transition', LANDING_DIMENSIONS_SCALE, 1),
        ),
        condition='self.qa_complete and self.has_ramp',
        value_field='min(LandingWidth, LandingLength)')

    ScoreLandingSlope = ScaleField(
        'Landing Slope Score',
        scale=(
            ('self.is_blended_transition', RAMP_RUNNING_SLOPE_MIN_SCALE, 3),
            ('not self.has_landing', NO_LANDING_SCALE, 2),
            ('not self.is_blended_transition', CROSS_SLOPE_SCALE, 1),
        ),
        condition='self.qa_complete and self.has_ramp',
        value_field='max(LandingRunningSlope, LandingCrossSlope)')

    ScoreApproachCrossSlope = ScaleField(
        'Approach Cross Slope Score',
        scale=(
            ('self.approach_count > 0', CROSS_SLOPE_SCALE, 1),
            ('self.approach_count == 0', StaticScale(
                ScaleLevel(100, 'No approaches', 1)), 2),
        ),
        condition='self.qa_complete and self.has_ramp',
        value_field='max(LeftApproachCrossSlope, RightApproachCrossSlope)')

    ScoreFlareSlope = ScaleField(
        'Flare Slope Score',
        scale=(
            ('self.has_flares', FLARE_SLOPE_SCALE, 1),
            ('not self.has_flares', StaticScale(
                ScaleLevel(100, 'No flares', 1)), 2),
        ),
        condition='self.qa_complete and self.has_ramp',
        value_field='FlareSlope')

    ScoreLargestPavementFault = ScaleField(
        'Largest Vertical Fault Score',
        scale=LARGEST_VFAULT_SCALE,
        condition='self.qa_complete and self.has_ramp',
        value_field='LargestPavementFault',
        use_description=True)

    ScoreObstruction = ScaleField(
        'Obstruction Score',
        scale=OBSTRUCTION_SCALE,
        condition='self.qa_complete and self.has_ramp',
        value_field='Obstruction',
        use_description=True)

    ScoreRampGeometry = WeightsField(
        'Ramp Geometry Score',
        condition='self.qa_complete and self.has_ramp',
        weights={
            'ScoreRampWidth': 0.2,
            'ScoreRampCrossSlope': 0.4,
            'ScoreRampRunningSlope': 0.4,
        })

    ScoreDetectableWarning = WeightsField(
        'Detectable Warning Score',
        condition='self.qa_complete and self.has_ramp',
        weights={
            'ScoreDetectableWarningType': 0.667,
            'ScoreDetectableWarningWidth': 0.333,
        })

    ScoreGutter = WeightsField(
        'Gutter Score',
        condition='self.qa_complete and self.has_ramp',
        weights={
            'ScoreGutterCrossSlope': 0.5,
            'ScoreGutterRunningSlope': 0.5,
        })

    ScoreLanding = WeightsField(
        'Landing Score',
        condition='self.qa_complete and self.has_ramp',
        weights={
            'ScoreLandingDimensions': 0.5,
            'ScoreLandingSlope': 0.5,
        })

    ScoreApproachFlare = WeightsField(
        'Approaches and Flares Score',
        condition='self.qa_complete and self.has_ramp',
        weights={
            'ScoreApproachCrossSlope': 0.5,
            'ScoreFlareSlope': 0.5,
        })

    ScoreHazard = WeightsField(
        'Hazard Score',
        condition='self.qa_complete and self.has_ramp',
        weights={
            'ScoreLargestPavementFault': 0.5,
            'ScoreObstruction': 0.5,
        })

    ScoreCompliance = WeightsField(
        'Compliance Score',
        condition='self.qa_complete and self.has_ramp',
        weights={
            'ScoreRampWidth': 0.05,
            'ScoreRampCrossSlope': 0.1,
            'ScoreRampRunningSlope': 0.1,
            'ScoreDetectableWarningType': 0.1,
            'ScoreDetectableWarningWidth': 0.05,
            'ScoreGutterCrossSlope': 0.05,
            'ScoreGutterRunningSlope': 0.05,
            'ScoreLandingDimensions': 0.1,
            'ScoreLandingSlope': 0.1,
            'ScoreApproachCrossSlope': 0.05,
            'ScoreFlareSlope': 0.05,
            'ScoreLargestPavementFault': 0.1,
            'ScoreObstruction': 0.1,
        })

    ScoreSurfaceCondition = ScaleField(
        'Surface Condition Score',
        condition='self.qa_complete and self.has_ramp',
        scale=SURFACE_CONDITION_SCALE,
        use_description=True,
        value_field='SurfaceCondition')

    ScorePavementFaultCount = ScaleField(
        'Vertical Fault Count Score',
        condition='self.qa_complete and self.has_ramp',
        scale=CURB_RAMP_VERTICAL_FAULT_COUNT_SCALE,
        value_field='PavementFaultCount')

    ScoreCrackedPanelCount = ScaleField(
        'Cracked Panel Count Score',
        condition='self.qa_complete and self.has_ramp',
        scale=CURB_RAMP_CRACKED_PANEL_SCALE,
        value_field='CrackedPanelCount')

    ScoreCondition = WeightsField(
        'Condition Score',
        condition='self.qa_complete and self.has_ramp',
        weights={
            'ScoreSurfaceCondition': 0.334,
            'ScorePavementFaultCount': 0.333,
            'ScoreCrackedPanelCount': 0.333,
        })

    @property
    def has_ramp(self):
        return self.RampType != D('None')

    @property
    def has_left_approach(self):
        return self.LeftApproachWidth > 0

    @property
    def has_right_approach(self):
        return self.RightApproachWidth > 0

    @property
    def approach_count(self):
        return sum([self.has_left_approach, self.has_right_approach])

    @property
    def has_landing(self):
        return self.LandingWidth > 0 and self.LandingLength > 0

    @property
    def has_flares(self):
        return self.EdgeTreatment == D('Flared Sides')

    @property
    def has_dws(self):
        return self.DetectableWarningType not in (D('None'), D('N/A'))

    @property
    def has_gutter(self):
        return self.GutterCrossSlope > 0 or self.GutterRunningSlope > 0

    @property
    def in_median(self):
        return self.InMedian == D('Yes')

    @property
    def is_parallel(self):
        return self.RampType == D('Parallel')

    @property
    def is_blended_transition(self):
        # Anything with a running slope greater than 5.0% is scored as a
        # ramp, while features with a running slope less than or equal to
        # 5.0% are scored as blended transitions.
        return self.RampRunningSlope <= 5

    @property
    def dws_coverage(self):
        # We subtract four inches from the ramp/landing width to account for
        # the two-inch border allowed around truncated domes to secure them to
        # the ramp.
        if self.is_parallel and self.has_landing:
            full_width = self.LandingWidth
        else:
            full_width = self.RampWidth
        return self.DetectableWarningWidth/(full_width - 4)

    @property
    def aggregate_scores(self):
        return self.qa_complete and self.has_ramp

    def clean(self):
        if self.has_ramp:
            # Replace N/As with Nones.
            for field_name in ('DetectableWarningType', 'SurfaceCondition',
                               'LargestPavementFault', 'Obstruction'):
                if getattr(self, field_name) == D('N/A'):
                    setattr(self, field_name, D('None'))

            # Replace N/A with No for In Median.
            if self.InMedian == D('N/A'):
                self.InMedian = D('No')

            # Set null responses to 0 in cases where no value is expected.
            if self.DetectableWarningType == D('None'):
                if self.DetectableWarningWidth is None:
                    self.DetectableWarningWidth = 0
                if self.DetectableWarningLength is None:
                    self.DetectableWarningLength = 0

            if self.EdgeTreatment != D('Flared Sides'):
                if self.FlareSlope is None:
                    self.FlareSlope = 0

    def validate(self):
        messages = super(CurbRamp, self).validate()
        # Check that the largest vertical fault and number of vertical faults
        # are consistent.
        if (self.LargestPavementFault == D('None')) != \
                (self.PavementFaultCount == 0):
            messages.append('Vertical Faults does not match Largest Fault')

        # Check that the edge treatment matches the flare slope value.
        if (self.EdgeTreatment == D('Flared Sides')) != \
                (self.FlareSlope > 0 or self.FlareSlope == -1):
            messages.append('Edge Treatment does not match Flare Slope')

        # Ignore validation messages (except for missing photo) if the ramp
        # type is None.
        if self.RampType == D('None'):
            messages = []

        # Check for a photo.
        if self.attachments.count() == 0:
            messages.append('Photo is missing')

        return messages

    def perform_qa(self):
        """
        Perform automated quality assurance.
        """

        # Don't touch the QA Status if the Override Auto QA Status field
        # is set to Yes.
        if self.AutoQAOverride != D('Yes'):
            return super(CurbRamp, self).perform_qa()


class Crosswalk(InventoryFeature):

    SurfaceType = NumericField(
        'Surface Type',
        required=True)

    Width = NumericField(
        'Width',
        required=True)

    CrossSlope = SlopeField(
        'Cross Slope',
        max=25,
        required=True)

    MarkingType = NumericField(
        'Marking Type',
        required=True)

    Comment = StringField(
        'Comment')

    StopControlledIntersection = NumericField(
        'Stop-Controlled Intersection')

    MidblockCrossing = NumericField(
        'Midblock Crossing')

    # Score fields
    ScoreWidth = ScaleField(
        'Width Score',
        condition='self.qa_complete',
        scale=(
            ('self.has_width', WIDTH_SCALE),
            ('not self.has_width', StaticScale(100)),
        ),
        value_field='Width')

    ScoreCrossSlope = ScaleField(
        'Cross Slope Score',
        condition='self.qa_complete',
        scale=(
            ('self.is_midblock', StaticScale(100)),
            ('self.is_stop_controlled', CROSS_SLOPE_SCALE),
            ('not self.is_stop_controlled',
             CROSSWALK_UNCONTROLLED_CROSS_SLOPE_SCALE),
        ),
        value_field='CrossSlope')

    ScoreCompliance = WeightsField(
        'Compliance Score',
        condition='self.qa_complete',
        weights={
            'ScoreWidth': 0.5,
            'ScoreCrossSlope': 0.5,
        })

    @property
    def has_width(self):
        return self.MarkingType not in (
            D('No Painted Markings'), D('Box for Exclusive Period'))

    @property
    def is_stop_controlled(self):
        return self.StopControlledIntersection == D('Yes')

    @property
    def is_midblock(self):
        return self.MidblockCrossing == D('Yes')

    def clean(self):
        if not self.has_width and self.Width is None:
            self.Width = 0


class PedestrianSignal(InventoryFeature):

    BUTTON_FIELDS = [
        'PedButtonSize',
        'HighContrastButton',
        'TactileArrowPresent',
        'VibrotactileSignal',
        'ButtonHeight',
        'AllWeatherSurface',
        'ButtonSpacing',
        'ButtonOffsetFCurb',
        'ButtonCount',
        'LocatorTone',
    ]

    SignalPresent = NumericField('Signal Present', required=True)
    PedButtonLocation = NumericField('Button Location', required=True)
    PedButtonSize = NumericField('Button Size', required=True)
    HighContrastButton = NumericField('High Contrast', required=True)
    TactileArrowPresent = NumericField('Tactile Arrow', required=True)
    VibrotactileSignal = NumericField('Vibrotactile Button', required=True)
    ButtonHeight = NumericField('Button Height', max=5*12, required=True)
    AllWeatherSurface = NumericField('All Weather Surface', required=True)
    ButtonSpacing = NumericField('10 Feet Apart', required=True)
    ButtonOffsetFCurb = NumericField('Within 10 Feet of Curb', required=True)
    ButtonCount = NumericField('Number of Buttons', min=0, max=2,
                               required=True)
    LocatorTone = NumericField('Locator Tone',  required=True)
    PassiveDetection = NumericField('Passive Detector', required=True)
    Comment = StringField('Comment')

    # Score fields
    ScoreButtonSize = ScaleField(
        'Button Size Score',
        condition='self.qa_complete and self.has_button',
        scale=SCORE_BUTTON_SIZE,
        value_field='PedButtonSize',
        use_description=True)

    ScoreButtonHeight = ScaleField(
        'Button Height Score',
        condition='self.qa_complete and self.has_button',
        scale=SCORE_BUTTON_HEIGHT,
        value_field='ButtonHeight')

    ScoreButtonPositionAppearance = MethodField(
        'Button Position and Appearance Score',
        condition='self.qa_complete and self.has_button',
        method_name='_position_appearance_score')

    ScoreTactileFeatures = MethodField(
        'Tactile Features Score',
        condition='self.qa_complete',
        method_name='_tactile_features_score')

    ScoreCompliance = MethodField(
        'Compliance Score',
        condition='self.qa_complete',
        method_name='_compliance_score')

    def _position_appearance_score(self, field_name):
        score = 0
        if self.ButtonCount == 1 or self.ButtonSpacing == D('Yes'):
            score += 15
        if self.ButtonOffsetFCurb == D('Yes'):
            score += 15
        if self.AllWeatherSurface == D('Yes'):
            score += 15
        if self.HighContrastButton == D('Yes'):
            score += 25
        if self.LocatorTone == D('Yes'):
            score += 30
        return score

    def _tactile_features_score(self, field_name):
        score = 0
        if self.TactileArrowPresent == D('Yes'):
            score += 50
        if self.VibrotactileSignal == D('Yes'):
            score += 50
        return score

    def _compliance_score(self, field_name):
        if self.has_button:
            return (0.2 * self.ScoreButtonSize +
                    0.2 * self.ScoreButtonHeight +
                    0.3 * self.ScoreButtonPositionAppearance +
                    0.3 * self.ScoreTactileFeatures)
        return self.ScoreTactileFeatures

    @property
    def has_button(self):
        return self.PedButtonLocation not in (D('No Button'), D('N/A'))

    def clean(self):
        # Set irrelevant fields to N/A for signals that don't have a button.
        if not self.has_button:
            for field_name in self.BUTTON_FIELDS:
                if getattr(self, field_name) is None:
                    field = self.fields.get(field_name)
                    if field.domain_name is not None:
                        setattr(self, field_name, D('N/A'))
                    else:
                        setattr(self, field_name, 0)

    def validate(self):
        messages = super(PedestrianSignal, self).validate()
        if not (self.has_button == (self.ButtonCount > 0)):
            messages.append('Button Count does not match Button Location')
        return messages
