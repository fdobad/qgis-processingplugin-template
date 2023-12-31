# -*- coding: utf-8 -*-
"""
/***************************************************************************
 ProcessingPluginClass
                                 A QGIS plugin
 Description of the p p
 Generated by Plugin Builder: http://g-sherman.github.io/Qgis-Plugin-Builder/
                              -------------------
        begin                : 2023-07-12
        copyright            : (C) 2023 by fdo
        email                : fbadilla@ing.uchile.cl
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

__author__ = "fdo"
__date__ = "2023-07-12"
__copyright__ = "(C) 2023 by fdo"


# noinspection PyPep8Naming
def classFactory(iface):  # pylint: disable=invalid-name
    """Load ProcessingPluginClass class from file ProcessingPluginClass.

    :param iface: A QGIS interface instance.
    :type iface: QgsInterface
    """
    #
    from .ProcessingPluginModule import ProcessingPluginClassPlugin

    return ProcessingPluginClassPlugin()
