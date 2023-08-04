#--------------------------------------------------------------------------------------------------------------------------------
# Name:        log_output
# Purpose:
#
# Author:      jennifer.mcclelland
#
# Created:     2022
# Copyright:   (c) jennifer.mcclelland 2022
#
# ----This class offers methods to create a logfile named with the current data and time.
#-----An interface is provided to add content to the logfile at any point in the processing.
#-----An error flag and error content holder can be set and derived to indicate if there were processing errors
#-----and the specific error content. In case of an error, this is added to the logfile before finalization.
#--------------------------------------------------------------------------------------------------------------------------------

from controller_modules.create_user_setting_file import CreateUserSetting

import os
import datetime
import csv


class LogOutput:

    __fileHandlerLog = None
    __fileHandlerTiles = None
    __fileHandlerWriter = None
    __fileHandlerCsv = None
    __userSettings = None
    __error = False
    __lastErrorMessage = ""
    __totalTime = 0
    __amountScenes = 0

    def __init__(self):

        # Get the repository folder path
        self.__userSettings = CreateUserSetting()

        # Create log output folder if not available
        if not os.path.exists(self.__userSettings.dataPath + "log_output/") and self.__userSettings.dataPath != "":
            os.makedirs(self.__userSettings.dataPath+"log_output/")

    def createLogOutputFile(self, prefixName):
        currentDatetime = datetime.datetime.now()
        date = ("%s%s%s" % (currentDatetime.day, currentDatetime.month, currentDatetime.year))
        time = ("%s:%s:%s" % (currentDatetime.hour, currentDatetime.minute, currentDatetime.second))

        self.__error = False
        fileName = self.__userSettings.dataPath+"log_output/"+"log_"+date+"_"+time + "_" + prefixName +".txt"
        tilesName = self.__userSettings.dataPath + "log_output/" + "tiles_" + date + "_" + time + "_" + prefixName + \
                    ".txt"
        procTimesName = self.__userSettings.dataPath + "log_output/" + "proc_times_" + date + "_" + time + "_" + \
                        prefixName + ".csv"

        self.__fileHandlerLog = open(fileName, 'a')
        self.__fileHandlerTiles = open(tilesName, 'a')
        self.__fileHandlerCsv = open(procTimesName, 'a')
        self.__fileHandlerWriter = csv.writer(self.__fileHandlerCsv)

        self.__fileHandlerWriter.writerow(["SceneNo", "Time"])

    def appendOutputToLog(self, content, error=False):
        print(content)
        if self.__fileHandlerLog is not None:
            self.__fileHandlerLog.write(content + "\n")
        if error:
            self.__error = error

    def appendProcTime(self, time):
        self.__amountScenes = self.__amountScenes + 1
        self.__totalTime = self.__totalTime + time
        self.__fileHandlerWriter.writerow([self.__amountScenes, time])

    def appendSceneToList(self, scene):
        if self.__fileHandlerTiles is not None:
            self.__fileHandlerTiles.write(str(scene) + "\n")

    def setTotalTime(self):
        self.__fileHandlerWriter.writerow([self.__amountScenes, self.__totalTime])

        output = "The total processing time for all scenes is: %s sec" % self.__totalTime
        self.__fileHandlerLog.write(output + "\n")
        self.__totalTime = 0
        print(output)

    def closeCurrentFiles(self):
        if self.__error:
            self.__fileHandlerLog.write("-----------------------Attention:Processing contains Error!!!------------------" + "\n")
        else:
            self.__fileHandlerLog.write("-----------------------Processing successful!!!------------------" + "\n")
        self.__fileHandlerLog.close()
        self.__fileHandlerCsv.close()
        self.__fileHandlerTiles.close()

    def setCurrentErrorMsg(self, msg):
        self.__lastErrorMessage = msg

    def getCurrentErrorMsg(self):
        return self.__lastErrorMessage

    def getError(self):
        return self.__error
