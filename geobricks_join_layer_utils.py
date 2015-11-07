import os
import re
import glob
from shutil import copyfile
from PyQt4.QtCore import *
from qgis.core import QgsRendererRangeV2LabelFormat, QgsField, QgsFeature, QgsStyleV2, QgsVectorLayer, QgsGraduatedSymbolRendererV2, QgsSymbolV2


def copy_layer(download_path, indicator_name):

    clean_layer_name = re.sub('\W+', '_', indicator_name)
    output_file = os.path.join(download_path, clean_layer_name + ".shp")
    input_base_path = os.path.join(os.path.dirname(os.path.realpath(__file__)), "resources")

    # copy resource file to output
    # resource_files = glob.glob(os.path.join(input_base_path, "ne_110m_admin_0_*"))
    resource_files = glob.glob(os.path.join(input_base_path, "NaturalEarthFAOSTAT*"))
    for resource_file in resource_files:
        base, extension = os.path.splitext(resource_file)
        copyfile(resource_file, os.path.join(download_path, clean_layer_name + extension))

    return output_file


def create_layer(layer, tmp_layer, data, year, index):

    # TODO: remove hardcoded index
    index += 62

    tmp_data_provider = tmp_layer.dataProvider()
    tmp_layer.startEditing()
    tmp_feature = QgsFeature()

    # Editing output_file

    # add column year
    layer.dataProvider().addAttributes([QgsField(str(year), QVariant.Double)])

    layer.startEditing()

    # TODO: add data check instead of the addedValue boolean?
    addedValue = False
    for feat in layer.getFeatures():
        if feat['faostat'] is not None:
            for d in data:
                code = d['country']['id']
                value = d['Value']
                if code == feat['faostat']:
                    if value:
                        # TODO: automatize the index 5 of feat['FAOSTAT']
                        layer.changeAttributeValue(feat.id(), index, float(value))
                        tmp_feature.setAttributes([float(value)])
                        # TODO add all togheter
                        tmp_data_provider.addFeatures([tmp_feature])
                        addedValue = True
                        break

    # TODO: in teory if addedValue is not present should be removed the column year?
    layer.commitChanges()
    return addedValue


def create_join_renderer(layer, field, classes, mode, color='Blues'):
    symbol = QgsSymbolV2.defaultSymbol(layer.geometryType())
    style = QgsStyleV2().defaultStyle()
    colorRamp = style.colorRampRef(color)
    renderer = QgsGraduatedSymbolRendererV2.createRenderer(layer, field, classes, mode, symbol, colorRamp)
    label_format = create_join_label_format(2)
    renderer.setLabelFormat(label_format)
    return renderer


def create_join_label_format(precision):
    format = QgsRendererRangeV2LabelFormat()
    template="%1 - %2 metres"
    format.setFormat(template)
    format.setPrecision(precision)
    format.setTrimTrailingZeroes(True)
    return format
