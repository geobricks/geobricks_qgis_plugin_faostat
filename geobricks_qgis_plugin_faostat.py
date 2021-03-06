# -*- coding: utf-8 -*-
"""
/***************************************************************************
 geobricks_qgis_plugin_faostat
                                 A QGIS plugin
 Download FAOSTAT data to produce thematic maps.
                              -------------------
        begin                : 2015-11-04
        git sha              : $Format:%H$
        copyright            : (C) 2015 by Geobricks
        email                : guido.barbaglia@geobricks.org
 ***************************************************************************/

/***************************************************************************
 *                                                                         *
 *   This program is free software; you can redistribute it and/or modify  *
 *   it under the terms of the GNU General Public License as published by  *
 *   the Free Software Foundation; either version 2 of the License, or     *
 *   (at your option) any later version.                                   *
 *                                                                         *
 ***************************************************************************/
"""
import os.path

from PyQt4.QtCore import QSettings
from PyQt4.QtCore import QTranslator
from PyQt4.QtCore import qVersion
from PyQt4.QtCore import QCoreApplication
from PyQt4.QtGui import QAction
from PyQt4.QtGui import QIcon
from PyQt4.QtGui import QFileDialog
from PyQt4.QtCore import *
from PyQt4.QtGui import QAction
from PyQt4.QtGui import QIcon
from PyQt4.QtGui import QFileDialog
from qgis.gui import QgsMessageBar
from PyQt4.QtGui import QLabel
from PyQt4.QtGui import QVBoxLayout
from PyQt4.QtGui import QHBoxLayout
from PyQt4.QtGui import QSizePolicy
from PyQt4.QtGui import QComboBox
from PyQt4.QtGui import QCheckBox
from PyQt4.QtGui import QLineEdit
from PyQt4.QtGui import QWidget
from PyQt4.QtGui import QPushButton
from PyQt4.QtGui import QProgressBar
from qgis.core import QgsMessageLog
from qgis.core import QgsMapLayerRegistry
from geobricks_qgis_plugin_faostat_dialog import geobricks_qgis_plugin_faostatDialog
from geobricks_faostat_connector import get_data
from geobricks_faostat_connector import get_items
from geobricks_faostat_connector import get_elements
from geobricks_faostat_connector import get_domains
from geobricks_faostat_connector import get_groups
from geobricks_join_layer_utils import copy_layer
from qgis.core import QgsVectorLayer
from qgis.core import QgsField
from PyQt4.QtCore import QVariant
from qgis.core import QgsFeature
from qgis.core import QgsRendererRangeV2LabelFormat
from qgis.core import QgsField
from qgis.core import QgsFeature
from qgis.core import QgsStyleV2
from qgis.core import QgsVectorLayer
from qgis.core import QgsGraduatedSymbolRendererV2
from qgis.core import QgsSymbolV2


