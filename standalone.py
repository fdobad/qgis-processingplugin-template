#!python3
"""
%autoindent
https://gis.stackexchange.com/a/408738
"""
import sys

from qgis.core import QgsApplication

QgsApplication.setPrefixPath("/usr", True)
qgs = QgsApplication([], False)
qgs.initQgis()

# Append the path where processing plugin can be found
sys.path.append("/usr/share/qgis/python/plugins")

import processing
from processing.core.Processing import Processing

Processing.initialize()

# Append the path where your plugin is
sys.path.append("/home/fdo/.local/share/QGIS/QGIS3/profiles/default/python/plugins/")
# Add your own algorithm provider
from processingpluginmodule.ProcessingPluginModule_provider import \
    ProcessingPluginClassProvider

provider = ProcessingPluginClassProvider()
QgsApplication.processingRegistry().addProvider(provider)

print(processing.algorithmHelp("fire2am:rasterknapsackoptimization"))
sys.exit(0)

result = processing.run(
    "fire2am:rasterknapsackoptimization",
    {
        "INPUT_ratio": 0.06,
        "INPUT_value": "/path/to/raster.any_supported_extension",
        "INPUT_weight": None,
        "OUTPUT_csv": "TEMPORARY_OUTPUT",
        "OUTPUT_layer": "TEMPORARY_OUTPUT",
        "SOLVER": "cbc: ratioGap=0.001 seconds=300",
        "CUSTOM_OPTIONS_STRING": "",
    },
)
print(result)
