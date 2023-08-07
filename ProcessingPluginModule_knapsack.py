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
__version__ = "$Format:%H$"

from contextlib import redirect_stderr, redirect_stdout
from functools import reduce
from io import StringIO
from os import sep
from pathlib import Path
from time import sleep

import numpy as np
from grassprovider.Grass7Utils import Grass7Utils
from osgeo import gdal
from pandas import DataFrame
from processing.tools.system import getTempFilename
from pyomo import environ as pyo
from pyomo.opt import SolverFactory, SolverStatus, TerminationCondition
from qgis.core import (Qgis, QgsFeatureSink, QgsMessageLog, QgsProcessing,
                       QgsProcessingAlgorithm, QgsProcessingException,
                       QgsProcessingFeedback, QgsProcessingParameterDefinition,
                       QgsProcessingParameterEnum,
                       QgsProcessingParameterFeatureSink,
                       QgsProcessingParameterFeatureSource,
                       QgsProcessingParameterField,
                       QgsProcessingParameterFileDestination,
                       QgsProcessingParameterNumber,
                       QgsProcessingParameterRasterDestination,
                       QgsProcessingParameterRasterLayer,
                       QgsProcessingParameterString, QgsProject,
                       QgsRasterBlock, QgsRasterFileWriter)
from qgis.PyQt.QtCore import QByteArray, QCoreApplication
from scipy import stats

SOLVER = {
    "cbc": "ratioGap=0.001 seconds=300",
    "glpk": "mipgap=0.001 tmlim=300",
    "ipopt": "",
    "gurobi": "mipgap=0.001 TimeLimit=300",
    "cplex_direct": "mipgap=0.001 timelimit=300",
    "scipy.fsolve": "",
    "scipy.newton": "",
    "scipy.root": "",
    "scipy.secant-newton": "",
}


