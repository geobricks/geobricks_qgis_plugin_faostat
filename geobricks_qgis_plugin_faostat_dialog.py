# -*- coding: utf-8 -*-
"""
/***************************************************************************
 geobricks_qgis_plugin_faostatDialog
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

import os

from PyQt4 import QtGui
from PyQt4 import uic

FORM_CLASS, _ = uic.loadUiType(os.path.join(
    os.path.dirname(__file__), 'geobricks_qgis_plugin_faostat_dialog_base.ui'))


class geobricks_qgis_plugin_faostatDialog(QtGui.QDialog, FORM_CLASS):
    def __init__(self, parent=None):
        super(geobricks_qgis_plugin_faostatDialog, self).__init__(parent)
        self.setupUi(self)
