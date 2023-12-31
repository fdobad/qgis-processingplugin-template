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
"""

__author__ = "fdo"
__date__ = "2023-07-12"
__copyright__ = "(C) 2023 by fdo"

# This will get replaced with a git SHA1 when you do a git archive

__version__ = "$Format:%H$"

import inspect
import os
import sys

from qgis.core import QgsApplication, QgsProcessingAlgorithm

from .ProcessingPluginModule_provider import ProcessingPluginClassProvider

cmd_folder = os.path.split(inspect.getfile(inspect.currentframe()))[0]

if cmd_folder not in sys.path:
    sys.path.insert(0, cmd_folder)


class ProcessingPluginClassPlugin(object):
    def __init__(self):
        self.provider = None

    def initProcessing(self):
        """Init Processing provider for QGIS >= 3.8."""
        self.provider = ProcessingPluginClassProvider()
        QgsApplication.processingRegistry().addProvider(self.provider)

    def initGui(self):
        self.initProcessing()

    def unload(self):
        QgsApplication.processingRegistry().removeProvider(self.provider)