class geobricks_qgis_plugin_faostat:

    def __init__(self, iface):
        self.iface = iface
        self.layout = QVBoxLayout()
        self.cbGroups = QComboBox()
        self.cbDomains = QComboBox()
        self.cbElements = QComboBox()
        self.cbItems = QComboBox()
        self.download_folder = QLineEdit()
        try:
            if self.last_download_folder is not None:
                self.download_folder.setText(self.last_download_folder)
        except:
            self.last_download_folder = None
        self.download_folder_button = QPushButton(self.tr('...'))
        self.download_folder_button.clicked.connect(self.select_output_file)
        self.progress = QProgressBar()
        self.add_to_canvas = QCheckBox(self.tr('Add output layer to canvas'))
        self.start_download_button = QPushButton(self.tr('Start Download'))
        self.start_download_button.clicked.connect(self.download_data)
        self.progress_label = QLabel('<b>' + self.tr('Progress') + '</b>')
        self.bar = QgsMessageBar()
        self.plugin_dir = os.path.dirname(__file__)
        locale = QSettings().value('locale/userLocale')[0:2]
        locale_path = os.path.join(
            self.plugin_dir,
            'i18n',
            'geobricks_qgis_plugin_faostat_{}.qm'.format(locale))
        if os.path.exists(locale_path):
            self.translator = QTranslator()
            self.translator.load(locale_path)
            if qVersion() > '4.3.3':
                QCoreApplication.installTranslator(self.translator)
        self.dlg = geobricks_qgis_plugin_faostatDialog()
        self.actions = []
        self.menu = self.tr('FAOSTAT Data Downloader')
        self.toolbar = self.iface.addToolBar('geobricks_qgis_plugin_faostat')
        self.toolbar.setObjectName('geobricks_qgis_plugin_faostat')
        self.initialized = False

    def run(self):

        # Build UI
        self.build_ui()

        # Populate domains
        groups = get_groups()
        for group in groups:
            self.cbGroups.addItem(group['label'], group['code'])

        # Test message bar
        self.bar.pushMessage(None, str(len(groups)) + self.tr(' groups added'), level=QgsMessageBar.INFO)

    def build_ui(self):

        # Reset layout
        self.layout = QVBoxLayout()

        # Groups
        lbl_0 = QLabel('<b>' + self.tr('Groups') + '</b>')
        self.cbGroups.addItem(self.tr('Please select a groups...'))
        self.cbGroups.activated[str].connect(self.on_groups_change)

        # Domains
        lbl_1 = QLabel('<b>' + self.tr('Domains') + '</b>')
        self.cbDomains.addItem(self.tr('Please select a group to populate this combo-box...'))
        self.cbDomains.activated[str].connect(self.on_domain_change)

        # Elements
        lbl_2 = QLabel('<b>' + self.tr('Elements') + '</b>')
        self.cbElements.addItem(self.tr('Please select a domain to populate this combo-box...'))

        # Items
        lbl_3 = QLabel('<b>' + self.tr('Items') + '</b>')
        self.cbItems.addItem(self.tr('Please select a domain to populate this combo-box...'))

        # Download Folder
        lbl_4 = QLabel('<b>' + self.tr('Download Folder') + '</b>')
        download_folder_widget = QWidget()
        download_folder_layout = QHBoxLayout()
        download_folder_widget.setLayout(download_folder_layout)
        download_folder_layout.addWidget(self.download_folder)
        download_folder_layout.addWidget(self.download_folder_button)

        # Progress bar
        self.progress.setValue(0)

        # Add to canvas
        self.add_to_canvas.toggle()

        # Message bar
        self.bar.setSizePolicy(QSizePolicy.Minimum, QSizePolicy.Fixed)
        self.layout.addWidget(self.bar)

        # Add widgets to layout
        self.layout.addWidget(lbl_0)
        self.layout.addWidget(self.cbGroups)
        self.layout.addWidget(lbl_1)
        self.layout.addWidget(self.cbDomains)
        self.layout.addWidget(lbl_2)
        self.layout.addWidget(self.cbElements)
        self.layout.addWidget(lbl_3)
        self.layout.addWidget(self.cbItems)
        self.layout.addWidget(lbl_4)
        self.layout.addWidget(download_folder_widget)
        self.layout.addWidget(self.add_to_canvas)
        self.layout.addWidget(self.start_download_button)
        self.layout.addWidget(self.progress_label)
        self.layout.addWidget(self.progress)

        # Set layout
        self.dlg.setLayout(self.layout)

        # Show dialog
        self.dlg.show()

    def download_data(self):

        # Get user selection
        group_code = self.cbGroups.itemData(self.cbGroups.currentIndex())
        domain_code = self.cbDomains.itemData(self.cbDomains.currentIndex())
        element_code = self.cbElements.itemData(self.cbElements.currentIndex())
        item_code = self.cbItems.itemData(self.cbItems.currentIndex())
        download_folder = self.download_folder.text()

        # Check selection
        if group_code is None:
            self.bar.pushMessage(None, self.tr('Please select a group'), level=QgsMessageBar.CRITICAL)
        elif domain_code is None:
            self.bar.pushMessage(None, self.tr('Please select a domain'), level=QgsMessageBar.CRITICAL)
        elif element_code is None:
            self.bar.pushMessage(None, self.tr('Please select an element'), level=QgsMessageBar.CRITICAL)
        elif item_code is None:
            self.bar.pushMessage(None, self.tr('Please select an item'), level=QgsMessageBar.CRITICAL)
        elif download_folder is None or len(download_folder) == 0:
            self.bar.pushMessage(None, self.tr('Please select a download folder'), level=QgsMessageBar.CRITICAL)
        else:
            # Get data
            data = get_data(domain_code, element_code, item_code)
            # Notify the user
            self.bar.pushMessage(None, self.tr('Downloaded rows: ') + str(len(data)), level=QgsMessageBar.INFO)
            # Layer name
            layer_name = self.cbItems.currentText().replace(' ', '_') + '_' + self.cbElements.currentText().replace(' ', '_')
            folder_name = os.path.join(download_folder, group_code, domain_code)
            if not os.path.exists(folder_name):
                os.makedirs(folder_name)
            # Copy template layer
            output_file = copy_layer(folder_name, layer_name)
            layer = QgsVectorLayer(output_file, 'layer_name', 'ogr')
            # Add all the years to the layer
            feature_idx = 64
            year_to_be_shown = 2014
            number_of_nulls = 0
            for year in range(2014, 1960, -1):
                progress = (1 + (feature_idx - 64)) * 1.86
                self.progress.setValue(progress)
                self.progress_label.setText('<b>' + self.tr('Progress') + ': ' + '</b> ' + self.tr('Adding Year ') + str(year))
                year_data = self.get_year_data(data, year)
                layer.dataProvider().addAttributes([QgsField(str(year), QVariant.Double)])
                if len(year_data) > 0:
                    layer.startEditing()
                    for feature in layer.getFeatures():
                        if feature['FAOSTAT'] is not None:
                            feature_code = str(feature['FAOSTAT'])
                            for d in year_data:
                                data_code = str(d['code'])
                                if data_code == feature_code:
                                    value = d['value']
                                    layer.changeAttributeValue(feature.id(), (feature_idx), float(value))
                                    tmp_feature = QgsFeature()
                                    tmp_feature.setAttributes([float(value)])
                                    layer.dataProvider().addFeatures([tmp_feature])
                                    if value is None:
                                        number_of_nulls += 1
                    layer.commitChanges()
                else:
                    year_to_be_shown -= 1
                feature_idx += 1
            # Add layer to canvas
            if self.add_to_canvas.isChecked():
                renderer = self.create_join_renderer(layer, str(year_to_be_shown), 11, QgsGraduatedSymbolRendererV2.Pretty)
                l = QgsVectorLayer(output_file, layer_name + '(' + str(year_to_be_shown) + ')', 'ogr')
                r = renderer.clone()
                r.setClassAttribute(str(year_to_be_shown))
                l.setRendererV2(r)
                QgsMapLayerRegistry.instance().addMapLayer(l)
                self.iface.legendInterface().setLayerVisible(l, True)
            # Close pop-up
            self.dlg.close()

    def create_join_renderer(self, layer, field, classes, mode, color='PuBu'):
        symbol = QgsSymbolV2.defaultSymbol(layer.geometryType())
        style = QgsStyleV2().defaultStyle()
        colorRamp = style.colorRampRef(color)
        renderer = QgsGraduatedSymbolRendererV2.createRenderer(layer, field, classes, mode, symbol, colorRamp)
        label_format = self.create_join_label_format(2)
        renderer.setLabelFormat(label_format)
        return renderer

    def create_join_label_format(self, precision):
        format = QgsRendererRangeV2LabelFormat()
        template = '%1 - %2'
        format.setFormat(template)
        format.setPrecision(precision)
        format.setTrimTrailingZeroes(True)
        return format

    def get_year_data(self, data, year):
        out = []
        for d in data:
            if d['year'] == str(year):
                out.append(d)
        return out

    def on_groups_change(self, text):

        # Get selected group code
        group_code = self.cbGroups.itemData(self.cbGroups.currentIndex())

        # Update domains list
        domains = get_domains(group_code)
        self.cbDomains.clear()
        self.cbDomains.addItem(self.tr('Please select a domain'))
        for domain in domains:
            self.cbDomains.addItem(domain['label'], domain['code'])

    def on_domain_change(self, text):

        # Get selected domain code
        domain_code = self.cbDomains.itemData(self.cbDomains.currentIndex())

        # Check domain code
        if domain_code is not None:

            # Update elements list
            try:
                elements = get_elements(domain_code)
                self.cbElements.clear()
                self.cbElements.addItem(self.tr('Please select an element'))
                for element in elements:
                    self.cbElements.addItem(element['label'], element['code'])
            except ValueError:
                self.bar.pushMessage(None, self.tr('No elements available for this domain. Please select another domain.'), level=QgsMessageBar.CRITICAL)

            # Update items list
            try:
                items = get_items(domain_code)
                self.cbItems.clear()
                self.cbItems.addItem(self.tr('Please select an item'))
                for item in items:
                    self.cbItems.addItem(item['label'], item['code'])
            except:
                self.bar.pushMessage(None, self.tr('No items available for this domain. Please select another domain.'), level=QgsMessageBar.CRITICAL)

        else:
            self.bar.pushMessage(None, self.tr('No domain selected. Please select a domain.'), level=QgsMessageBar.CRITICAL)

    def tr(self, message):
        return QCoreApplication.translate('geobricks_qgis_plugin_faostat', message)

    def add_action(self, icon_path, text, callback, enabled_flag=True, add_to_menu=True, add_to_toolbar=True,
                   status_tip=None, whats_this=None, parent=None):
        icon = QIcon(icon_path)
        action = QAction(icon, text, parent)
        action.triggered.connect(callback)
        action.setEnabled(enabled_flag)
        if status_tip is not None:
            action.setStatusTip(status_tip)
        if whats_this is not None:
            action.setWhatsThis(whats_this)
        if add_to_toolbar:
            self.toolbar.addAction(action)
        if add_to_menu:
            self.iface.addPluginToMenu(
                self.menu,
                action)
        self.actions.append(action)
        return action

    def initGui(self):
        icon_path = ':/plugins/geobricks_qgis_plugin_faostat/icon.png'
        self.add_action(
            icon_path,
            text=self.tr('FAOSTAT Data Downloader'),
            callback=self.run,
            parent=self.iface.mainWindow())

    def unload(self):
        for action in self.actions:
            self.iface.removePluginMenu(
                self.tr(self.tr('FAOSTAT Data Downloader')),
                action)
            self.iface.removeToolBarIcon(action)
        del self.toolbar

    def select_output_file(self):
        filename = QFileDialog.getExistingDirectory(self.dlg, self.tr('Select Folder'))
        self.last_download_folder = filename
        self.download_folder.setText(self.last_download_folder)