class ProcessingPluginClassAlgorithm_knapsack(QgsProcessingAlgorithm):
    """
    This is an example algorithm that takes a vector layer and
    creates a new identical one.

    It is meant to be used as an example of how to create your own
    algorithms and explain methods and variables used to do it. An
    algorithm like this will be available in all elements, and there
    is not need for additional work.

    All Processing algorithms should extend the QgsProcessingAlgorithm
    class.
    """

    # Constants used to refer to parameters and outputs. They will be
    # used when calling the algorithm from another algorithm, or when
    # calling from the QGIS console.
    OUTPUT_layer = "OUTPUT_layer"
    OUTPUT_csv = "OUTPUT_csv"
    INPUT_value = "INPUT_value"
    INPUT_weight = "INPUT_weight"
    INPUT_ratio = "INPUT_ratio"

    def initAlgorithm(self, config):
        """
        Here we define the inputs and output of the algorithm, along
        with some other properties.
        """
        # value
        self.addParameter(
            QgsProcessingParameterRasterLayer(
                name=self.INPUT_value,
                description=self.tr("Values layer (if blank 0's will be used)"),
                defaultValue=[QgsProcessing.TypeRaster],
                optional=True,
            )
        )
        # weight
        self.addParameter(
            QgsProcessingParameterRasterLayer(
                name=self.INPUT_weight,
                description=self.tr("Weights layer (if blank 1's will be used)"),
                defaultValue=[QgsProcessing.TypeRaster],
                optional=True,
            )
        )
        # ratio double
        qppn = QgsProcessingParameterNumber(
            name=self.INPUT_ratio,
            description=self.tr("Capacity ratio (1 = weight.sum)"),
            type=QgsProcessingParameterNumber.Double,
            defaultValue=0.069,
            optional=False,
            minValue=0.0,
            maxValue=1.0,
        )
        qppn.setMetadata({"widget_wrapper": {"decimals": 3}})
        self.addParameter(qppn)

        # QgsProcessingParameterRasterDestination(name: str, description: str = '', defaultValue: Any = None, optional: bool = False, createByDefault: bool = True)
        self.addParameter(
            # QgsProcessingParameterRasterDestination(
            RasterDestinationGpkg(self.OUTPUT_layer, self.tr("Output layer"))
        )
        # , defaultValue='output.gpkg' pierde el lugar tmp

        # QgsProcessingParameterFileDestination(name: str, description: str = '', fileFilter: str = '', defaultValue: Any = None, optional: bool = False, createByDefault: bool = True)
        defaultValue = QgsProject().instance().absolutePath()
        defaultValue = defaultValue + sep + "statistics.csv" if defaultValue != "" else None
        qparamfd = QgsProcessingParameterFileDestination(
            name=self.OUTPUT_csv,
            description=self.tr("CSV statistics file output (overwrites!)"),
            fileFilter="CSV files (*.csv)",
            defaultValue=defaultValue,
        )
        qparamfd.setMetadata({"widget_wrapper": {"dontconfirmoverwrite": True}})
        self.addParameter(qparamfd)

        # check if solver is available
        solver_available = [False] * len(SOLVER)
        for i, solver in enumerate(SOLVER):
            if SolverFactory(solver).available():
                solver_available[i] = True
        # QgsProcessingParameterEnum(name: str, description: str = '', options: Iterable[str] = [], allowMultiple: bool = False, defaultValue: Any = None, optional: bool = False)
        # self.addParameter(
        #     QgsProcessingParameterEnum(
        #         name="SOLVER",
        #         description="Available Solvers",
        #         options=[solver for i, solver in enumerate(SOLVER) if solver_available[i]],
        #         defaultValue=0,
        #         optional=False,
        #     )
        # )

        # gsProcessingParameterString(name: str, description: str = '', defaultValue: Any = None, multiLine: bool = False, optional: bool = False)
        qpps = QgsProcessingParameterString(
            name="SOLVER",
            description="(Available) solvers: (default) options_string",
        )
        qpps.setMetadata(
            {
                "widget_wrapper": {
                    "value_hints": [f"{k}: {v}" for i, (k, v) in enumerate(SOLVER.items()) if solver_available[i]],
                    "setEditable": True,
                }
            }
        )
        qpps.setFlags(qpps.flags() | QgsProcessingParameterDefinition.FlagAdvanced)
        self.addParameter(qpps)

        qpps2 = QgsProcessingParameterString(
            name="CUSTOM_OPTIONS_STRING",
            description="Override options_string (" " (single space) to use None)",
            defaultValue="",
            optional=True,
        )
        qpps2.setFlags(qpps2.flags() | QgsProcessingParameterDefinition.FlagAdvanced)
        self.addParameter(qpps2)

    def processAlgorithm(self, parameters, context, feedback):
        # feedback.pushCommandInfo(f"processAlgorithm START")
        # feedback.pushCommandInfo(f"parameters {parameters}")
        # feedback.pushCommandInfo(f"context args: {context.asQgisProcessArguments()}")

        value_layer = self.parameterAsRasterLayer(parameters, self.INPUT_value, context)
        value_data = get_raster_data(value_layer)
        value_nodata = get_raster_nodata(value_layer)
        value_map_info = get_raster_info(value_layer)

        weight_layer = self.parameterAsRasterLayer(parameters, self.INPUT_weight, context)
        weight_data = get_raster_data(weight_layer)
        weight_nodata = get_raster_nodata(weight_layer)
        weight_map_info = get_raster_info(weight_layer)

        if value_layer and weight_layer:
            assert (
                value_map_info["width"] == weight_map_info["width"]
                and value_map_info["height"] == weight_map_info["height"]
                and value_map_info["cellsize_x"] == weight_map_info["cellsize_x"]
                and value_map_info["cellsize_y"] == weight_map_info["cellsize_y"]
            ), feedback.reportError("Layers must have the same width, height and cellsizes")
            width, height, extent, crs, _, _ = value_map_info.values()
        elif value_layer and not weight_layer:
            width, height, extent, crs, _, _ = value_map_info.values()
            weight_data = np.ones(height * width)
        elif not value_layer and weight_layer:
            width, height, extent, crs, _, _ = weight_map_info.values()
            value_data = np.zeros(height * width)

        N = width * height

        feedback.pushCommandInfo(f"width: {width}, height: {height}, extent: {extent}, crs: {crs}")
        feedback.pushCommandInfo(
            f"value !=0: {np.any(value_data!=0)}\n"
            f" nodata: {value_nodata}\n"
            f" preview: {value_data}\n"
            f" stats: {stats.describe(value_data)}\n"
        )
        feedback.pushCommandInfo(
            f"weight !=1: {np.any(weight_data!=1)}\n"
            f" nodata: {weight_nodata}\n"
            f" preview: {weight_data}\n"
            f" stats: {stats.describe(weight_data)}\n"
        )

        if isinstance(value_nodata, list):
            feedback.pushError(f"value_nodata: {value_nodata}")
        if isinstance(weight_nodata, list):
            feedback.pushError(f"weight_nodata: {weight_nodata}")

        no_indexes = reduce(
            np.union1d,
            (
                np.where(value_data == value_nodata)[0],
                np.where(value_data == 0)[0],
                np.where(weight_data == weight_nodata)[0],
            ),
        )
        feedback.pushCommandInfo(f"discarded pixels (no_indexes): {len(no_indexes)/N:.2%}")
        mask = np.ones(N, dtype=bool)
        mask[no_indexes] = False

        ratio = self.parameterAsDouble(parameters, self.INPUT_ratio, context)
        weight_sum = weight_data[mask].sum()
        capacity = round(weight_sum * ratio)
        feedback.pushCommandInfo(f"ratio {ratio}, weight_sum: {weight_sum}, capacity: {capacity}")

        feedback.setProgress(10)
        feedback.setProgressText(f"rasters processed 10%")

        # def bounds_rule(m, i):
        #     if i in no_indexes:
        #         return (0, 0)
        #     return (0, 1)

        m = pyo.ConcreteModel()
        # m.N = pyo.RangeSet(0, width * height - 1) # w*h - len(fix_list)
        m.N = pyo.RangeSet(0, N - len(no_indexes) - 1)
        m.Cap = pyo.Param(initialize=capacity)
        # m.We = pyo.Param(m.N, within=pyo.Reals, initialize=weight_data)
        # m.Va = pyo.Param(m.N, within=pyo.Reals, initialize=value_data)
        m.We = pyo.Param(m.N, within=pyo.Reals, initialize=weight_data[mask])
        m.Va = pyo.Param(m.N, within=pyo.Reals, initialize=value_data[mask])
        # m.X = pyo.Var(m.N, within=pyo.Binary, bounds=bounds_rule)
        m.X = pyo.Var(m.N, within=pyo.Binary)
        obj_expr = pyo.sum_product(m.X, m.Va, index=m.N)
        m.obj = pyo.Objective(expr=obj_expr, sense=pyo.maximize)

        def capacity_rule(m):
            return pyo.sum_product(m.X, m.We, index=m.N) <= m.Cap

        m.capacity = pyo.Constraint(rule=capacity_rule)

        solver_string = self.parameterAsString(parameters, "SOLVER", context)
        feedback.pushWarning(f"solver_string:{solver_string}")
        solver, options_string = solver_string.split(": ", 1) if ": " in solver_string else (solver_string, "")
        feedback.pushWarning(f"solver:{solver}, options_string:{options_string}")

        if len(custom_options:= self.parameterAsString(parameters, "CUSTOM_OPTIONS_STRING", context))>0:
            if custom_options == " ":
                options_string = None
            else:
                options_string = custom_options
        feedback.pushWarning(f"re options_string:{options_string}")

        opt = SolverFactory(solver)
        feedback.setProgress(20)
        feedback.setProgressText("pyomo model built, solver object created 20%")

        pyomo_std_feedback = FileLikeFeedback(feedback, True)
        pyomo_err_feedback = FileLikeFeedback(feedback, False)
        with redirect_stdout(pyomo_std_feedback), redirect_stderr(pyomo_err_feedback):
            if options_string:
                results = opt.solve(m, tee=True, options_string=options_string)
            else:
                results = opt.solve(m, tee=True)
            # TODO
            # # Stop the algorithm if cancel button has been clicked
            # if feedback.isCanceled():

        status = results.solver.status
        termCondition = results.solver.termination_condition

        if status in [SolverStatus.error, SolverStatus.aborted, SolverStatus.unknown]:
            feedback.reportError(f"Solver status: {status}, termination condition: {termCondition}")
            return {self.OUTPUT_layer: None, self.OUTPUT_csv: None}
        if termCondition in [
            TerminationCondition.infeasibleOrUnbounded,
            TerminationCondition.infeasible,
            TerminationCondition.unbounded,
        ]:
            feedback.reportError(f"Optimization problem is {termCondition}. No output is generated.")
            return {self.OUTPUT_layer: None, self.OUTPUT_csv: None}
        if not termCondition == TerminationCondition.optimal:
            feedback.pushWarning("Output is generated for a non-optimal solution.")

        feedback.setProgress(80)
        feedback.setProgressText("pyomo model solved 80%")

        response = np.array([pyo.value(m.X[i], exception=False) for i in m.X])
        response[response == None] = 2
        response = response.astype(np.int16)
        base = -np.ones(N, dtype=np.int16)
        base[mask] = response
        base.resize(height, width)

        # dens = value_data / weight_data
        # asort = np.argsort(dens)
        # feedback.pushCommandInfo("c,i,j,x,wei,val,den")
        # for c in asort:
        #     i, j = id2xy(c, width, height)
        #     feedback.pushCommandInfo(
        #             f"px:{c}, i:{i}, j:{j}, x:{m.X[i + j * width].value}, w:{weight_data[c]:.4f}, v:{value_data[c]:.4f}, d:{value_data[c] / weight_data[c]:.4f}"
        #     )

        output_file = self.parameterAsFileOutput(parameters, self.OUTPUT_csv, context)
        feedback.pushCommandInfo(f"output_file: {output_file}, type: {type(output_file)}")
        df = DataFrame(np.random.randint(0, 10, (4, 3)), columns=["a", "b", "c"])
        df.to_csv(output_file, index=False)

        output_layer_filename = self.parameterAsOutputLayer(parameters, self.OUTPUT_layer, context)
        feedback.pushCommandInfo(
            # f"output_layer_filename: {output_layer_filename}, type: {type(output_layer_filename)}"
            f"isfile: {Path(output_layer_filename).is_file()}"
            # f"file size:{Path(output_layer_filename).stat().st_size}"
        )
        outFormat = Grass7Utils.getRasterFormatFromFilename(output_layer_filename)
        feedback.pushCommandInfo(f"outFormat: {outFormat}")

        feedback.pushCommandInfo(f"response is !=0: {np.any(response != 0)}")
        array2rasterInt16(
            # response,
            base,
            "knapsack",
            output_layer_filename,
            extent,
            crs,
            nodata=-1,
        )

        feedback.setProgress(100)
        # feedback.pushCommandInfo(f"processAlgorithm END")
        return {self.OUTPUT_layer: output_layer_filename, self.OUTPUT_csv: output_file}

    def name(self):
        """
        Returns the algorithm name, used for identifying the algorithm. This
        string should be fixed for the algorithm, and must not be localised.
        The name should be unique within each provider. Names should contain
        lowercase alphanumeric characters only and no spaces or other
        formatting characters.
        """
        return "Raster Knapsack Optimization"

    def displayName(self):
        """
        Returns the translated algorithm name, which should be used for any
        user-visible display of the algorithm name.
        """
        return self.tr(self.name())

    def group(self):
        """
        Returns the name of the group this algorithm belongs to. This string
        should be localised.
        """
        return self.tr(self.groupId())

    def groupId(self):
        """
        Returns the unique ID of the group this algorithm belongs to. This
        string should be fixed for the algorithm, and must not be localised.
        The group id should be unique within each provider. Group id should
        contain lowercase alphanumeric characters only and no spaces or other
        formatting characters.
        """
        return "Fire A A & M"

    def tr(self, string):
        return QCoreApplication.translate("Processing", string)

    def createInstance(self):
        return ProcessingPluginClassAlgorithm_knapsack()


