#----------------------------------------------------------------------------------------------------------------------------------------------------------
# Name:        snap_graph_processing
# Purpose:
#
# Author:      jennifer.mcclelland
#
# Created:     2022
# Copyright:   (c) jennifer.mcclelland 2022
#
#-------This class interfaces to pyrosar and snap gpt for multiprocessing execution of Snap graph operator .xml files.
#-------Documentation: https://senbox.atlassian.net/wiki/spaces/SNAP/pages/70503590/Creating+a+GPF+Graph?preview=%2F70503590%2F70505565%2Fgpt_kmeans_help.png
#-------To execute an individual, well formatted .xml graph, the read and write paths must be set.
#-------These paths respectively point to the input scene and define the output scene location and name
#-------With the pyrosar executeByWorkers method, one large graph operator calculation sequence is split into
#-------smaller groups. The intermediate results are stored on harddrive temporarily thus disburdening the memory management and
#-------significantly speeding up the performance time. The size of groups depend on the operation and the underlying architecture.
#-------For more documentation see: https://pyrosar.readthedocs.io/en/v0.12/pyroSAR.html?highlight=groupbyworkers#pyroSAR.snap.auxil.groupbyWorkers
#-----------------------------------------------------------------------------------------------------------------------------------------------------------

import io
import os
from lxml import etree

from pyroSAR.snap.auxil import execute as pyroSarGptExecute
from pyroSAR.snap.auxil import split
from pyroSAR.snap.auxil import groupbyWorkers

from contextlib import redirect_stdout
import datetime

