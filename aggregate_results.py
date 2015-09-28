"""
Aggregate scores from the Sidewalk Inventory and Assessment.
"""

import arcpy
import os
from production import SS_PATH, CR_PATH, CW_PATH, PS_PATH, ZONE_PATH, \
    RESULT_PATH


FEATURE_CLASSES = [
    ('Sidewalk',  'Sidewalk', SS_PATH),
    ('CurbRamp', 'Curb Ramp', CR_PATH),
    ('Crosswalk', 'Crosswalk', CW_PATH),
    ('PedestrianSignal', 'Pedestrian Signal', PS_PATH),
]

memory_layers = []


def memory_path(layer_name):
    return r'in_memory\%s' % (layer_name,)


def create_memory_layer():
    layer_name = 'layer_%i' % (len(memory_layers),)
    memory_layers.append(layer_name)
    return layer_name


def clear_memory_layers():
    for layer_name in memory_layers:
        if arcpy.Exists(memory_path(layer_name)):
            arcpy.Delete_management(memory_path(layer_name))

target_path = ZONE_PATH

for (fc_name, fc_label, fc_path) in FEATURE_CLASSES:
    # Create a wildcard for score fields.
    score_wildcard = fc_name + 'Score*'

    # Update field types and labels.
    field_mappings = arcpy.FieldMappings()
    for field in arcpy.ListFields(fc_path, 'Score*'):
        field_map = arcpy.FieldMap()
        field_map.addInputField(fc_path, field.name)
        output_field = field_map.outputField
        output_field.type = 'Double'
        output_field.name = fc_name + field.name
        output_field.aliasName = fc_label + ' ' + field.aliasName
        field_map.outputField = output_field
        field_mappings.addFieldMap(field_map)

    print 'Updating %s field types and labels' % (fc_label,)
    ftl_name = create_memory_layer()
    arcpy.FeatureClassToFeatureClass_conversion(
        fc_path, 'in_memory', ftl_name, field_mapping=field_mappings)
    ftl_field_names = [f.name for f in arcpy.ListFields(memory_path(ftl_name))]

    # Check whether this is a linear feature.
    is_linear = arcpy.Describe(fc_path).shapeType == 'Polyline'
    if is_linear:
        # Intersect features with the analysis polygons.
        print 'Intersecting %s' % (fc_label,)
        intersect_name = create_memory_layer()
        arcpy.Intersect_analysis(
            [memory_path(ftl_name), ZONE_PATH], memory_path(intersect_name))

        # Remove unwanted fields.
        for field in arcpy.ListFields(memory_path(intersect_name)):
            if field.name not in ftl_field_names:
                arcpy.DeleteField_management(
                    memory_path(intersect_name), field.name)

        # Add a field with the length of the feature.
        arcpy.AddGeometryAttributes_management(
            memory_path(intersect_name), 'LENGTH')

        # Multiply scores by the feature length.
        print 'Length-weighting %s scores' % (fc_label,)
        for field in arcpy.ListFields(
                memory_path(intersect_name), score_wildcard):
            arcpy.CalculateField_management(
                memory_path(intersect_name), field.name,
                '!%s! * !LENGTH!' % (field.name,), 'PYTHON')

        ftl_name = intersect_name

    # Create a field map.
    field_mappings = arcpy.FieldMappings()
    field_mappings.addTable(target_path)

    # Add score fields.
    for field in arcpy.ListFields(memory_path(ftl_name), score_wildcard):
        field_map = arcpy.FieldMap()
        field_map.addInputField(memory_path(ftl_name), field.name)
        field_map.mergeRule = 'Sum' if is_linear else 'Mean'
        field_mappings.addFieldMap(field_map)

    # For linear features, add the length field.
    if is_linear:
        field_map = arcpy.FieldMap()
        field_map.addInputField(memory_path(ftl_name), 'LENGTH')
        field_map.mergeRule = 'Sum'
        field_mappings.addFieldMap(field_map)

    # Perform the join.
    join_name = create_memory_layer()
    print 'Joining %s' % (fc_label,)
    arcpy.SpatialJoin_analysis(
        target_path, memory_path(ftl_name), memory_path(join_name),
        field_mapping=field_mappings,
        match_option='CONTAINS' if is_linear else 'INTERSECT')

    # Rename the count field.
    arcpy.AlterField_management(
        memory_path(join_name), 'Join_Count', fc_name + 'Count',
        fc_label + ' Count')

    # Remove the TARGET_FID field.
    arcpy.DeleteField_management(memory_path(join_name), 'TARGET_FID')

    # Divide scores for linear features by the total length.
    if is_linear:
        print 'Completing length-weighting for %s scores' % (fc_label,)
        for field in arcpy.ListFields(
                memory_path(join_name), score_wildcard):
            arcpy.CalculateField_management(
                memory_path(join_name), field.name,
                'None if !%s! is None else !%s! / !LENGTH!' % (
                    field.name, field.name), 'PYTHON')

        # Rename the length field.
        arcpy.AlterField_management(
            memory_path(join_name), 'LENGTH', fc_name + 'Length',
            fc_label + ' Total Length')

    # Clean up join feature class, and create new target path.
    target_path = memory_path(join_name)

# Remove the old results, if they exist.
if arcpy.Exists(RESULT_PATH):
    arcpy.Delete_management(RESULT_PATH)

# Save the new results.
print 'Saving results to %s' % (RESULT_PATH,)
results_workspace, results_name = os.path.split(RESULT_PATH)
arcpy.FeatureClassToFeatureClass_conversion(
    target_path, results_workspace, results_name)
