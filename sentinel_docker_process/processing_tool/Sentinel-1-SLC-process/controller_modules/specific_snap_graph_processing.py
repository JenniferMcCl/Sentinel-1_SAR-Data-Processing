# -------------------------------------------------------------------------------
# Name:        specific_snap_graph_processing
# Purpose:
#
# Author:      jennifer.mcclelland
#
# Created:     2022
# Copyright:   (c) jennifer.mcclelland 2022
#
# -------This class offers methods to process Sentinel 1 SAR data in batches with preprepared xml files.
# -------Specific sequences of xml files are executed.
# --------The predefined .xml files are located in the snap_graph_files folder and accessed.
# -------The read and write paths for processing graphs are set per scene during batch processing.
# -------Specific output data file naming structure is defined.
# -------Read node: "<path to output folder>/<scene id>_<graph node abreviation><.dim>"
# -------Write node: "<path to output folder>/<scene id>_<graph node abreviation>"
# -------------------------------------------------------------------------------

from geojson import Polygon

from controller_modules.snap_graph_processing import SnapGraphProcessing
from controller_modules.geo_position import GeoPosition

import os
import shutil
from shapely import wkt
from lxml import etree


class SpecificSnapGraphProcessing:

    def __init__(self, xmlFolder, outputPath):
        self.preprocessingGraphs = xmlFolder + "preprocessing_graphs/"
        self.spacialCalcGraphs = xmlFolder + "spacial_calc_graphs/"
        self.simpleSubGraphs = xmlFolder + "simple_sub_graphs/"
        self.mainCalcGraphs = xmlFolder + "main_calc_graphs/"

        if outputPath is None:
            print("Abort because of missing output path")
            quit()

        self.tempFiles = outputPath + "temp/"
        if not os.path.exists(self.tempFiles):
            os.makedirs(self.tempFiles)

        filePath = outputPath + "in_output_file_list/"
        if not os.path.exists(filePath):
            os.makedirs(filePath)

        self.terrainProjection = 'PROJCS["ETRS89 / UTM zone 32N", GEOGCS["ETRS89", DATUM["European Terrestrial ' \
                                 'Reference System 1989", SPHEROID["GRS 1980", 6378137.0, 298.257222101, ' \
                                 'AUTHORITY["EPSG","7019"]], TOWGS84[0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0], ' \
                                 'AUTHORITY["EPSG","6258"]], PRIMEM["Greenwich", 0.0, AUTHORITY["EPSG","8901"]], ' \
                                 'UNIT["degree", 0.017453292519943295], AXIS["Geodetic longitude", EAST], ' \
                                 'AXIS["Geodetic latitude", NORTH], AUTHORITY["EPSG","4258"]], PROJECTION[' \
                                 '"Transverse_Mercator"], PARAMETER["central_meridian", 9.0], PARAMETER[' \
                                 '"latitude_of_origin", 0.0], PARAMETER["scale_factor", 0.9996], PARAMETER[' \
                                 '"false_easting", 500000.0], PARAMETER["false_northing", 0.0], UNIT["m", 1.0], ' \
                                 'AXIS["Easting", EAST], AXIS["Northing", NORTH], AUTHORITY["EPSG","25832"]]'

    def setAllProcessingParameters(self):

        # ################Ensure final output format is GeoTiff###############################
        SnapGraphProcessing.setNewOperatorParameter(
            self.simpleSubGraphs + "terrain_correction.xml", "Write", "formatName", "GeoTIFF")

        # Ensure terrain projection is set
        SnapGraphProcessing.setNewOperatorParameter(self.mainCalcGraphs + "calc_coherence.xml",
                                                    "Terrain-Correction", "mapProjection",
                                                    self.terrainProjection)
        SnapGraphProcessing.setNewOperatorParameter(
            self.mainCalcGraphs + "calc_coherence_no_deburst.xml", "Terrain-Correction",
            "mapProjection", self.terrainProjection)

        SnapGraphProcessing.setNewOperatorParameter(self.mainCalcGraphs + "calc_backscatter.xml",
                                                    "Terrain-Correction", "mapProjection",
                                                    self.terrainProjection)
        SnapGraphProcessing.setNewOperatorParameter(
            self.simpleSubGraphs + "terrain_correction.xml", "Terrain-Correction",
            "mapProjection", self.terrainProjection)

    # ######################Here are the methods to set the paths to the xml files#####################

    def setBackscatterPaths(self, scene, resultName, outputPath):

        sceneId = self.getSceneId(scene)
        SnapGraphProcessing.setInOutputPaths(self.preprocessingGraphs + "step1_apply_orbit_calibr.xml",
                                                    self.tempFiles + sceneId + ".dim",
                                                    self.tempFiles + "step1_" + sceneId)

        SnapGraphProcessing.setInOutputPaths(self.spacialCalcGraphs + "subset_with_geo_coords.xml",
                                                    self.tempFiles + "step1_" + sceneId + ".dim",
                                                    self.tempFiles + sceneId + "_subset")

        SnapGraphProcessing.setInOutputPaths(self.mainCalcGraphs + "calc_backscatter.xml",
                                                    self.tempFiles + sceneId + "_subset.dim",
                                                    outputPath + resultName)

    def setRadVegIdPaths(self, scene, merged):
        sceneId = self.getSceneId(scene)

        SnapGraphProcessing.setInOutputPaths(self.preprocessingGraphs + "step1_apply_orbit_calibr.xml",
                                                    scene, self.tempFiles + "step1_" + sceneId)

        path = self.tempFiles + "step1_" + sceneId + ".dim" if merged[0] is True else \
            self.tempFiles + "step1_" + sceneId + "_deb.dim"

        SnapGraphProcessing.setInOutputPaths(self.spacialCalcGraphs + "subset_with_geo_coords.xml",
                                                    path,
                                                    self.tempFiles + "subset_" + sceneId)

        SnapGraphProcessing.setInOutputPaths(
            self.preprocessingGraphs + "polar_matrix_multilook_speckle_filter.xml",
            self.tempFiles + "subset_" + sceneId + ".dim",
            self.tempFiles + "polarmlsf_" + sceneId)

        self.setDpVegIdPaths(sceneId)
     #   self.setCpVegIdPaths(sceneId)

    def setDpVegIdPaths(self, sceneId):
        SnapGraphProcessing.setInOutputPaths(self.mainCalcGraphs + "calc_dp_rad_veg_index.xml",
                                                    self.tempFiles + "polarmlsf_" + sceneId + ".dim",
                                                    self.tempFiles + sceneId + "_dpradid")

    def setCpVegIdPaths(self, sceneId):
        SnapGraphProcessing.setInOutputPaths(self.mainCalcGraphs + "calc_cp_rad_veg_index.xml",
                                                    self.tempFiles + "polarmlsf_" + sceneId + ".dim",
                                                    self.tempFiles + sceneId + "_cpradid")

    # ###############################Here specific operator parameter values can be set############################

    def setSubsetAoiValue(self, wktAoi):
        SnapGraphProcessing.setNewOperatorParameter(self.spacialCalcGraphs + "subset_with_geo_coords.xml",
                                                           "Subset", "geoRegion", wktAoi)

    def setSplitwktAoiValue(self, wktAoi):
        SnapGraphProcessing.setNewOperatorParameter(self.spacialCalcGraphs + "topsar_split_apply_orbit.xml",
                                                           "TOPSAR-Split", "wktAoi", wktAoi)

    # ##################Here are the methods to execute the xml file graphs in specific sequences######################

    # ###########------------------Methods to process multiscene backscatter-----------------------------############
    def multiSceneProcBackscatter(self, entryByTime, nameExtension, wktAoi, outputPath, logObject):

        if len(entryByTime) != 2:
            print("Something wrong with scene entry given in backscatter processing.")
            return

        # #Prepare the list to check for slice creation and output file name
        scenePair = entryByTime[0].split(",")
        outputFileName = entryByTime[1] + (
            "_" + nameExtension if nameExtension is not None else "")

        if self.__isFileAvailable(outputPath + outputFileName + ".tif"):
            logObject.appendOutputToLog(
                "File:{0}/ already processed.\n".format(outputPath + outputFileName + ".tif"))
            return

        # #Load the wkt aoi as polygon object
        polyWktAoi = ""
        if wktAoi != "":
            polyWktAoi = wkt.loads(wktAoi)

        # #Check for special cases such as:
        # # 1. an empty scene pair
        # # 2. scene lists of two or more where one scene is sufficient to cover Aoi.
        # # This might catch (SNAP!!!) error where slicing can not be performed because overlap of two scenes is too
        # high
        # #TODO: Find solution for cases where none of the scenes individually overlap the Aoi
        scene = []
        if len(scenePair) == 0:
            logObject.appendOutputToLog("List of Scenes not suitable for Sliced Backscatter processing.")
            return
        elif len(scenePair) >= 2:
            scene = self.__getContainingScene(scenePair, wktAoi)
            print("Scene slice list might be reduced to one slice if Aoi overlap is fullfilled.")
            if scene is not None:
                logObject.appendOutputToLog("Scene list: " + str(scenePair) + "\nbeing reduced to: " + str(scene))

        # #Differenciate between cases where no Slice must be performed and Slice must be performed
        if len(scenePair) == 1 or scene is not None:
            wktScene1 = GeoPosition().getWktFromScene(scenePair[0].strip() + "/manifest.safe")
            polyWktScene1 = wkt.loads(wktScene1)

            if polyWktAoi != "" and (not polyWktScene1.intersects(polyWktAoi)):
                print("Attention: WktAoi does not intersect both scene pairs for Split")
                return

            scene = [scenePair[0].strip()]
            logObject.appendOutputToLog("Regular processing")
        else:
            wktScene1 = GeoPosition().getWktFromScene(scenePair[0].strip() + "/manifest.safe")
            wktScene2 = GeoPosition().getWktFromScene(scenePair[1].strip() + "/manifest.safe")
            polyWktScene1 = wkt.loads(wktScene1)
            polyWktScene2 = wkt.loads(wktScene2)

            # #Check if the Aoi really intersects with both scenes to be sliced
            if (polyWktAoi != "" and (
                    not polyWktScene1.intersects(polyWktAoi) or not polyWktScene2.intersects(polyWktAoi))):
                print("Attention: WktAoi does not intersect both scene pairs for Split")
                return

            scene = [scenePair[0].strip(), scenePair[1].strip()]
            logObject.appendOutputToLog("Slice must be performed before processing.")

        logObject.appendOutputToLog("Processing entry:" + str(scenePair))

        sceneId = self.getSceneId(scene[0])
        SnapGraphProcessing.setInOutputPaths(self.preprocessingGraphs + "grd_border_thermal_noise_removal.xml",
                                                    scene[0],
                                                    self.tempFiles + sceneId + "_grd_prepro")
        SnapGraphProcessing.performProcessing(self.preprocessingGraphs + "grd_border_thermal_noise_removal.xml",
                                                     logObject)

        if not self.__isFileAvailable(self.tempFiles + sceneId + "_grd_prepro.dim"):
            logObject.appendSceneToList(entryByTime)
            logObject.appendOutputToLog("Skipping scene in Backscatter processing:" + sceneId + " could not be "
                                                                                                "processed.")
            return

        if len(scene) == 2:
            sceneId2 = self.getSceneId(scene[1])
            SnapGraphProcessing.setInOutputPaths(
                self.preprocessingGraphs + "grd_border_thermal_noise_removal.xml",
                scene[1],
                self.tempFiles + sceneId2 + "_grd_prepro")
            SnapGraphProcessing.performProcessing(
                self.preprocessingGraphs + "grd_border_thermal_noise_removal.xml", logObject)

            self.__setAndProcessSlice(sceneId + "_grd_prepro", sceneId2 + "_grd_prepro", self.tempFiles, logObject)

            if not self.__isFileAvailable(self.tempFiles + sceneId2 + "_grd_prepro.dim"):
                logObject.appendSceneToList(entryByTime)
                logObject.appendOutputToLog("Skipping scene in Backscatter processing:" + sceneId2 + " could not be "
                                                                                                    "processed.")
                return

        scenePath = self.tempFiles + sceneId + "_grd_prepro.dim" if len(
            scene) == 1 else self.tempFiles + self.getSceneId(scene[1]) + "_grd_prepro_slice.dim"

        if self.__isFileAvailable(scenePath):
            self.setBackscatterPaths(scenePath, outputFileName, outputPath)
            self.setSubsetAoiValue(wktAoi)
            self.processBackscatter(scenePath, logObject)
        else:
            logObject.appendSceneToList(entryByTime)
            logObject.appendOutputToLog("Skipping scene in Backscatter processing:" + scenePath + " is not available.")

        self.deleteAllTempFiles()

    def processBackscatter(self, scene, logObject):
        SnapGraphProcessing.setNewOperatorParameter(self.preprocessingGraphs + "step1_apply_orbit_calibr.xml",
                                                           "Calibration", "selectedPolarisations", 'VV,VH')
        SnapGraphProcessing.setNewOperatorParameter(self.preprocessingGraphs + "step1_apply_orbit_calibr.xml",
                                                           "Calibration", "outputSigmaBand", 'False')
        SnapGraphProcessing.setNewOperatorParameter(self.preprocessingGraphs + "step1_apply_orbit_calibr.xml",
                                                           "Calibration", "outputGammaBand", 'False')
        SnapGraphProcessing.setNewOperatorParameter(self.preprocessingGraphs + "step1_apply_orbit_calibr.xml",
                                                           "Calibration", "outputBetaBand", 'True')
        SnapGraphProcessing.performProcessing(self.preprocessingGraphs + "step1_apply_orbit_calibr.xml",
                                                     logObject)

        sceneId = self.getSceneId(scene)
        bands = self.__getAvailableBands(self.tempFiles + "step1_" + sceneId + ".dim")
        SnapGraphProcessing.setNewOperatorParameter(self.spacialCalcGraphs + "subset_with_geo_coords.xml",
                                                           "Subset", "sourceBands", bands)

        self.__processAndCheckSubset(logObject)
        SnapGraphProcessing.executeByGroups(self.mainCalcGraphs + "calc_backscatter.xml", logObject,
                                                   self.tempFiles, 1)

    # ###########------------------Methods to process multiscene vegetation id-----------------------------############

    def multiSceneProcRadVegId(self, entryByTime, nameExtension, wktAoi, outputPath, logObject):
        """Depending on given scene list performs spacial operations to combine scenes and reduce data to Aoi area.
           Radar Vegetation Index calculation is then performed on result. 
           All paths are set for intermediate and final results.

        Parameters
        ----------
        entryByTime : list
            The list of scenes containing one or two scenes to combine
        wktAoi : str
            The Aoi in Wkt format
        outputPath : str
            The path where the result data is produced
        logObject : LogOutput
            The logOutput class object that adds processing content to the current logfile

        Returns
        -------
        None
            If the given scene list is empty
        """

        if len(entryByTime) != 2:
            print("Something wrong with scene entry given in Vegetation Index processing.")
            return

        merged = [False]
        scenePair = entryByTime[0].split(",")
        outputFileName = entryByTime[-1] + (
            "_" + nameExtension if nameExtension is not None else "")

        if len(scenePair) > 2 or len(scenePair) == 0:
            logObject.appendOutputToLog("List of Scenes not suitable for Sliced Vegetation Index processing.")
            return

        logObject.appendOutputToLog("Processing entry:" + str(scenePair))

        resultScene = ""
        if len(scenePair) == 1:
            resultScene = scenePair[0].strip()
            logObject.appendOutputToLog("Regular processing")
        elif len(scenePair) == 2:
            scenePair = [scenePair[0].strip(), scenePair[1].strip()]
            scenePair = self.__checkForReducedPair(scenePair, wktAoi, logObject)

        if len(scenePair) == 1:
            resultScene = scenePair[0]
        elif len(scenePair) == 2:
            logObject.appendOutputToLog("Slice must be performed before processing.")
            SnapGraphProcessing.setNewOperatorParameter(self.simpleSubGraphs + "topsar_split.xml",
                                                               "TOPSAR-Split", "selectedPolarisations", "VH,VV")
            SnapGraphProcessing.setNewOperatorParameter(self.simpleSubGraphs + "topsar_split.xml",
                                                               "TOPSAR-Split", "wktAoi", wktAoi)
            validPairs = self.__getAoiSubswathOverlap(scenePair, wktAoi)
            resultScene = self.getProcSliceByValidSw(validPairs, scenePair, self.tempFiles, merged, logObject)

        if resultScene:
            self.setSubsetAoiValue(wktAoi)
            self.setRadVegIdPaths(resultScene, merged)
            self.processRadVegId(resultScene, outputPath + outputFileName, merged, logObject)

            if not self.__isFileAvailable(outputPath + outputFileName + "_dp.tif"):
                logObject.appendOutputToLog("Rad Veg Indicies can not be processed.")
                logObject.appendSceneToList(entryByTime)
        else:
            logObject.appendOutputToLog(
                "Rad Veg Indicies can not be processed. Something wrong with given Scene and WktAoi or preprocessing "
                "failed.")
            logObject.appendSceneToList(entryByTime)

        self.deleteAllTempFiles()

    def getProcSliceByValidSw(self, validPairs, scene, outputPath, merged, logObject) -> str:

        """Depending on the validity flags of the boolean pair list validPairs the individual subswaths of given
        scenes are sliced
           and merged.

        Parameters
        ----------
        validPairs : list
            boolean pair list indicating if subswaths of given scenes must be sliced and merged
        scene : list
            The list of scenes containing one or two scenes to combine
        outputPath : str
            The path where the result data is produced
        merged : list[bool]
            A flag to indicate to the caller if a merge has been performed internally on scene components or not
        logObject : LogOutput
            The logOutput class object that adds processing content to the current logfile

        Returns
        -------
        str
            The path name of the Sentinel 1 Code-De BEAM-DIMAP formatted xml/.dim processed last.
            This is for the caller to continue futher processing steps.
        """

        subswaths = []

        for i in range(0, len(validPairs)):

            if validPairs[i][0] or validPairs[i][1]:
                subswath = "IW" + str(3 - i)

                success1 = self.__setAndProcessSplit(scene[0], outputPath, subswath, logObject)
                if self.__wktOverlapsProcessedSw(logObject) is False:
                    logObject.setCurrentErrorMsg("")
                    continue

                success2 = self.__setAndProcessSplit(scene[1], outputPath, subswath, logObject)
                if self.__wktOverlapsProcessedSw(logObject) is False:
                    logObject.setCurrentErrorMsg("")
                    continue

                if not success2 or not success1:
                    return ""

                subswaths.append(subswath)
                self.__setAndProcessSlice(self.getSceneId(scene[0]) + "_" + subswath + "_split",
                                          self.getSceneId(scene[1]) + "_" + subswath + "_split", outputPath, logObject)

        subswaths = list(set(subswaths))

        if len(subswaths) == 0:
            logObject.appendOutputToLog(
                "Skipping scene Pair in vegetation index processing:" + scene[0] + "," + scene[1])
            logObject.appendOutputToLog("Wkt aoi does not overlap any bursts")
            return ""

        if len(subswaths) == 1:
            return outputPath + self.getSceneId(scene[1]) + "_" + subswaths[0] + "_split_slice.dim"

        if len(subswaths) == 2:
            merged[0] = True
            SnapGraphProcessing.setMultiplePaths(self.spacialCalcGraphs + "step3_deburst_merge2_sw.xml",
                                                        [outputPath + self.getSceneId(scene[1]) + "_" + subswaths[
                                                            0] + "_split_slice.dim",
                                                         outputPath + self.getSceneId(scene[1]) + "_" + subswaths[
                                                             1] + "_split_slice.dim"], "Read")

            SnapGraphProcessing.setMultiplePaths(self.spacialCalcGraphs + "step3_deburst_merge2_sw.xml",
                                                        [outputPath + self.getSceneId(
                                                            scene[1]) + "_split_slice_merge2"], "Write")
            SnapGraphProcessing.performProcessing(self.spacialCalcGraphs + "step3_deburst_merge2_sw.xml",
                                                         logObject)
            return outputPath + self.getSceneId(scene[1]) + "_split_slice_merge2.dim"

        if len(subswaths) == 3:
            merged[0] = True
            SnapGraphProcessing.setMultiplePaths(self.spacialCalcGraphs + "step3_deburst_merge_all_sw.xml",
                                                        [outputPath + self.getSceneId(
                                                            scene[1]) + "_IW1_split_slice.dim",
                                                         outputPath + self.getSceneId(
                                                             scene[1]) + "_IW2_split_slice.dim",
                                                         outputPath + self.getSceneId(
                                                             scene[1]) + "_IW3_split_slice.dim"], "Read")

            SnapGraphProcessing.setMultiplePaths(self.spacialCalcGraphs + "step3_deburst_merge_all_sw.xml",
                                                        [outputPath + self.getSceneId(
                                                            scene[1]) + "_split_slice_merge3"], "Write")
            SnapGraphProcessing.performProcessing(self.spacialCalcGraphs + "step3_deburst_merge_all_sw.xml",
                                                         logObject)
            return outputPath + self.getSceneId(scene[1]) + "_split_slice_merge3.dim"

    def processRadVegId(self, scene, outputFileName, merged, logObject):

        """This function processes calculation of Radar Vegetation Index on given scene.
           With a negative merged flag value indicating that no merge was performed beforehand the deburst step must
           still executed.

        Parameters
        ----------
        scene : str
            The Path/Name of scene to perform calculation on
        outputFileName : str
            The file name for the result
        merged : list[bool]
            A flag to indicate if a merge has been performed on scene components beforehand or not
        logObject : LogOutput
            The logOutput class object that adds processing content to the current logfile
        """

        if self.__isFileAvailable(outputFileName + "_dp.tif"):
            logObject.appendOutputToLog(
                "File:{0}/ already processed.\n".format(outputFileName + ".tif"))
            return

        SnapGraphProcessing.setNewOperatorParameter(self.preprocessingGraphs + "step1_apply_orbit_calibr.xml",
                                                           "Calibration", "selectedPolarisations", 'VH,VV')
        SnapGraphProcessing.setNewOperatorParameter(self.preprocessingGraphs + "step1_apply_orbit_calibr.xml",
                                                           "Calibration", "outputSigmaBand", 'true')
        SnapGraphProcessing.setNewOperatorParameter(self.preprocessingGraphs + "step1_apply_orbit_calibr.xml",
                                                           "Calibration", "outputGammaBand", 'false')
        SnapGraphProcessing.setNewOperatorParameter(self.preprocessingGraphs + "step1_apply_orbit_calibr.xml",
                                                           "Calibration", "outputBetaBand", 'false')

        SnapGraphProcessing.performProcessing(self.preprocessingGraphs + "step1_apply_orbit_calibr.xml",
                                                     logObject)

        sceneId = self.getSceneId(scene)
        if merged[0] is False:
            self.__setAndProcessDeburst("step1_" + sceneId + ".dim", self.tempFiles, logObject)

        path = self.tempFiles + "step1_" + sceneId + ".dim" if merged[0] is True else \
            self.tempFiles + "step1_" + sceneId + "_deb.dim"
        bands = self.__getAvailableBands(path)
        SnapGraphProcessing.setNewOperatorParameter(self.spacialCalcGraphs + "subset_with_geo_coords.xml",
                                                           "Subset", "sourceBands", bands)

        self.__processAndCheckSubset(logObject)
        SnapGraphProcessing.performProcessing(
            self.preprocessingGraphs + "polar_matrix_multilook_speckle_filter.xml", logObject)

        outputFileNameDp = outputFileName + "_dp.tif"
        outputFileNameCp = outputFileName + "_cp.tif"
        self.processDpVegId(sceneId, outputFileNameDp, logObject)
    #    self.processCpVegId(sceneId, outputFileNameCp, logObject)

    def processDpVegId(self, sceneId, outputFileName, logObject):
        SnapGraphProcessing.performProcessing(self.mainCalcGraphs + "calc_dp_rad_veg_index.xml", logObject)

        SnapGraphProcessing.setInOutputPaths(self.simpleSubGraphs + "terrain_correction.xml",
                                                    self.tempFiles + sceneId + "_dpradid" + ".dim",
                                                    outputFileName)
        SnapGraphProcessing.performProcessing(self.simpleSubGraphs + "terrain_correction.xml", logObject)

    def processCpVegId(self, sceneId, outputFileName, logObject):
        SnapGraphProcessing.performProcessing(self.mainCalcGraphs + "calc_cp_rad_veg_index.xml", logObject)

        SnapGraphProcessing.setInOutputPaths(self.simpleSubGraphs + "terrain_correction.xml",
                                                    self.tempFiles + sceneId + "_cpradid" + ".dim",
                                                    outputFileName)
        SnapGraphProcessing.performProcessing(self.simpleSubGraphs + "terrain_correction.xml", logObject)

    def __checkForReducedPair(self, entryByTime, wktAoi, logObject=None):
        """This method reduces invalid entryByTime pair to single entry for radar vegetation index calculation. If
        one scene fully overlaps AOI, reduction can be made and no Slice is necessary. This only works with
        entryByTime entries with maximal length of 2.

           Parameters
           ----------
           entryByTime : list
               The pair of scenes containing one or two scenes to combine by Split
           wktAoi : str
               The Aoi in Wkt format
           logObject : LogOutput
               The logOutput class object that adds processing content to the current logfile

           Returns
           -------
           The resulting scene or pair for radar vegetation index calculation. If input is invalid the result is empty.
           """
        if len(entryByTime) == 2:
            if self.__getContainingScene([entryByTime[0].strip()], wktAoi):
                logObject.appendOutputToLog("Scene pair: " + str([entryByTime[0], entryByTime[1]]) +
                                             "\nbeing reduced to: " + str([entryByTime[0]]))
                entryByTime = [entryByTime[0]]

            elif self.__getContainingScene([entryByTime[1].strip()], wktAoi):
                logObject.appendOutputToLog("Scene pair: " + str([entryByTime[0], entryByTime[1]]) +
                                            "\nbeing reduced to: " + str([entryByTime[1]]))
                entryByTime = [entryByTime[1]]

        return entryByTime

    # ###########------------------Methods to process multiscene coherence-----------------------------############

    def multiSceneProcCoherence(self, entryByTime, nameExtension, wktAoi, outputPath, logObject):

        self.__setAllCoherenceOperators(wktAoi)

        outputFileName = ""
        if len(entryByTime) != 3:
            print("Something wrong with scene entry given in coherence processing.")
            return
        else:
            outputFileName = entryByTime[-1] + (
                "_" + nameExtension if nameExtension is not None else "")

            if self.__isFileAvailable(outputPath + outputFileName + ".tif"):
                logObject.appendOutputToLog(
                    "File:{0}/ already processed.\n".format(outputPath + outputFileName + ".tif"))
                return

        merged = [False]
        entryByTime1 = entryByTime[0].split(",")
        entryByTime2 = entryByTime[1].split(",")

        if len(entryByTime1) > 2 or len(entryByTime2) > 2:
            logObject.appendOutputToLog("List of Scenes not suitable for Sliced Coherence processing.")
            return

        #If one pair overlaps AOI reduce to single pair and avoid uneccessary slice
        entryByTime1, entryByTime2 = self.__checkForReducedCoherencePair(entryByTime1, entryByTime2, wktAoi, logObject)

        logObject.appendOutputToLog("Processing entry:" + str(entryByTime1) + "/\n" + str(entryByTime2))

        if len(entryByTime1) == 1 or len(entryByTime2) == 1:
            pair = []
            if len(entryByTime1) > 1 or len(entryByTime2) > 1:
                pair = self.__createValidCoherencePair(entryByTime1, entryByTime2, wktAoi, logObject)

            scene = entryByTime1[0].strip() if pair == [] else pair[0]
            scene2 = entryByTime2[0].strip() if pair == [] else pair[1]

            logObject.appendOutputToLog("Regular processing")

            # Use overlap function on same scene since only first entry is needed
            validSubswaths = self.__getAoiSubswathOverlap([scene, scene], wktAoi)
            subswaths = self.__getSubswathList(scene, validSubswaths, logObject)
            if not self.setAndProcessCoherence(scene, scene2, outputFileName, subswaths, outputPath, logObject):
                logObject.appendSceneToList(entryByTime)

        elif len(entryByTime1) > 1 and len(entryByTime2) > 1:
            logObject.appendOutputToLog("Slice must be performed before processing.")

        if len(entryByTime1) > 1 and len(entryByTime2) > 1:

            scene1Slice1 = entryByTime1[0].strip()
            scene2Slice1 = entryByTime1[1].strip()
            scene1Slice2 = entryByTime2[0].strip()
            scene2Slice2 = entryByTime2[1].strip()

            relevantSubswaths = self.__getAoiSubswathOverlap([scene1Slice1, scene2Slice1], wktAoi)
            slicedRes = self.getGeocodedSliceByValidSw(relevantSubswaths, [scene1Slice1, scene2Slice1],
                                                       [scene1Slice2, scene2Slice2], self.tempFiles, merged, logObject)
            if not slicedRes:
                logObject.appendSceneToList(entryByTime)
                logObject.appendOutputToLog("Skipping scene Pair in coherence processing: " + str([scene1Slice1,
                scene2Slice1]) + "," + str([scene1Slice2, scene2Slice2]))
                logObject.appendOutputToLog("One of the scenes pair could not be preprocessed.")
                return

            bands = self.__getAvailableBands(slicedRes)

            if merged[0] is True:

                SnapGraphProcessing.setNewOperatorParameter(
                    self.mainCalcGraphs + "calc_coherence_no_deburst.xml", "Subset", "sourceBands", bands)
                SnapGraphProcessing.setInOutputPaths(self.mainCalcGraphs + "calc_coherence_no_deburst.xml",
                                                            slicedRes,
                                                            outputPath + outputFileName)

                SnapGraphProcessing.performProcessing(self.mainCalcGraphs + "calc_coherence_no_deburst.xml",
                                                             logObject)
            else:
                SnapGraphProcessing.setNewOperatorParameter(self.mainCalcGraphs + "calc_coherence.xml", "Subset",
                                                                   "sourceBands", bands)
                SnapGraphProcessing.setInOutputPaths(self.mainCalcGraphs + "calc_coherence.xml", slicedRes,
                                                            outputPath + outputFileName)

                SnapGraphProcessing.performProcessing(self.mainCalcGraphs + "calc_coherence.xml", logObject)

        self.deleteAllTempFiles()

    def setAndProcessCoherence(self, scene, scene2, outputFileName, subswaths, outputPath, logObject):

        reducedSubswaths = []
        for subswath in subswaths:
            success = self.preprocessingCoherence(scene, scene2, subswath, logObject)
            if not success[0] and success[1]:
                print("Removing subswath: " + str(subswath) + "since wkt does not overlap any bursts.")
                continue
            if not success[1]:
                logObject.appendOutputToLog("Skipping scene Pair in coherence processing:" + scene + "," + scene2)
                logObject.appendOutputToLog("One of the scenes could not be processed.")
                return False
            reducedSubswaths.append(subswath)

        if len(reducedSubswaths) == 0:
            logObject.appendOutputToLog("Skipping scene Pair in coherence processing:" + scene + "," + scene2)
            logObject.appendOutputToLog("Wkt aoi does not overlap any bursts")
            return False

        sceneId = self.getSceneId(scene)
        scenePath = ""

        if len(reducedSubswaths) == 1:
            scenePath = self.tempFiles + sceneId + "_" + reducedSubswaths[0] + "_enhspediv"

        merged = False
        if len(reducedSubswaths) == 2:
            merged = True
            sceneId = self.getSceneId(scene)
            scenePath = self.tempFiles + sceneId + "_enhspediv" + "_slice_merge2"

            SnapGraphProcessing.setMultiplePaths(self.spacialCalcGraphs + "step3_deburst_merge2_sw.xml",
                                                        [self.tempFiles + sceneId + "_" + reducedSubswaths[
                                                            0] + "_enhspediv.dim",
                                                         self.tempFiles + sceneId + "_" + reducedSubswaths[
                                                             1] + "_enhspediv.dim"], "Read")

            SnapGraphProcessing.setMultiplePaths(self.spacialCalcGraphs + "step3_deburst_merge2_sw.xml",
                                                        [scenePath], "Write")
            SnapGraphProcessing.performProcessing(self.spacialCalcGraphs + "step3_deburst_merge2_sw.xml",
                                                         logObject)

        if len(reducedSubswaths) == 3:
            merged = True
            sceneId = self.getSceneId(scene)
            scenePath = self.tempFiles + sceneId + "_enhspediv" + "_slice_merge3"
            SnapGraphProcessing.setMultiplePaths(self.spacialCalcGraphs + "step3_deburst_merge_all_sw.xml",
                                                        [self.tempFiles + sceneId + "_" + reducedSubswaths[
                                                            0] + "_enhspediv.dim",
                                                         self.tempFiles + sceneId + "_" + reducedSubswaths[
                                                             1] + "_enhspediv.dim",
                                                         self.tempFiles + sceneId + "_" + reducedSubswaths[
                                                             2] + "_enhspediv.dim"], "Read")

            SnapGraphProcessing.setMultiplePaths(self.spacialCalcGraphs + "step3_deburst_merge_all_sw.xml",
                                                        [scenePath], "Write")
            SnapGraphProcessing.performProcessing(self.spacialCalcGraphs + "step3_deburst_merge_all_sw.xml",
                                                         logObject)

        bands = self.__getAvailableBands(scenePath + ".dim")

        outputFile = outputPath + outputFileName if outputPath else os.getcwd() + outputFileName
        if merged is False:
            SnapGraphProcessing.setNewOperatorParameter(self.mainCalcGraphs + "calc_coherence.xml", "Subset",
                                                               "sourceBands", bands)

            SnapGraphProcessing.setInOutputPaths(self.mainCalcGraphs + "calc_coherence.xml", scenePath + ".dim",
                                                        outputFile)
            SnapGraphProcessing.performProcessing(self.mainCalcGraphs + "calc_coherence.xml", logObject)
        else:
            SnapGraphProcessing.setNewOperatorParameter(self.mainCalcGraphs + "calc_coherence_no_deburst.xml",
                                                               "Subset", "sourceBands", bands)

            SnapGraphProcessing.setInOutputPaths(self.mainCalcGraphs + "calc_coherence_no_deburst.xml",
                                                        scenePath + ".dim", outputPath + outputFileName)
            SnapGraphProcessing.performProcessing(self.mainCalcGraphs + "calc_coherence_no_deburst.xml",
                                                         logObject)
        return True

    def preprocessingCoherence(self, scene1, scene2, subswath, logObject):

        sceneId1 = self.getSceneId(scene1)
        sceneId2 = self.getSceneId(scene2)

        SnapGraphProcessing.setNewOperatorParameter(self.spacialCalcGraphs + "topsar_split_apply_orbit.xml",
                                                           "TOPSAR-Split", "subswath", subswath)

        SnapGraphProcessing.setInOutputPaths(self.spacialCalcGraphs + "topsar_split_apply_orbit.xml", scene1,
                                                    self.tempFiles + sceneId1 + "_splitorb")

        logObject.appendOutputToLog("Starting Split calculation for " + subswath + ":")
        SnapGraphProcessing.performProcessing(self.spacialCalcGraphs + "topsar_split_apply_orbit.xml", logObject)

        # Check if Split succeeded with given wktAoi on first Scene
        if self.__wktOverlapsProcessedSw(logObject) is False:
            logObject.setCurrentErrorMsg("")
            return False, True

        if not self.__isFileAvailable(self.tempFiles + sceneId1 + "_splitorb.dim"):
            return False, False

        SnapGraphProcessing.setInOutputPaths(self.spacialCalcGraphs + "topsar_split_apply_orbit.xml", scene2,
                                                    self.tempFiles + sceneId2 + "_splitorb")
        SnapGraphProcessing.performProcessing(self.spacialCalcGraphs + "topsar_split_apply_orbit.xml", logObject)

        # Check if Split succeeded with given wktAoi on second Scene
        if self.__wktOverlapsProcessedSw(logObject) is False:
            logObject.setCurrentErrorMsg("")
            return False, True

        if not self.__isFileAvailable(self.tempFiles + sceneId2 + "_splitorb.dim"):
            return False, False

        #Add check of burst amounts. If only one, reprocess split with specific amount of 2!
        #TODO: Test this for all special cases
        self.__checkAndReprocessSplit(scene1, "", logObject)
        self.__checkAndReprocessSplit(scene2, "", logObject)

        SnapGraphProcessing.setMultiplePaths(self.preprocessingGraphs + "geocod_enh_spe_div.xml",
                                                    [self.tempFiles + sceneId1 + "_splitorb.dim",
                                                     self.tempFiles + sceneId2 + "_splitorb.dim"], "Read")
        SnapGraphProcessing.setMultiplePaths(self.preprocessingGraphs + "geocod_enh_spe_div.xml",
                                                    [self.tempFiles + sceneId1 + "_" + subswath + "_enhspediv"],
                                                    "Write")
        SnapGraphProcessing.performProcessing(self.preprocessingGraphs + "geocod_enh_spe_div.xml", logObject)
        return True, True

    def getGeocodedSliceByValidSw(self, validPairs, scene, scene2, outputPath, merged, logObject=None) -> str:

        """Depending on the validity flags of the boolean pair list validPairs the individual subswaths of given
        scenes are sliced
           and merged.

        Parameters
        ----------
        validPairs : list
            boolean pair list indicating if subswaths of given scenes must be sliced and merged
        scene : list
            The first scene pair to be geocoded, contains two scenes to be additionally sliced
        scene2 : list
            The second scene pair to be geocoded, contains two scenes to be additionally sliced
        outputPath : str
            The path where the result data is produced
        merged : list[bool]
            A flag to indicate to the caller if a merge has been performed internally on scene components or not
        logObject : LogOutput
            The logOutput class object that adds processing content to the current logfile

        Returns
        -------
        str
            The path name of the Sentinel 1 Code-De BEAM-DIMAP formatted xml/.dim processed last.
            This is for the caller to continue futher processing steps.
        """

        geocodedScene2Id = ""
        subswaths = []

        for i in range(0, len(validPairs)):

            if validPairs[i][0] or validPairs[i][1]:
                subswath = "IW" + str(3 - i)
                subswaths.append(subswath)

                SnapGraphProcessing.setNewOperatorParameter(
                    self.spacialCalcGraphs + "topsar_split_apply_orbit.xml", "TOPSAR-Split", "subswath", subswath)

                geocodedSceneId = self.getSplitApplyOrbitGeoCode(scene[0], scene2[0], self.tempFiles, subswath,
                                                                 logObject)
                if geocodedSceneId is None:
                    return ""

                geocodedScene2Id = self.getSplitApplyOrbitGeoCode(scene[1], scene2[1], self.tempFiles, subswath,
                                                                  logObject)
                if geocodedScene2Id is None:
                    return ""

                self.__setAndProcessSlice(self.getSceneId(geocodedSceneId), self.getSceneId(geocodedScene2Id),
                                          self.tempFiles, logObject)

        subswaths = list(set(subswaths))

        if len(subswaths) == 1:
            return geocodedScene2Id + "_slice.dim"

        if len(subswaths) == 2:
            merged[0] = True
            sceneId = self.getSceneId(scene[1])
            scenePath = outputPath + sceneId + "_enhspediv" + "_slice_merge2"
            SnapGraphProcessing.setMultiplePaths(self.spacialCalcGraphs + "step3_deburst_merge2_sw.xml",
                                                        [outputPath + sceneId + "_" + subswaths[0]
                                                         + "_enhspediv" + "_slice.dim",
                                                         outputPath + sceneId + "_" + subswaths[1]
                                                         + "_enhspediv" + "_slice.dim"], "Read")

            SnapGraphProcessing.setMultiplePaths(self.spacialCalcGraphs + "step3_deburst_merge2_sw.xml",
                                                        [scenePath], "Write")
            SnapGraphProcessing.performProcessing(self.spacialCalcGraphs + "step3_deburst_merge2_sw.xml",
                                                         logObject)
            return scenePath + ".dim"

        if len(subswaths) == 3:
            merged[0] = True
            sceneId = self.getSceneId(scene[1])
            scenePath = outputPath + sceneId + "_enhspediv" + "_slice_merge3"
            SnapGraphProcessing.setMultiplePaths(self.spacialCalcGraphs + "step3_deburst_merge_all_sw.xml",
                                                        [outputPath + sceneId + "_" + subswaths[0]
                                                         + "_enhspediv" + "_slice.dim",
                                                         outputPath + sceneId + "_" + subswaths[1]
                                                         + "_enhspediv" + "_slice.dim",
                                                         outputPath + sceneId + "_" + subswaths[2]
                                                         + "_enhspediv" + "_slice.dim"], "Read")

            SnapGraphProcessing.setMultiplePaths(self.spacialCalcGraphs + "step3_deburst_merge_all_sw.xml",
                                                        [scenePath], "Write")
            SnapGraphProcessing.performProcessing(self.spacialCalcGraphs + "step3_deburst_merge_all_sw.xml",
                                                         logObject)
            return scenePath + ".dim"

        else:
            return ""

    def getSplitApplyOrbitGeoCode(self, scene, scene2, outputPath, subswath, logObject=None):

        SnapGraphProcessing.setNewOperatorParameter(self.spacialCalcGraphs + "topsar_split_apply_orbit.xml",
                                                           "TOPSAR-Split", "subswath", subswath)
        sceneId = self.getSceneId(scene)
        sceneId2 = self.getSceneId(scene2)

        # Do Split and Apply Orbit for first Geocoding scene
        SnapGraphProcessing.setInOutputPaths(self.spacialCalcGraphs + "topsar_split_apply_orbit.xml", scene,
                                                    outputPath + sceneId + "_" + subswath + "_splitorb")
        SnapGraphProcessing.performProcessing(self.spacialCalcGraphs + "topsar_split_apply_orbit.xml", logObject)

        if not self.__isFileAvailable(outputPath + sceneId + "_" + subswath + "_splitorb.dim"):
            return None

        if self.__wktOverlapsProcessedSw(logObject) is False:
            logObject.setCurrentErrorMsg("")
            logObject.appendOutputToLog("Skipping scene Pair in coherence processing:" + scene + "/" + scene2)
            logObject.appendOutputToLog("Wkt aoi does not overlap any bursts")
            return None

        self.__checkAndReprocessSplit(scene, subswath, logObject)

        # Do Split and Apply Orbit for second Geocoding scene
        SnapGraphProcessing.setInOutputPaths(self.spacialCalcGraphs + "topsar_split_apply_orbit.xml", scene2,
                                                    outputPath + sceneId2 + "_" + subswath + "_splitorb")
        SnapGraphProcessing.performProcessing(self.spacialCalcGraphs + "topsar_split_apply_orbit.xml", logObject)

        if not self.__isFileAvailable(outputPath + sceneId2 + "_" + subswath + "_splitorb.dim"):
            return None

        if self.__wktOverlapsProcessedSw(logObject) is False:
            logObject.setCurrentErrorMsg("")
            logObject.appendOutputToLog("Skipping scene Pair in coherence processing:" + scene + "/" + scene2)
            logObject.appendOutputToLog("Wkt aoi does not overlap any bursts")
            return None

        self.__checkAndReprocessSplit(scene2, subswath, logObject)

        # Geocode both scenes of first pair
        SnapGraphProcessing.setMultiplePaths(self.preprocessingGraphs + "geocod_enh_spe_div.xml",
                                                    [outputPath + sceneId + "_" + subswath + "_splitorb.dim",
                                                     outputPath + sceneId2 + "_" + subswath + "_splitorb.dim"], "Read")
        SnapGraphProcessing.setMultiplePaths(self.preprocessingGraphs + "geocod_enh_spe_div.xml",
                                                    [outputPath + sceneId + "_" + subswath + "_enhspediv"], "Write")
        SnapGraphProcessing.performProcessing(self.preprocessingGraphs + "geocod_enh_spe_div.xml", logObject)

        return outputPath + sceneId + "_" + subswath + "_enhspediv"

    def __createValidCoherencePair(self, entryByTime1, entryByTime2, wktAoi, logObject=None):

        """This method reduces invalid entryByTime1 and entryByTime2 pair combinations to one valid pair for
        coherence calculation. If one entryByTime entry contains only one scene, the pair is invalid.
           For this case no two coherence pairs can be calculated for slice operation.
           This only works with entryByTime entries of maximal length of 2.

          Parameters
          ----------
          entryByTime1 : list
              The list of scenes containing one or two scenes to combine by Split
          entryByTime2 : list
              The list of scenes containing one or two scenes to combine by Split
          wktAoi : str
              The Aoi in Wkt format
          logObject : LogOutput
              The logOutput class object that adds processing content to the current logfile

          Returns
          -------
          The resulting pair for coherence calculation. If input is invalid the result is empty.
          """

        if (len(entryByTime1) > 2 or len(entryByTime2) > 2):
            print("Something wrong with Entry to create Coherence Pair")

        scene1 = entryByTime1[0].strip() if len(entryByTime1) == 1 else entryByTime2[0].strip()
        scene2Alternatives = entryByTime1 if len(entryByTime1) == 2 else entryByTime2

        if len(scene2Alternatives) == 1:
            return [scene1, scene2Alternatives[0]]

        wktSceneAlt1 = GeoPosition().getWktFromScene(scene2Alternatives[0].strip() + "/manifest.safe")
        polyWktSceneAlt1: Polygon = wkt.loads(wktSceneAlt1)
        wktSceneAlt2 = GeoPosition().getWktFromScene(scene2Alternatives[1].strip() + "/manifest.safe")
        polyWktSceneAlt2 = wkt.loads(wktSceneAlt2)
        polyWktAoi = wkt.loads(wktAoi)

        areaOverlap1 = polyWktSceneAlt1.intersection(polyWktAoi).area
        areaOverlap2 = polyWktSceneAlt2.intersection(polyWktAoi).area

        if (areaOverlap1 == 0 and areaOverlap2 == 0):
            print("Creation of coherence pair was not successful")
            return []
        else:
            lessOverlappingScene = scene2Alternatives[0].strip() if areaOverlap1 > areaOverlap2 else \
                scene2Alternatives[1].strip()
            logObject.appendOutputToLog("Reducing scene Slice pair:" + str(scene2Alternatives) + "to:" + "/\n" +
                                        scene2Alternatives[1].strip())

            return [scene1, lessOverlappingScene]

    def __checkForReducedCoherencePair(self, entryByTime1, entryByTime2, wktAoi, logObject=None):
        """This method reduces invalid entryByTime1 and entryByTime2 pairs to single entries for coherence
        calculation. If one of both pairs fully overlaps AOI, reduction can be made and no Split is necessary.
            This only works with entryByTime entries with maximal length of 2.

           Parameters
           ----------
           entryByTime1 : list
               The list of scenes containing one or two scenes to combine by Split
           entryByTime2 : list
               The list of scenes containing one or two scenes to combine by Split
           wktAoi : str
               The Aoi in Wkt format
           logObject : LogOutput
               The logOutput class object that adds processing content to the current logfile

           Returns
           -------
           The resulting pair for coherence calculation. If input is invalid the result is empty.
           """
        if len(entryByTime1) > 1 and len(entryByTime2) > 1:
            if self.__getContainingScene([entryByTime1[0].strip()], wktAoi) and \
                    self.__getContainingScene([entryByTime2[0].strip()], wktAoi):
                logObject.appendOutputToLog("Scene list: " + str([entryByTime1, entryByTime2]) +
                                             "\nbeing reduced to: " + str([entryByTime1[0], entryByTime2[0]]))

                entryByTime1 = [entryByTime1[0]]
                entryByTime2 = [entryByTime2[0]]
            elif self.__getContainingScene([entryByTime1[1].strip()], wktAoi) and \
                    self.__getContainingScene([entryByTime2[1].strip()], wktAoi):
                logObject.appendOutputToLog("Scene list: " + str([entryByTime1, entryByTime2]) +
                                             "\nbeing reduced to: " + str([entryByTime1[1], entryByTime2[1]]))
                entryByTime1 = [entryByTime1[1]]
                entryByTime2 = [entryByTime2[1]]
        return entryByTime1, entryByTime2

    def __setAllCoherenceOperators(self, wktAoi):
        SnapGraphProcessing.setNewOperatorParameter(self.preprocessingGraphs + "step1_apply_orbit_calibr.xml",
                                                    "Calibration", "selectedPolarisations", 'VV,VH')
        SnapGraphProcessing.setNewOperatorParameter(self.preprocessingGraphs + "step1_apply_orbit_calibr.xml",
                                                    "Calibration", "outputSigmaBand", 'true')
        SnapGraphProcessing.setNewOperatorParameter(self.preprocessingGraphs + "step1_apply_orbit_calibr.xml",
                                                    "Calibration", "outputGammaBand", 'false')
        SnapGraphProcessing.setNewOperatorParameter(self.preprocessingGraphs + "step1_apply_orbit_calibr.xml",
                                                    "Calibration", "outputBetaBand", 'false')

        SnapGraphProcessing.setNewOperatorParameter(self.spacialCalcGraphs + "topsar_split_apply_orbit.xml",
                                                    "TOPSAR-Split", "selectedPolarisations", "VV,VH")
        SnapGraphProcessing.setNewOperatorParameter(self.spacialCalcGraphs + "topsar_split_apply_orbit.xml",
                                                    "TOPSAR-Split", "wktAoi", wktAoi)
        SnapGraphProcessing.setNewOperatorParameter(self.spacialCalcGraphs + "topsar_split_apply_orbit.xml",
                                                    "TOPSAR-Split", "firstBurstIndex", str(1))
        SnapGraphProcessing.setNewOperatorParameter(self.spacialCalcGraphs + "topsar_split_apply_orbit.xml",
                                                    "TOPSAR-Split", "lastBurstIndex", str(9999))
        SnapGraphProcessing.setNewOperatorParameter(self.mainCalcGraphs + "calc_coherence_no_deburst.xml",
                                                    "Subset", "geoRegion", wktAoi)
        SnapGraphProcessing.setNewOperatorParameter(self.mainCalcGraphs + "calc_coherence_no_deburst.xml",
                                                    "Write", "formatName", "GeoTIFF")
        SnapGraphProcessing.setNewOperatorParameter(self.mainCalcGraphs + "calc_coherence.xml", "Subset",
                                                    "geoRegion", wktAoi)
        SnapGraphProcessing.setNewOperatorParameter(self.mainCalcGraphs + "calc_coherence.xml", "TOPSAR-Deburst",
                                                    "selectedPolarisations", "VV,VH")
        SnapGraphProcessing.setNewOperatorParameter(self.mainCalcGraphs + "calc_coherence.xml", "Write",
                                                    "formatName", "GeoTIFF")

    # ###################Helper methods for subswath selection for processing############################

    def __getAoiSubswathOverlap(self, scenePair, wktAoi) -> list:

        """This function checks spacial overlapping of the given Aoi in wkt format with each subswath of given scenes.

        Parameters
        ----------
        scenePair : list
            The list of scenes containing one or two scenes to combine
        wktAoi : str
            The Aoi in wkt format

        Returns
        -------
        list
            A list of pairs representing all subswaths of both scenes.
            The contained boolean values indicate if wktAoi overlaps subswath or not.
        """

        SnapGraphProcessing.setNewOperatorParameter(self.simpleSubGraphs + "topsar_split.xml", "TOPSAR-Split",
                                                           "wktAoi", wktAoi)

        if wktAoi == "":
            return [[True, True], [True, True], [True, True]]

        wktScene1 = GeoPosition().getWktFromScene(scenePair[0] + "/manifest.safe")
        wktScene2 = GeoPosition().getWktFromScene(scenePair[1] + "/manifest.safe")

        validPairs = [[False, False], [False, False], [False, False]]

        if wktScene1 is None or wktScene2 is None:
            print("Wkt not valid for Scene")
            return validPairs

        polyWktAoi = wkt.loads(wktAoi)
        polyWktScene1 = wkt.loads(wktScene1)
        polyWktScene2 = wkt.loads(wktScene2)

        if not polyWktScene1.intersects(polyWktAoi) or not polyWktScene2.intersects(polyWktAoi):
            print("Attention: WktAoi does not intersect both scene pairs for Split")
            return validPairs

        swMultipolyscene1 = GeoPosition().swMultiPolygonFromScene(scenePair[0] + "/manifest.safe")
        swMultipolyscene2 = GeoPosition().swMultiPolygonFromScene(scenePair[1] + "/manifest.safe")

        for i in range(0, len(validPairs)):
            if swMultipolyscene1[i].intersects(polyWktAoi):
                validPairs[i][0] = True

            if swMultipolyscene2[i].intersects(polyWktAoi):
                validPairs[i][1] = True

        return validPairs

    def __getSubswathList(self, scene, validSubswaths, logobject):
        subswaths = []
        mode = SnapGraphProcessing().getAscendingMode([scene, scene])
        if mode is None:
            logobject.appendOutputToLog(
                "----------------------Path Mode Acending/Descending not found in scene.--------------------")
            return None

        for i in range(0, len(validSubswaths)):
            if validSubswaths[i][0] is True:
                subswath = "IW" + str(3 - i)
                subswaths.append(subswath)
        return subswaths

    # ################################These methods set paths and process############################

    def __setAndProcessSplit(self, scene, outputPath, subswath, logobject=None):
        SnapGraphProcessing.setNewOperatorParameter(self.simpleSubGraphs + "topsar_split.xml", "TOPSAR-Split",
                                                           "subswath", subswath)
        SnapGraphProcessing.setInOutputPaths(self.simpleSubGraphs + "topsar_split.xml", scene,
                                                    outputPath + self.getSceneId(scene) + "_" + subswath + "_split")

        SnapGraphProcessing.performProcessing(self.simpleSubGraphs + "topsar_split.xml", logobject)
        return self.__isFileAvailable(outputPath + self.getSceneId(scene) + "_" + subswath + "_split.dim")

    def __setAndProcessSlice(self, scene1, scene2, outputPath, logobject=None):
        sentinelScene = scene1.endswith(".safe") or scene1.endswith(".SAFE")
        SnapGraphProcessing.setMultiplePaths(self.spacialCalcGraphs + "slice_assembly.xml",
                                                    [scene1 if sentinelScene else outputPath + scene1 + ".dim",
                                                     scene2 if sentinelScene else outputPath + scene2 + ".dim"], "Read")

        sceneId = self.getSceneId(scene2)
        SnapGraphProcessing.setMultiplePaths(self.spacialCalcGraphs + "slice_assembly.xml",
                                                    [outputPath + sceneId + "_slice"], "Write")
        SnapGraphProcessing.performProcessing(self.spacialCalcGraphs + "slice_assembly.xml", logobject)

    def __setAndProcessDeburst(self, scene, outputPath, logobject=None):
        sceneId = self.getSceneId(scene)
        SnapGraphProcessing.setInOutputPaths(self.spacialCalcGraphs + "topsar_deburst.xml",
                                                    outputPath + sceneId + ".dim",
                                                    outputPath + sceneId + "_deb")
        SnapGraphProcessing.performProcessing(self.spacialCalcGraphs + "topsar_deburst.xml", logobject)

    # ##################################Here are accessible helper methods#################################

    def deleteAllTempFiles(self):
        folder = self.tempFiles
        for filename in os.listdir(folder):
            file_path = os.path.join(folder, filename)
            try:
                if os.path.isfile(file_path) or os.path.islink(file_path):
                    os.unlink(file_path)
                elif os.path.isdir(file_path):
                    shutil.rmtree(file_path)
            except Exception as e:
                print('Failed to delete %s. Reason: %s' % (file_path, e))

    def getSceneId(self, scene):
        sceneIdPathList1 = list(scene.split(".")[0].split("/"))
        return sceneIdPathList1[len(sceneIdPathList1) - 1]

    # ##################################Here are general private helper methods#################################

    def __isFileAvailable(self, fileName):
        if os.path.exists(fileName):
            return True
        else:
            return False

    def __wktOverlapsProcessedSw(self, logobject=None):
        if logobject.getError() is True and \
                self.__checkErrForBurstOverlap(logobject.getCurrentErrorMsg()) is False:
            return False
        return True

    def __getContainingScene(self, sceneList, wktAoi):
        # #TODO: Test with lists of 3
        for scene in sceneList:
            wktScene = GeoPosition().getWktFromScene(scene.strip() + "/manifest.safe")
            polyWktScene = wkt.loads(wktScene)
            polyWktAoi = wkt.loads(wktAoi)
            if polyWktScene.contains(polyWktAoi):
                return scene.strip()
        return None

    def __checkErrForBurstOverlap(self, msg):
        snapErrorMsg = msg.splitlines()[1] if (msg is not None and len(msg.splitlines()) > 1) else ""
        if snapErrorMsg == "wktAOI does not overlap any burst":
            return False
        return True

    def __checkErrForSubsetOverlap(self, msg):
        if msg != "" and msg.splitlines()[0].startswith("No intersection with source product boundary"):
            return False
        else:
            return True

    def __getAvailableBands(self, scene) -> str:
        if not os.path.exists(scene):
            return ""

        tree = etree.parse(scene)
        root = tree.getroot()
        result = root.xpath("//BAND_NAME")
        bandList = []

        for entry in result:
            bandList.append(entry.text)

        bands = ','.join(list(bandList))
        return bands

    def __processAndCheckSubset(self, logObject):

        SnapGraphProcessing.performProcessing(self.spacialCalcGraphs + "subset_with_geo_coords.xml", logObject)

        # Check if Subset succeeded with given wkt polygon on previous Scene
        if logObject.getError() is True and self.__checkErrForSubsetOverlap(logObject.getCurrentErrorMsg()) is False:
            logObject.appendOutputToLog(
                "Given Subset wkt does not overlap Scene. Set overlapping Subset wkt polygon!!!")
            return False
        return True

    def __checkAndReprocessSplit(self, scene, subswath, logObject):
        sceneId1 = self.getSceneId(scene)
        subswath = "" if subswath =="" else "_" + subswath

        firstBurstIndex = int(SnapGraphProcessing.getElementByName(self.tempFiles + sceneId1 + subswath +
                                                                   "_splitorb.dim",
                                                                   "firstBurstIndex"))

        lastBurstIndex = int(SnapGraphProcessing.getElementByName(self.tempFiles + sceneId1 + subswath +
                                                                  "_splitorb.dim",
                                                                  "lastBurstIndex"))

        if firstBurstIndex == lastBurstIndex:
            if firstBurstIndex == 1:
                lastBurstIndex = lastBurstIndex + 1
            elif firstBurstIndex > 1:
                firstBurstIndex = firstBurstIndex - 1


            SnapGraphProcessing.setNewOperatorParameter(self.spacialCalcGraphs + "topsar_split_apply_orbit.xml",
                                                        "TOPSAR-Split", "wktAoi", "")
            SnapGraphProcessing.setNewOperatorParameter(self.spacialCalcGraphs + "topsar_split_apply_orbit.xml",
                                                        "TOPSAR-Split", "firstBurstIndex", str(firstBurstIndex))
            SnapGraphProcessing.setNewOperatorParameter(self.spacialCalcGraphs + "topsar_split_apply_orbit.xml",
                                                        "TOPSAR-Split", "lastBurstIndex", str(lastBurstIndex))

            SnapGraphProcessing.setInOutputPaths(self.spacialCalcGraphs + "topsar_split_apply_orbit.xml", scene,
                                                 self.tempFiles + sceneId1 + subswath + "_splitorb")
            SnapGraphProcessing.performProcessing(self.spacialCalcGraphs + "topsar_split_apply_orbit.xml", logObject)

    # #########################Old methods no longer relevant for batch processing. #################################
    # Failed because of undocumented Snap limitations or bugs.

    def setSplitSliceMergeSubsetMultiPaths(self, scene1, scene2, outputPath):

        sceneId1 = self.getSceneId(scene1)
        sceneId2 = self.getSceneId(scene2)

        SnapGraphProcessing.setMultiplePaths(self.spacialCalcGraphs + "step1_topsar_split_all_sw.xml",
                                                    [scene1 + "/manifest.safe",
                                                     scene1 + "/manifest.safe",
                                                     scene1 + "/manifest.safe",
                                                     scene2 + "/manifest.safe",
                                                     scene2 + "/manifest.safe",
                                                     scene2 + "/manifest.safe"], "Read")

        SnapGraphProcessing.setMultiplePaths(self.spacialCalcGraphs + "step1_topsar_split_all_sw.xml",
                                                    [self.tempFiles + sceneId1 + "_sw1_split",
                                                     self.tempFiles + sceneId1 + "_sw2_split",
                                                     self.tempFiles + sceneId1 + "_sw3_split",
                                                     self.tempFiles + sceneId2 + "_sw1_split",
                                                     self.tempFiles + sceneId2 + "_sw2_split",
                                                     self.tempFiles + sceneId2 + "_sw3_split"], "Write")

        SnapGraphProcessing.setMultiplePaths(self.spacialCalcGraphs + "step2_topsar_slice_all_sw.xml",
                                                    [self.tempFiles + sceneId1 + "_sw1_split.dim",
                                                     self.tempFiles + sceneId1 + "_sw2_split.dim",
                                                     self.tempFiles + sceneId1 + "_sw3_split.dim",
                                                     self.tempFiles + sceneId2 + "_sw1_split.dim",
                                                     self.tempFiles + sceneId2 + "_sw2_split.dim",
                                                     self.tempFiles + sceneId2 + "_sw3_split.dim"], "Read")

        SnapGraphProcessing.setMultiplePaths(self.spacialCalcGraphs + "step2_topsar_slice_all_sw.xml",
                                                    [self.tempFiles + sceneId1 + "_sw1_split_slice",
                                                     self.tempFiles + sceneId1 + "_sw2_split_slice",
                                                     self.tempFiles + sceneId1 + "_sw3_split_slice"], "Write")

        SnapGraphProcessing.setMultiplePaths(self.spacialCalcGraphs + "step3_deburst_merge_all_sw.xml",
                                                    [self.tempFiles + sceneId1 + "_sw1_split_slice.dim",
                                                     self.tempFiles + sceneId1 + "_sw2_split_slice.dim",
                                                     self.tempFiles + sceneId1 + "_sw3_split_slice.dim"], "Read")

        SnapGraphProcessing.setMultiplePaths(self.spacialCalcGraphs + "step3_deburst_merge_all_sw.xml",
                                                    [self.tempFiles + sceneId1 + "_split_slice_merge"], "Write")

        SnapGraphProcessing.setMultiplePaths(self.spacialCalcGraphs + "subset_with_geo_coords.xml",
                                                    [self.tempFiles + sceneId1 + "_split_slice_merge.dim"], "Read")
        SnapGraphProcessing.setMultiplePaths(self.spacialCalcGraphs + "subset_with_geo_coords.xml",
                                                    [self.tempFiles + sceneId1 + "_split_slice_merge_sub"], "Write")

        SnapGraphProcessing.setMultiplePaths(self.simpleSubGraphs + "terrain_correction.xml",
                                                    [self.tempFiles + sceneId1 + "_split_slice_merge_sub.dim"], "Read")
        SnapGraphProcessing.setMultiplePaths(self.simpleSubGraphs + "terrain_correction.xml",
                                                    [outputPath + sceneId1 + "_split_slice_merge_sub_tc"], "Write")

    def processSplitSliceMergeSubset(self, scene, logObject=None):
        sceneId = self.getSceneId(scene)
        SnapGraphProcessing.performProcessing(self.spacialCalcGraphs + "step1_topsar_split_all_sw.xml",
                                                     logObject)
        SnapGraphProcessing.performProcessing(self.spacialCalcGraphs + "step2_topsar_slice_all_sw.xml",
                                                     logObject)
        SnapGraphProcessing.performProcessing(self.spacialCalcGraphs + "step3_deburst_merge_all_sw.xml",
                                                     logObject)

        bands = self.__getAvailableBands(self.tempFiles + sceneId + "_split_slice_merge" + ".dim")
        SnapGraphProcessing.setNewOperatorParameter(self.spacialCalcGraphs + "subset_with_geo_coords.xml",
                                                           "Subset", "sourceBands", bands)
        self.__processAndCheckSubset(logObject)
        SnapGraphProcessing.performProcessing(self.simpleSubGraphs + "terrain_correction.xml")