class SnapGraphProcessing:

    # #TODO:Check this method after changes
    @staticmethod
    def setInOutputPaths(xmlFile, inputPath, outputPath):
        tree = etree.parse(xmlFile)
        root = tree.getroot()

        # #Check for Read and Write Nodes
        read = root.xpath("//node[@id = 'Read']")
        read = root.xpath("//node[@id = 'Read (1)']") if read is None or len(read) == 0 else read

        write = root.xpath("//node[@id = 'Write']")
        write = root.xpath("//node[@id = 'Write (1)']") if write is None or len(write) == 0 else write

        parametersRead = read[0].find("parameters") if read is not None and len(write) > 0 else None
        parametersWrite = write[0].find("parameters") if write is not None and len(write) > 0 else None

        if parametersRead is None or parametersWrite is None or len(parametersRead) < 1 or len(parametersWrite) < 1:
            print("No read/write nodes in xml file")
            readFileName = None
            writeFileName = None
        else:
            readFileName = parametersRead.find("file")
            writeFileName = parametersWrite.find("file")

            # #For product files add Sentinel-1 format
            if inputPath.endswith(".SAFE"):
                formatname = parametersRead.find("formatName")
                if formatname is None:
                    print("Add formatname")
                    etree.SubElement(parametersRead, "formatName").text = "SENTINEL-1"
                else:
                    formatname.text = "SENTINEL-1"
            else:
                formatname = parametersRead.find("formatName")
                if formatname is not None:
                    formatname.text = ""

        # #Check for file name nodes
        if readFileName is None or writeFileName is None:
            print("Read or write Input not valid")
        else:
            readFileName.text = inputPath
            writeFileName.text = outputPath
            print("New input path:" + inputPath)
            print("New output path:" + outputPath)

        # #Write new paths to xml
        prettyString = etree.tostring(root, pretty_print=True, encoding='unicode')
        with open(xmlFile, "w") as f:
            f.write(prettyString)

    @staticmethod
    def setMultiplePaths(xmlFile, pathList, mode="Read"):
        tree = etree.parse(xmlFile)
        root = tree.getroot()

        # #Check for Read and Write Nodes
        index = 1
        for path in pathList:

            pathResult = root.xpath("//node[@id = '" + mode + " (" + str(index) + ")']") if mode == "Read" else root.xpath("//node[@id = 'Write']")

            if index == 1 and mode == "Read" and pathResult is None:
                pathResult = root.xpath("//node[@id = 'Read']")

            parameters = pathResult[0 if mode == "Read" else index - 1].find("parameters") if pathResult is not None else None
            fileName = parameters.find("file") if parameters is not None else None

            # #Check for file name nodes
            if fileName is None:
                print("Path Input not valid")
            else:
                fileName.text = path
                print("New " + mode + " path " + str(index) + " for " + xmlFile + ":\n" + path)

            index += 1

        # #Write new paths to xml
        prettyString = etree.tostring(root, pretty_print=True, encoding='unicode')
        with open(xmlFile, "w") as f:
            f.write(prettyString)

    @staticmethod
    def setNewOperatorParameter(xmlFile, operatorName, parameterName, newValue):
        tree = etree.parse(xmlFile)
        root = tree.getroot()
        pathResult = root.xpath("//node[@id = '" + operatorName + "']")

        if pathResult is None or len(pathResult) == 0:
            return

        parameters = pathResult[0].find("parameters")
        parameter = parameters.find(parameterName) if parameters is not None and len(parameters) > 0 else None

        if parameter is None:
            print("Parameter Invalid")
            return

        if parameter.text == newValue:
            print(operatorName + " " + parameterName + " " + newValue + " already valid")
            return

        parameter.text = newValue
        prettyString = etree.tostring(root, pretty_print=True, encoding='unicode')
        with open(xmlFile, "w") as f:
            f.write(prettyString)
        print(operatorName + " has new " + parameterName + " value " + newValue)

    @staticmethod
    def getOperatorParameter(xmlFile, operatorName, parameterName):
        tree = etree.parse(xmlFile)
        root = tree.getroot()
        pathResult = root.xpath("//node[@id = '" + operatorName + "']")

        if pathResult is None or len(pathResult) == 0:
            return None

        parameters = pathResult[0].find("parameters")
        parameter = parameters.find(parameterName) if parameters is not None and len(parameters) > 0 else None

        if parameter is None:
            print("Parameter Invalid")
            return None

        return parameter.text

    @staticmethod
    def getElementByName(xmlFile, name):
        if not os.path.exists(xmlFile):
            return None

        tree = etree.parse(xmlFile)
        root = tree.getroot()
        pathResult = root.xpath("//MDATTR[@name = '" + name + "']")

        if pathResult is None or len(pathResult) == 0:
            return None

        return pathResult[0].text

    @staticmethod
    def performProcessing(xmlFile, logobject=None):
        readPath = SnapGraphProcessing.getOperatorParameter(xmlFile, "Read", "file")

        if readPath is None:
            readPath = SnapGraphProcessing.getOperatorParameter(xmlFile, "Read (1)", "file")

        if readPath is not None and readPath != "" and (not os.path.exists(readPath)):
            if logobject is not None:
                logobject.appendOutputToLog("Aborting Processing of: " + xmlFile + ".\n"
                                            + readPath + " does not exist.")
            return

        timeBefore = datetime.datetime.now()
        try:
            f = io.StringIO()
            with redirect_stdout(f):
                pyroSarGptExecute(xmlFile, cleanup=False)
            output = 'Got stdout: {0}'.format(f.getvalue())
            timeAfter = datetime.datetime.now()
            timeForProcessing = timeAfter-timeBefore
            timeOutput = "The processing time: %s sec" % (datetime.timedelta(seconds=timeForProcessing.seconds))

            if logobject is not None:
                logobject.appendOutputToLog(timeOutput)
                logobject.appendOutputToLog(output)

        except RuntimeError as e:

            if logobject is not None:
                logobject.appendOutputToLog("RuntimeError: \n" + str(e), error=True)
                logobject.setCurrentErrorMsg(str(e))

    @staticmethod
    def executeByGroups(xmlFile, logobject, outputPath, amountGroups):

        if amountGroups == 0:
            groups = None
        else:
            groups = groupbyWorkers(xmlFile, n=amountGroups)

        if groups is not None:
            subs = split(xmlFile, groups=groups, outdir=outputPath)
            for sub in subs:
                SnapGraphProcessing.performProcessing(sub, logobject)
        else:
            try:
                SnapGraphProcessing.performProcessing(xmlFile, logobject)
            except RuntimeError as e:
                print(e)

    @staticmethod
    def getAscendingMode(scenePair):
        tree = etree.parse(scenePair[0] + "/manifest.safe")
        root = tree.getroot()
        result = root.findall('.//{http://www.esa.int/safe/sentinel-1.0/sentinel-1}pass')

        mode1 = result[0].text if result is not None and len(result) > 0 else None

        tree = etree.parse(scenePair[1] + "/manifest.safe")
        root = tree.getroot()
        result = root.findall('.//{http://www.esa.int/safe/sentinel-1.0/sentinel-1}pass')

        mode2 = result[0].text if result is not None and len(result) > 0 else None
        return mode1 if (mode1 is not None and mode1 == mode2) else None
