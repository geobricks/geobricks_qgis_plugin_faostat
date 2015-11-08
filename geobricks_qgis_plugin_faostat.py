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
from PyQt4.QtGui import QMessageBox
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
# TODO: check if all imports are needed
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
        self.cbGroups = QComboBox()
        self.cbDomains = QComboBox()
        self.cbElements = QComboBox()
        self.cbItems = QComboBox()
        self.download_folder = QLineEdit()
        self.download_folder_button = QPushButton(self.tr('...'))
        self.download_folder_button.clicked.connect(self.select_output_file)
        self.progress = QProgressBar()
        self.add_to_canvas = QCheckBox(self.tr('Add output layer to canvas'))
        self.start_download_button = QPushButton(self.tr('Start Download'))
        self.start_download_button.clicked.connect(self.download_data)
        self.progress_label = QLabel('<b>' + self.tr('Progress') + '</b>')
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
        self.bar.pushMessage(None, self.tr('Welcome!'), level=QgsMessageBar.INFO)

    def build_ui(self):

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

        # Widget layout
        layout = QVBoxLayout()

        # Message bar
        self.bar = QgsMessageBar()
        self.bar.setSizePolicy(QSizePolicy.Minimum, QSizePolicy.Fixed)
        layout.addWidget(self.bar)

        # Add widgets to layout
        layout.addWidget(lbl_0)
        layout.addWidget(self.cbGroups)
        layout.addWidget(lbl_1)
        layout.addWidget(self.cbDomains)
        layout.addWidget(lbl_2)
        layout.addWidget(self.cbElements)
        layout.addWidget(lbl_3)
        layout.addWidget(self.cbItems)
        layout.addWidget(lbl_4)
        layout.addWidget(download_folder_widget)
        layout.addWidget(self.add_to_canvas)
        layout.addWidget(self.start_download_button)
        layout.addWidget(self.progress_label)
        layout.addWidget(self.progress)

        # Set layout
        self.dlg.setLayout(layout)

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
            # Notify the user
            self.bar.pushMessage(self.tr('User selection:'), self.tr('Domain: ') + domain_code + ', ' + self.tr('Element: ') + element_code + ', ' + self.tr('Item: ') + item_code, level=QgsMessageBar.INFO)
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
            for year in range(2014, 1960, -1):
                progress = (1 + (feature_idx - 64)) * 1.85
                self.progress.setValue(progress)
                self.progress_label.setText('<b>' + self.tr('Progress') + ': ' + '</b> ' + self.tr('Adding Year ') + str(year))
                year_data = self.get_year_data(data, year)
                layer.dataProvider().addAttributes([QgsField(str(year), QVariant.Double)])
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
                layer.commitChanges()
                feature_idx += 1

            if self.add_to_canvas.isChecked():
                renderer = self.create_join_renderer(layer, '2014', 21, QgsGraduatedSymbolRendererV2.Pretty)
                l = QgsVectorLayer(output_file, layer_name, 'ogr')
                r = renderer.clone()
                r.setClassAttribute('2014')
                l.setRendererV2(r)
                QgsMapLayerRegistry.instance().addMapLayer(l)
                self.iface.legendInterface().setLayerVisible(l, True)

    def create_join_renderer(self, layer, field, classes, mode, color='Blues'):
        symbol = QgsSymbolV2.defaultSymbol(layer.geometryType())
        style = QgsStyleV2().defaultStyle()
        colorRamp = style.colorRampRef(color)
        renderer = QgsGraduatedSymbolRendererV2.createRenderer(layer, field, classes, mode, symbol, colorRamp)
        label_format = self.create_join_label_format(2)
        renderer.setLabelFormat(label_format)
        return renderer

    def create_join_label_format(self, precision):
        format = QgsRendererRangeV2LabelFormat()
        template = '%1 - %2 metres'
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

        # Notify the user
        self.bar.pushMessage(None, self.tr('You have selected "') + text + self.tr('", Group Code: ') + group_code, level=QgsMessageBar.INFO)

        # Update domains list
        domains = get_domains(group_code)
        self.cbDomains.clear()
        self.cbDomains.addItem(self.tr('Please select a domain'))
        for domain in domains:
            self.cbDomains.addItem(domain['label'], domain['code'])

    def on_domain_change(self, text):

        # Get selected domain code
        domain_code = self.cbDomains.itemData(self.cbDomains.currentIndex())

        # Notify the user
        self.bar.pushMessage(None, self.tr('You have selected "') + text + self.tr('", Domain Code: ') + domain_code, level=QgsMessageBar.INFO)

        # Update elements list
        elements = get_elements(domain_code)
        self.cbElements.clear()
        self.cbElements.addItem(self.tr('Please select an element'))
        for element in elements:
            self.cbElements.addItem(element['label'], element['code'])

        # Update items list
        items = get_items(domain_code)
        self.cbItems.clear()
        self.cbItems.addItem(self.tr('Please select an item'))
        for item in items:
            self.cbItems.addItem(item['label'], item['code'])

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

    def update_items_elements(self):
        try:
            domain_name = self.dlg.cbDomain.currentText()
            domain_code = self.domains[domain_name]
            self.update_items(domain_code)
            self.update_elements(domain_code)
        except:
            pass

    def update_items(self, domain_code):
        self.dlg.cbItem.clear()
        data = get_items(domain_code)
        values = []
        values.append(self.tr('Please select an item...'))
        self.elements = {}
        for d in data:
            self.domains[d['label']] = d
            values.append(d['label'])
        self.dlg.cbItem.addItems(values)

    def update_elements(self, domain_code):
        self.dlg.cbElement.clear()
        data = get_elements(domain_code)
        values = []
        values.append(self.tr('Please select an element...'))
        self.elements = {}
        for d in data:
            self.domains[d['label']] = d
            values.append(d['label'])
        self.dlg.cbElement.addItems(values)

    def initialize_domains(self):
        self.dlg.cbDomain.clear()
        data = [
            {
                'name': self.tr('Production: Crops'),
                'id': 'QC'
            },
            {
                'name': self.tr('Production: Crops Processed'),
                'id': 'QD'
            }
        ]
        values = []
        values.append(self.tr('Please select a domain...'))
        self.domains = {}
        for d in data:
            self.domains[d['name']] = d['id']
            values.append(d['name'])
        self.dlg.cbDomain.addItems(values)

    def select_output_file(self):
        filename = QFileDialog.getExistingDirectory(self.dlg, self.tr('Select Folder'))
        self.download_folder.setText(filename)

    def create_layer(self):
        download_path = self.dlg.download_path.text()
        if self.dlg.download_path.text() is None or len(self.dlg.download_path.text()) == 0:
            QMessageBox.critical(None, self.tr('Error'), self.tr('Please insert the download folder'))
        else:
            processed_layers = 0
            self.dlg.progressBar.setValue(processed_layers)
            data = get_data('', '', '')
