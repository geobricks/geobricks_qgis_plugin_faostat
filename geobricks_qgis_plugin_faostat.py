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
from PyQt4.QtCore import QSettings, QTranslator, qVersion, QCoreApplication
from PyQt4.QtGui import QAction, QIcon, QFileDialog
# Initialize Qt resources from file resources.py
import resources
# Import the code for the dialog
from geobricks_qgis_plugin_faostat_dialog import geobricks_qgis_plugin_faostatDialog
from geobricks_faostat_connector import get_items, get_elements
import os.path


class geobricks_qgis_plugin_faostat:
    """QGIS Plugin Implementation."""

    def __init__(self, iface):
        """Constructor.

        :param iface: An interface instance that will be passed to this class
            which provides the hook by which you can manipulate the QGIS
            application at run time.
        :type iface: QgsInterface
        """
        # Save reference to the QGIS interface
        self.iface = iface
        # initialize plugin directory
        self.plugin_dir = os.path.dirname(__file__)
        # initialize locale
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

        # Create the dialog (after translation) and keep reference
        self.dlg = geobricks_qgis_plugin_faostatDialog()

        # Declare instance attributes
        self.actions = []
        self.menu = self.tr(u'&FAOSTAT Data Downloader')
        # TODO: We are going to let the user set this up in a future iteration
        self.toolbar = self.iface.addToolBar(u'geobricks_qgis_plugin_faostat')
        self.toolbar.setObjectName(u'geobricks_qgis_plugin_faostat')

        # TODO: check if there is a better way to handle inizialition
        self.initialized = False

    # noinspection PyMethodMayBeStatic
    def tr(self, message):
        """Get the translation for a string using Qt translation API.

        We implement this ourselves since we do not inherit QObject.

        :param message: String for translation.
        :type message: str, QString

        :returns: Translated version of message.
        :rtype: QString
        """
        # noinspection PyTypeChecker,PyArgumentList,PyCallByClass
        return QCoreApplication.translate('geobricks_qgis_plugin_faostat', message)


    def add_action(
        self,
        icon_path,
        text,
        callback,
        enabled_flag=True,
        add_to_menu=True,
        add_to_toolbar=True,
        status_tip=None,
        whats_this=None,
        parent=None):
        """Add a toolbar icon to the toolbar.

        :param icon_path: Path to the icon for this action. Can be a resource
            path (e.g. ':/plugins/foo/bar.png') or a normal file system path.
        :type icon_path: str

        :param text: Text that should be shown in menu items for this action.
        :type text: str

        :param callback: Function to be called when the action is triggered.
        :type callback: function

        :param enabled_flag: A flag indicating if the action should be enabled
            by default. Defaults to True.
        :type enabled_flag: bool

        :param add_to_menu: Flag indicating whether the action should also
            be added to the menu. Defaults to True.
        :type add_to_menu: bool

        :param add_to_toolbar: Flag indicating whether the action should also
            be added to the toolbar. Defaults to True.
        :type add_to_toolbar: bool

        :param status_tip: Optional text to show in a popup when mouse pointer
            hovers over the action.
        :type status_tip: str

        :param parent: Parent widget for the new action. Defaults None.
        :type parent: QWidget

        :param whats_this: Optional text to show in the status bar when the
            mouse pointer hovers over the action.

        :returns: The action that was created. Note that the action is also
            added to self.actions list.
        :rtype: QAction
        """

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
        """Create the menu entries and toolbar icons inside the QGIS GUI."""

        icon_path = ':/plugins/geobricks_qgis_plugin_faostat/icon.png'
        self.add_action(
            icon_path,
            text=self.tr(u'FAOSTAT Data Downloader'),
            callback=self.run,
            parent=self.iface.mainWindow())


    def unload(self):
        """Removes the plugin menu item and icon from QGIS GUI."""
        for action in self.actions:
            self.iface.removePluginMenu(
                self.tr(u'&FAOSTAT Data Downloader'),
                action)
            self.iface.removeToolBarIcon(action)
        # remove the toolbar
        del self.toolbar


    def update_items_elements(self):

        self.update_items()
        self.update_elements()

    def update_items(self):

        self.dlg.cbItem.clear()

        data = get_items('QC')

        values = []
        self.elements = {}
        for d in data:
            self.domains[d['label']] = d
            values.append(d['label'])

        values.sort()
        self.dlg.cbItem.addItems(values)

    def update_elements(self):

        self.dlg.cbElement.clear()

        data = get_elements('QC')

        values = []
        self.elements = {}
        for d in data:
            self.domains[d['label']] = d
            values.append(d['label'])

        values.sort()
        self.dlg.cbElement.addItems(values)


    def initialize_domains(self):
        self.dlg.cbDomain.clear()

        # TODO: connect to APIs
        data = [
            {
                'name': 'Production - Crops',
                'id': 'QC'
            }
        ]

        # cache codes
        values = []
        self.domains = {}
        for d in data:
            self.domains[d['name']] = d['id']
            values.append(d['name'])

        values.sort()
        self.dlg.cbDomain.addItems(values)

    def select_output_file(self):
        filename = QFileDialog.getExistingDirectory(self.dlg, "Select Folder")
        self.dlg.download_path.setText(filename)

    def run(self):

        # if the interface is initiated
        if self.initialized:
            self.dlg.progressText.setText('')
            self.dlg.progressBar.setValue(0)

        if not self.initialized:
            # dirty check if interface was already initialized
            self.initialized = True

            # initialize selectors
            self.initialize_domains()

            self.update_items_elements()

            self.dlg.cbDomain.currentIndexChanged.connect(self.update_items_elements)

            # add select download folder
            self.dlg.pushButton.clicked.connect(self.select_output_file)

            # on OK and Cancel click
            #self.dlg.buttonBox.accepted.connect(self.process_layers)
            self.dlg.buttonBox.rejected.connect(self.dlg.close)

        # show the dialog
        self.dlg.show()