class RasterDestinationGpkg(QgsProcessingParameterRasterDestination):
    """overrides the defaultFileExtension method to gpkg
    ALTERNATIVE:
    from types import MethodType
    QPPRD = QgsProcessingParameterRasterDestination(self.OUTPUT_layer, self.tr("Output layer"))
    def _defaultFileExtension(self):
        return "gpkg"
    QPPRD.defaultFileExtension = MethodType(_defaultFileExtension, QPPRD)
    """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def defaultFileExtension(self):
        return "gpkg"


def id2xy(idx, w=6, h=4):
    """idx: index, w: width, h:height"""
    return idx % w, idx // w


def get_raster_data(layer):
    """raster layer into numpy array
        slower alternative:
            for i in range(lyr.width()):
                for j in range(lyr.height()):
                    values.append(block.value(i,j))
    # npArr = np.frombuffer( qByteArray)  #,dtype=float)
    # return npArr.reshape( (layer.height(),layer.width()))
    """
    if layer:
        provider = layer.dataProvider()
        block = provider.block(1, layer.extent(), layer.width(), layer.height())
        qByteArray = block.data()
        return np.frombuffer(qByteArray)  # ,dtype=float)


def get_raster_nodata(layer):
    if layer:
        dp = layer.dataProvider()
        if dp.sourceHasNoDataValue(1):
            return dp.sourceNoDataValue(1)


