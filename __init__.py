# -*- coding: utf-8 -*-
"""
/***************************************************************************
 geobricks_qgis_plugin_faostat
                                 A QGIS plugin
 Download FAOSTAT data to produce thematic maps.
                             -------------------
        begin                : 2015-11-04
        copyright            : (C) 2015 by Geobricks
        email                : guido.barbaglia@geobricks.org
        git sha              : $Format:%H$
 ***************************************************************************/

/***************************************************************************
 *                                                                         *
 *   This program is free software; you can redistribute it and/or modify  *
 *   it under the terms of the GNU General Public License as published by  *
 *   the Free Software Foundation; either version 2 of the License, or     *
 *   (at your option) any later version.                                   *
 *                                                                         *
 ***************************************************************************/
 This script initializes the plugin, making it known to QGIS.
"""


# noinspection PyPep8Naming
def classFactory(iface):  # pylint: disable=invalid-name
    """Load geobricks_qgis_plugin_faostat class from file geobricks_qgis_plugin_faostat.

    :param iface: A QGIS interface instance.
    :type iface: QgsInterface
    """
    #
    from .geobricks_qgis_plugin_faostat import geobricks_qgis_plugin_faostat
    return geobricks_qgis_plugin_faostat(iface)
