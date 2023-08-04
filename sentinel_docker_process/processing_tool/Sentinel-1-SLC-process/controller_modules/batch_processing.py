#-------------------------------------------------------------------------------------------------------------
# Name:        batch_processing
# Purpose:
#
# Author:      jennifer.mcclelland
#
# Created:     2022
# Copyright:   (c) jennifer.mcclelland 2022
#
#----------This class executes batch processing for given lists of scenes.
#----------Batch processing sequences for Backscatter, Radar Vegetation Index and Coherence are defined.
#----------The processing is performed on a given list of scenes primarily created with the InOutputFile class.
#----------For each processing sequence a log file is created and saved, containing all processing information.
#-------------------------------------------------------------------------------------------------------------

from controller_modules.log_output import LogOutput
from controller_modules.specific_snap_graph_processing import SpecificSnapGraphProcessing

import os
import datetime


class BatchProcessing:

    specificSnapGraphProcessing = None

    def __init__(self, userSettings):
        self.specificSnapGraphProcessing = SpecificSnapGraphProcessing(os.getcwd() + "/snap_graph_files/", userSettings.dataPath)

    # ###################This is for calculation of backscatter ######################
    def calculateBackscatter(self, backscatterProcessingList, wktAoi, userSettings):

        logOutput = LogOutput()
        logOutput.createLogOutputFile("backscatter")
        logOutput.appendOutputToLog("Backscatter process starting for AOI: " + str(userSettings.areaName) + " and "
                                                                                                             "geojson: "
                                    + str(userSettings.currentAoi))

        for scene in backscatterProcessingList:

            timeBefore = datetime.datetime.now()
            self.specificSnapGraphProcessing.multiSceneProcBackscatter(scene, userSettings.areaName, wktAoi, userSettings.backscatterOutputPath, logOutput)

            timeAfter = datetime.datetime.now()
            timeForProcessing = timeAfter-timeBefore
            timeOutput = "The total processing time for one scene is: %s sec" % (datetime.timedelta(
                seconds=timeForProcessing.seconds))

            logOutput.appendProcTime(timeForProcessing.seconds)
            logOutput.appendOutputToLog(timeOutput)

        logOutput.setTotalTime()

        logOutput.closeCurrentFiles()

    # ###################This is for calculation of dual pol and complex pol vegetation indices######################
    def calculateVegIndex(self, vegIdProcessingList, wktAoi, userSettings):
        logOutput = LogOutput()
        logOutput.createLogOutputFile("veg_index")
        logOutput.appendOutputToLog("Vegetation Index processes starting for AOI: " + str(userSettings.areaName)
                                    + " and geojson: " + str(userSettings.currentAoi))

        for scene in vegIdProcessingList:
            timeBefore = datetime.datetime.now()
            self.specificSnapGraphProcessing.multiSceneProcRadVegId(scene, userSettings.areaName, wktAoi,
                                                                    userSettings.dpVegIndexPath,
                                                                    logOutput)

            timeAfter = datetime.datetime.now()
            timeForProcessing = timeAfter - timeBefore
            timeOutput = "The total processing time for one scene is: %s sec" % (datetime.timedelta(
                seconds=timeForProcessing.seconds))

            logOutput.appendProcTime(timeForProcessing.seconds)
            logOutput.appendOutputToLog(timeOutput)

        logOutput.setTotalTime()

        logOutput.closeCurrentFiles()
        self.specificSnapGraphProcessing.deleteAllTempFiles()

    # ###################This is for calculation of coherence##########################
    def calculateCoh(self, cohProcessingList6Days, cohProcessingList12Days,  wktAoi, userSettings):
        logOutput = LogOutput()
        logOutput.createLogOutputFile("coherence")
        logOutput.appendOutputToLog("Coherence process starting for AOI: " + str(userSettings.areaName) + " and "
                                                                                                           "geojson: "
                                    + str(userSettings.currentAoi))

        for scene in cohProcessingList6Days:
            timeBefore = datetime.datetime.now()
            self.specificSnapGraphProcessing.multiSceneProcCoherence(scene, userSettings.areaName, wktAoi,
                                                                     userSettings.cohOutputPath,
                                                                     logOutput)

            timeAfter = datetime.datetime.now()
            timeForProcessing = timeAfter - timeBefore
            timeOutput = "The total processing time for one scene is: %s sec" % (datetime.timedelta(
                seconds=timeForProcessing.seconds))

            logOutput.appendProcTime(timeForProcessing.seconds)
            logOutput.appendOutputToLog(timeOutput)

        for scene in cohProcessingList12Days:
            timeBefore = datetime.datetime.now()
            self.specificSnapGraphProcessing.multiSceneProcCoherence(scene, userSettings.areaName, wktAoi,
                                                                     userSettings.cohOutputPath, logOutput)

            timeAfter = datetime.datetime.now()
            timeForProcessing = timeAfter - timeBefore
            timeOutput = "The total processing time for one scene is: %s sec" % (datetime.timedelta(
                seconds=timeForProcessing.seconds))

            logOutput.appendProcTime(timeForProcessing.seconds)
            logOutput.appendOutputToLog(timeOutput)

        logOutput.setTotalTime()
        logOutput.closeCurrentFiles()
        self.specificSnapGraphProcessing.deleteAllTempFiles()