def get_raster_info(layer):
    if layer:
        return {
            "width": layer.width(),
            "height": layer.height(),
            "extent": layer.extent(),
            "crs": layer.crs(),
            "cellsize_x": layer.rasterUnitsPerPixelX(),
            "cellsize_y": layer.rasterUnitsPerPixelY(),
        }


class FileLikeFeedback(StringIO):
    def __init__(self, feedback, std):
        super().__init__()
        self.feedback = feedback
        self.std = std
        if self.std:
            self.print = self.feedback.pushConsoleInfo
        else:
            self.print = self.feedback.pushWarning
        self.feedback.pushWarning(f"{self.std} FileLikeFeedback init")

    def write(self, msg):
        self.feedback.pushWarning(f"{self.std} FileLikeFeedback write")
        super().write(msg)
        self.flush()

    def flush(self):
        # self.feedback.pushConsoleInfo(super().getvalue())
        self.print(super().getvalue())
        super().__init__()
        self.feedback.pushWarning(f"{self.std} FileLikeFeedback flush")


# class FileLikeFeedback:
#     def __init__(self, feedback):
#         super().__init__()
#         self.feedback = feedback
#     def write(self, msg):
#        self.msg+=msg
#     def flush(self):
#        self.feedback.pushConsoleInfo(self.msg)
#        self.msg = ""


def array2rasterInt16(data, name, geopackage, extent, crs, nodata=None):
    """numpy array to gpkg casts to name"""
    data = np.int16(data)
    h, w = data.shape
    bites = QByteArray(data.tobytes())
    block = QgsRasterBlock(Qgis.CInt16, w, h)
    block.setData(bites)
    fw = QgsRasterFileWriter(str(geopackage))
    fw.setOutputFormat("gpkg")
    fw.setCreateOptions(["RASTER_TABLE=" + name, "APPEND_SUBDATASET=YES"])
    provider = fw.createOneBandRaster(Qgis.Int16, w, h, extent, crs)
    provider.setEditable(True)
    provider.writeBlock(block, 1, 0, 0)
    if nodata != None:
        provider.setNoDataValue(1, nodata)
    provider.setEditable(False)
    del provider, fw, block