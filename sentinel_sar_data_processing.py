#--------------------------------------------------------------------------------------------------------------------------------
# Name:        specific_snap_graph_processing
# Purpose:
#
# Author:      jennifer.mcclelland
#
# Created:     2022
# Copyright:   (c) jennifer.mcclelland 2022
#
# ----This is the main script for sentinel Sar data processing------------------------------------------------------------------- #
# ----This script can be executed in Terminal via "python3 sentinel_sar_data_processing.py --<option>"--------------------------- #
# ----Possible option is 'withGui'----------------------------------------------------------------------------------------------- #
# ----If '--withGui' is set the main function starts a gui to enter the user settings before processing-------------------------- #
# ----Otherwise the main function starts processing immediately------------------------------------------------------------------ #
# ----User Settings 'processingSequence' entry must contain either: 'Coherence', 'Radar Vegetation Index', 'Backscatter', or 'All'#
#--------------------------------------------------------------------------------------------------------------------------------


from controller_modules.create_user_setting_file import CreateUserSetting
from controller_modules.create_user_settings_gui import CreateUserSettingsGui
from controller_modules.geo_position import GeoPosition
from controller_modules.snap_graph_processing import SnapGraphProcessing
from controller_modules.batch_processing import BatchProcessing
from controller_modules.create_input_output import CreateInputOutput
from controller_modules.pyFunc_queries import PyFuncQueries
from controller_modules.specific_snap_graph_processing import SpecificSnapGraphProcessing

import os
import sys

def executeBySettings(userSettings):

    snapGraphProcessing = SnapGraphProcessing()
    specificSnapGraphProcessing = SpecificSnapGraphProcessing(os.getcwd() + "/snap_graph_files/", userSettings.dataPath)

    # ################Ensure final output format is GeoTiff###############################
    snapGraphProcessing.setNewOperatorParameter(specificSnapGraphProcessing.simpleSubGraphs + "terrain_correction.xml",
                                                "Write", "formatName", "GeoTIFF")

