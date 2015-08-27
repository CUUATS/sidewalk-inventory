"""
Sidewalk Inventory and Assessment data model.
"""

from cuuats.datamodel import BaseFeature, OIDField, GeometryField, \
    NumericField, StringField, GlobalIDField, BreaksScale, DictScale, \
    ForeignKey, D
from cuuats.datamodel.features import IDENTIFIER_RE

# Scales
WIDTH_SCALE = BreaksScale(
    [36, 39, 42, 45, 48], [0, 20, 40, 60, 80, 100], False)

IN_MEDIAN_WIDTH_SCALE = BreaksScale(
    [48, 51, 54, 57, 60], [0, 20, 40, 60, 80, 100], False)

CROSS_SLOPE_SCALE = BreaksScale(
    [2, 4, 6, 8, 10], [100, 80, 60, 40, 20, 0], True)

RAMP_RUNNING_SLOPE_SCALE = BreaksScale(
    [8.3, 9.3, 10.3], [100, 67, 33, 0], True)

DWS_TYPE_SCALE = DictScale({
    'Truncated Domes - YELLOW': 100,
    'Truncated Domes - RED': 100,
    'Truncated Domes - OTHER': 100,
    'Pavement Grooves': 50,
    'Other': 50,
    'None': 0,
    'N/A': 0,
})

DWS_WIDTH_SCALE = BreaksScale(
    [0, 0.7, 0.8, 0.9, 1], [0, 20, 40, 60, 80, 100], True)

DWS_LENGTH_SCALE = BreaksScale(
    [0, 11, 23], [0, 33, 67, 100], True)

GUTTER_RUNNING_SLOPE_SCALE = BreaksScale(
    [5, 7, 9, 11, 13], [100, 80, 60, 40, 20, 0], True)

LANDING_DIMENSIONS_SCALE = BreaksScale(
    [24, 30, 36, 42, 48], [0, 20, 40, 60, 80, 100], False)

LARGEST_VFAULT_SCALE = DictScale({
    'Over 0.50 inch': 0,
    'Between 0.25 and 0.50 inch, no bevel': 50,
    'All vertical discontinuities compliant': 100,
    'None': 100,
    'N/A': 100,
})

OBSTRUCTION_SCALE = DictScale({
    'Pole or signpost': 0,
    'Hydrant': 0,
    'Bollard': 0,
    'Grate': 0,
    'Tree roots': 0,
    'Tree trunk or other vegetation': 0,
    'Other': 0,
    'None': 100,
    'N/A': 100,
})

FLARE_SLOPE_SCALE = BreaksScale(
    [10, 12, 14, 16, 18], [100, 80, 60, 40, 20, 0], True)


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

    # Fields common to all of the sidewalk inventory features
    OBJECTID = OIDField('OBJECTID', order=-1)
    path_type = NumericField('Path Type')
    owner = StringField('Owner')
    municipality = StringField('Municipality')
    data_source = StringField('Data Source')
    crossing_type = StringField('Crossing Type')
    bike_facility = StringField('Bicycle Facility')
    safe_route = StringField('Safe Route to School')

    summary_count = NumericField(
        'Summary Count')

    driveway_count = NumericField(
        'Driveway Count')

    localissue_count = NumericField(
        'Local Issue Count')

    Shape = GeometryField('SHAPE', order=1)

    def update_sidewalk_fields(self):
        self.summary_count = 0
        self.driveway_count = 0
        self.localissue_count = 0

        for sw in self.sidewalk_set:
            if sw.is_summary:
                self.summary_count += 1
            elif sw.is_driveway:
                self.driveway_count += 1
            elif sw.is_localissue:
                self.localissue_count += 1


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
    def qa_complete(self):
        """
        Is the QA status complete?
        """

        return self.QAStatus == D('Complete')

    def _get_eval_value(self, field):
        """
        Get the current value of the field, converting feet.inches values
        to inches.
        """

        value = getattr(self, field.name)
        if not isinstance(field, NumericField):
            return value

        # We have a feet.inches field.
        if value is None:
            return None

        value_parts = ('%0.2f' % (value,)).split('.')
        return int(value_parts[0]) * 12 + int(value_parts[1])

    def eval(self, expression):
        """
        Evaluate the expression in the context of the feature instance.
        """

        # Override expression evaluation so that feet.inches fields evaluate
        # to the value of the field in inches.
        identifiers = IDENTIFIER_RE.findall(expression)
        locals_dict = dict([(n, self._get_eval_value(f)) for (n, f)
                            in self.fields.items() if n in identifiers])
        locals_dict.update({'self': self})
        return eval(expression, {}, locals_dict)

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

    SingleApproach = NumericField(
        'Single Approach')

    Comment = StringField(
        'Comment')

    AutoQAStatus = NumericField('Auto QA Status')
    AutoQAComment = StringField('Auto QA Comment')
    AutoQAOverride = NumericField('Override Auto QA Status')

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
    def in_median(self):
        return self.InMedian == D('Yes')

    @property
    def is_blended_transition(self):
        # Anything with a running slope greater than 5.0% is scored as a
        # ramp, while features with a running slope less than or equal to
        # 5.0% are scored as blended transitions.
        return self.RampRunningSlope <= 5

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

    SurfaceType = NumericField('Surface Type', required=True)
    Width = NumericField('Width', required=True)
    CrossSlope = SlopeField('Cross Slope', max=25, required=True)
    MarkingType = NumericField('Marking Type', required=True)
    Comment = StringField('Comment')

    def clean(self):
        no_width = (D('No Painted Markings'), D('Box for Exclusive Period'))
        if self.MarkingType in no_width and self.Width is None:
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
