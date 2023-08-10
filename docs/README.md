     Forest Fires Advanced Analytics & Management Tools
        
           QGIS Processing Plugin Template
                
            by fire2a.com research centre

                     version=

[This repo](https://github.com/fdobad/qgis-processingplugin-template) is a template for QGIS processing toolbox [plugins](https://plugins.qgis.org).

Its main content is a proof-of-concept integration between QGIS rasters and a knapsack optimization MIP model.

Users can create a new raster layer that selects the most valuable pixels in a raster, according to a capacity constraint defined by another -optional- raster and a fractional ratio.

This can be achieved in four ways:
- Graphically on the [processing toolbox](https://docs.qgis.org/latest/en/docs/user_manual/processing/toolbox.html) interface, 
- On the [command line](https://docs.qgis.org/latest/en/docs/user_manual/processing/standalone) using `$ qgis_process`
- Or in python scripts [qgis console](#script-in-qgis-console) or [standalone](https://raw.githubusercontent.com/fdobad/qgis-processingplugin-template/main/standalone.py).

Finally several solvers can be used (cbc, glpk, cplex_direct, ipopt, TODO gurobi, scipy), thanks to the MIP being modeled and solved through [pyomo](http://www.pyomo.org). Though is up to the user to install each solver, the plugin checks for availability before displaying them in the solver chooser comboBox. Also a solver options string is optionally configurable (i.e., set precision and time limits)

__Installation instructions [here](./plugin_installation.md)__  
__QGIS-plugin-repo [link](./plugins.xml)__  

| screenshot |
| --- |
|<img src="img/screenshot.png"  alt='cannot load image' height=400px >|

# Usage
## Graphical
1. Open QGIS Processing Toolbox (the cog icon)
2. Type or navigate to: Fire2a > Raster Knapsack Optimization
3. Select one or two layers, input the capacity ratio
4. Click Run

## Script in QGIS Console
```
from qgis import processing
result = processing.run(
    "Fire2a:Raster Knapsack Optimization",
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
QgsProject.instance().addMapLayer(result['OUTPUT_layer'])
```