#    Ensure terrain projection is set
    snapGraphProcessing.setNewOperatorParameter(specificSnapGraphProcessing.mainCalcGraphs + "calc_coherence.xml",
                                                "Terrain-Correction", "mapProjection",
                                                specificSnapGraphProcessing.terrainProjection)
    snapGraphProcessing.setNewOperatorParameter(specificSnapGraphProcessing.mainCalcGraphs + "calc_coherence_no_deburst.xml",
                                                "Terrain-Correction", "mapProjection",
                                                specificSnapGraphProcessing.terrainProjection)
    snapGraphProcessing.setNewOperatorParameter(specificSnapGraphProcessing.mainCalcGraphs + "calc_backscatter.xml",
                                                "Terrain-Correction", "mapProjection",
                                                specificSnapGraphProcessing.terrainProjection)
    snapGraphProcessing.setNewOperatorParameter(specificSnapGraphProcessing.simpleSubGraphs + "terrain_correction.xml",
                                                "Terrain-Correction", "mapProjection",
                                                specificSnapGraphProcessing.terrainProjection)

    productTypeSlc = 'SLC'
    productTypeGrd = 'GRD'

    if userSettings.currentAoi == "" or userSettings.currentAoi is None:
        return
    if userSettings.calculationStartDate == "" or userSettings.calculationEndDate == "" or \
            userSettings.calculationStartDate is None or userSettings.calculationEndDate is None:
        return

    wktAoi = GeoPosition().loadWktFromGeojson(userSettings.currentAoi)

    filePath = userSettings.dataPath + "in_output_file_list/"
    if not os.path.exists(filePath):
        os.makedirs(filePath)

    vegIdProcessingList = []
    cohProcessingList12Days = []
    cohProcessingList6Days = []
    backscatterProcessingList = []

    sliceMode = True if userSettings.processingMode == "AOI Processing" else False

    if userSettings.processingList is None:

        tilesSlc = PyFuncQueries().buildSentinel1QueryTileList(userSettings.currentAoi, userSettings.calculationStartDate,
                                                               userSettings.calculationEndDate, productTypeSlc)
        tilesGrd = PyFuncQueries().buildSentinel1QueryTileList(userSettings.currentAoi, userSettings.calculationStartDate,
                                                               userSettings.calculationEndDate, productTypeGrd)
        inOutputListSlc = CreateInputOutput().generateFileList(tilesSlc, productTypeSlc, userSettings.calculationStartDate,
                                                               userSettings.calculationEndDate, filePath,
                                                               userSettings.areaName, sliceMode)
        inOutputListGrd = CreateInputOutput().generateFileList(tilesGrd, productTypeGrd, userSettings.calculationStartDate,
                                                               userSettings.calculationEndDate, filePath,
                                                               userSettings.areaName, sliceMode)

        vegIdProcessingList = inOutputListSlc[0] if len(inOutputListSlc) >= 1 else []
        cohProcessingList12Days = inOutputListSlc[1] if len(inOutputListSlc) >= 2 else []
        cohProcessingList6Days = inOutputListSlc[2] if len(inOutputListSlc) == 3 else []
        backscatterProcessingList = inOutputListGrd

    else:
        for root, dirs, files in os.walk(userSettings.processingList):
            for file in files:
                if file.endswith("backscatter.txt"):
                    backscatterProcessingList = CreateInputOutput().readFileToList(userSettings.processingList + file)
                if file.endswith("polarimetry.txt") or file.endswith("veg_index.txt"):
                    vegIdProcessingList = CreateInputOutput().readFileToList(userSettings.processingList + file)
                if file.endswith("coherence_6d.txt"):
                    cohProcessingList6Days = CreateInputOutput().readFileToList(userSettings.processingList + file)
                if file.endswith("coherence_12d.txt"):
                    cohProcessingList12Days = CreateInputOutput().readFileToList(userSettings.processingList + file)

    if userSettings.processingSequence == "All":
        BatchProcessing(userSettings).calculateBackscatter(backscatterProcessingList,  wktAoi, userSettings)
        BatchProcessing(userSettings).calculateVegIndex(vegIdProcessingList, wktAoi, userSettings)
        BatchProcessing(userSettings).calculateCoh(cohProcessingList6Days, cohProcessingList12Days,  wktAoi, userSettings)

    elif userSettings.processingSequence == "Backscatter":
        BatchProcessing(userSettings).calculateBackscatter(backscatterProcessingList,  wktAoi, userSettings)

    elif userSettings.processingSequence == "Radar Vegetation Index":
        BatchProcessing(userSettings).calculateVegIndex(vegIdProcessingList, wktAoi, userSettings)

    else:
        BatchProcessing(userSettings).calculateCoh(cohProcessingList6Days, cohProcessingList12Days,  wktAoi, userSettings)


def multiAoiExecution(userSettings):
    path = userSettings.aoiLocation
    for root, dirs, files in os.walk(path):
        for file in files:
            if file.endswith(".geojson"):
                userSettings.currentAoi = path + file
                name = file.removesuffix('.geojson')
                userSettings.areaName = name
                userSettings.setAttribute("areaName", name)
                executeBySettings(userSettings)

def executeByLocationSettings(userSettings):
    if os.path.exists(userSettings.aoiLocation) and os.path.isdir(userSettings.aoiLocation):
        multiAoiExecution(userSettings)
    else:
        userSettings.currentAoi = userSettings.aoiLocation
        executeBySettings(userSettings)

def main():
    args = sys.argv[1:]
    userSettings = CreateUserSetting()

    if len(args) == 1 and args[0] == "--withGui":
        CreateUserSettingsGui(executeByLocationSettings).runGui()
    else:
        executeByLocationSettings(userSettings)
        print("Ensure all Settings are set in 'user_settings.xml' file")




if __name__ == "__main__":
    main()
