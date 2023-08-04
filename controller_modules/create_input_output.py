#-------------------------------------------------------------------------------
# Name:        create_input_output
# Purpose:
#
# Author:      tanja.riedel and jennifer.mcclelland
# Created:     2022
# Copyright:   (c) tanja.riedel 2022 and jennifer.mcclelland
#
#generates input / output file list
#outputs:
# for GRD data: array - input/output file list for radar backscatter
# for SLC data: (1) array - input/output file list for polarimatric vegetation index
#               (2) array_coh_6d - input/output file list for coherence, 6 days time range
#               (3) array_coh_12d - input/output file list for coherence, 12 days time range
#-------------------------------------------------------------------------------

import os
import numpy as np
import datetime
import math
from controller_modules.geo_position import GeoPosition
from controller_modules.snap_graph_processing import SnapGraphProcessing
from lxml import etree


class CreateInputOutput:

    # Set this to true to attach unique scene id to output names
    __WITH_SCENE_ID = True

    def generateFileList(self, tiles, productType, startDate, endDate, resultPath, areaNameExtension="Test Area",
                         sliceMode=True):
        ###################################################################################################################################
        # generate info array (Path & Name, Start, End, polarisation, abs Orbit, rel Orbit, mean incidence angle)
        # list to array
        # result: array

        if len(tiles) == 0:
            return [],[],[]

        info=np.array(tiles)
        ac_info=[]

        for i in range(len(tiles)):
            temp=info[i]
            temp=temp.replace("__","_")
            #name annotation xml-File
            xml_dir=temp + "/annotation/"
            temp=temp.split("/")[::-1]
            #scene name
            temp=temp[0]
            #convert to small characters for xml-file definition
            temp_xml=temp.lower()
            #replace _ by -
            temp_xml=temp_xml.replace("__",'-')
            temp_xml=temp_xml.replace("_",'-')
            temp=temp.split("_")
            xml=xml_dir + temp_xml[0:10] + "-vv-" + temp_xml[17:62] + "-001.xml"
            pol='VVVH'
            if temp[3] == '1SDH':
                xml=xml_dir + temp_xml[0:10] + "-hh-" + temp_xml[17:62] + "-001.xml"
                pol='HHHV'

            #Calculation of relative orbit number, see https://forum.step.esa.int/t/sentinel-1-relative-orbit-from-filename/7042/18
            rel_orbit = ""
            if temp[0] == 'S1A':
                rel_orbit=math.fmod(int(temp[6])-73, 175)+1
            if temp[0] == 'S1B':
                rel_orbit=math.fmod(int(temp[6])-27, 175)+1
            rel_orbit=math.floor(rel_orbit)

            #read incidence angle info from annotation xml-file <incidenceAngleMidSwath>  # not really necessary information - skip
            '''if productType == 'GRD':
                mytree = ET.parse(xml)
                myroot = mytree.getroot()
                IA = myroot.find('imageAnnotation/imageInformation/incidenceAngleMidSwath')
                IA =float(IA.text)
                IA=round(IA,2)'''

            mode = SnapGraphProcessing().getAscendingMode([info[i], info[i]])
            orbitDir = ''
            if mode == "ASCENDING":
                orbitDir = 'asc'
            elif mode == "DESCENDING":
                orbitDir = 'desc'

            #write information to list
            temp2=[info[i], temp[0], pol, temp[4], temp[5], temp[6], rel_orbit,
                   orbitDir, temp[8].replace('.SAFE', '')]
            ac_info.append(temp2)

        #List to array
        ac_info=np.array(ac_info)

        #################################################################################################################################################################

        # Remove duplicates from list (same start time and absolute orbit) and save to txt-file
        # Check if slice assembly is required (sequentially recorded S1 data; identical absolute Orbit)
        # Define and write output txt file

        # fileName = 'tiles_' + productType + '_' + startDate + '_' + endDate + '_' + orbitDirection +
        # '_cleaned_SliceAssembly.txt'
        currentDatetime = datetime.datetime.now()
        date = ("%s%s%s" % (currentDatetime.day, currentDatetime.month, currentDatetime.year))
        time = ("%s:%s:%s" % (currentDatetime.hour, currentDatetime.minute, currentDatetime.second))

        if productType == 'GRD':
            fileName = areaNameExtension + '_tiles_' + productType + '_' + startDate + '_' + endDate + "_" + date + \
                       "_" + time + '_GRD_backscatter.txt'
            outputProduct = 'BS'
        if productType == 'SLC':
            fileName = areaNameExtension + '_tiles_' + productType + '_' + startDate + '_' + endDate + "_" + date + \
                       "_" + time + '_SLC_polarimetry.txt'
            outputProduct = 'polVI'
            fileNameCoh1 = areaNameExtension + '_tiles_' + productType + '_' + startDate + '_' + endDate + "_" + date + \
                       "_" + time+ '_SLC_coherence_6d.txt'
            outputProductCoh1 = 'coh6d'
            fileNameCoh2 = areaNameExtension + '_tiles_' + productType + '_' + startDate + '_' + endDate + "_" + date + \
                       "_" + time+ '_SLC_coherence_12d.txt'
            outputProductCoh2 = 'coh12d'

        # check for duplicates - identical start time
        len_info=len(ac_info)
        # start times
        temp=ac_info[:,3]
        pos_duplicates = [idx for idx, item in enumerate(temp) if item in temp[:idx]]

        if len(pos_duplicates) == 0:
            print('no duplicates in file list')
        else:
            print('duplicates in the list')
            print('pos duplicates', pos_duplicates)
            pos_duplicates = self.updateDuplicatePositions(pos_duplicates, ac_info)
            ac_info = np.delete(ac_info, pos_duplicates, axis=0)
            tiles=ac_info[:,0]      # update tile list


        # check, if slice assembly is required - identical absolute orbits
        len_info, len_start = len(ac_info), len(ac_info) # update required in case of duplicates
        if sliceMode:
            temp = ac_info[:,5]
            len_start = len(set(temp))

        if not sliceMode and productType == 'GRD':
            counter = 0
            redundantScenes = []
            for x in range(0, len_info - 1):
                if counter > x:
                    continue
                if self.__isPairValid(ac_info[x][0], ac_info[x + 1][0]):
                    continue
                elif x + 2 < len(ac_info) and self.__isPairValid(ac_info[x][0], ac_info[x + 2][0]):
                    redundantScenes.append(x + 1)
                    counter = x + 2
            ac_info = np.delete(ac_info, redundantScenes, axis=0)
            len_info, len_start = len(ac_info), len(ac_info)

        # output array
        array = []
        array_coh_6d = []
        array_coh_12d = []

        # no slice assembly is required
        if len_info == len_start:
            print('No slice assembling required')
            for i in range (0,len_info):
                uniqueId = '_' + ac_info[i, 8] if self.__WITH_SCENE_ID else ""
                file_out=ac_info[i,3][0 : ac_info[i,3].index("T")] + '_' + ac_info[i,1] + '_' + ac_info[i,2] + '_' + ac_info[i,6] + '_' + ac_info[
                    i,7] + uniqueId + '_' + outputProduct

                line=[ac_info[i,0], file_out]
                array.append(line)

                # for SLC date: write coherence input file
                if productType == 'SLC':
                    match = self.__getCohMatching(ac_info[i], tiles)
                    matching_6d = match[0]
                    matching_12d = match[1]

                    if matching_6d:
                        lines = self.__getMultipleCohMatchingLines(ac_info[i], matching_6d, 6)

                        if not lines:
                            continue
                        else:
                            for j in lines:
                                array_coh_6d.append(j)

                    if matching_12d:
                        lines = self.__getMultipleCohMatchingLines(ac_info[i], matching_12d, 12)

                        if not lines:
                            continue
                        else:
                            for j in lines:
                                array_coh_12d.append(j)

        # slice assembly is required
        if len_info != len_start:
            print('Slice assembling required')

            j=0
            for i in range (0,len_info):
                if j >= len_info:
                    break

                # slice assembly is required for identical absolute orbits (variable temps)
                # check, if i+1 is element of slice assembly list
                abs_orb=temp[j]
                matching = [s for s in tiles if abs_orb in s]
                test2 = [s for s in matching if '1SDH' in s]     # used below for check HH appearence

                # number of scenes in matching
                slice_ass_numb=len(matching)

                if matching:

                    # Initial scenes without slice number can not be selected to create pairs for a specific date.
                    # The first scene of the specific date must be skipped. It additionally must be removed from the
                    # list of potential matches to create a valid pair.
                    sliceId = self.__getSliceId(ac_info[j, 0])
                    if sliceId == '0':
                        j = j + 1
                        continue

                    sliceId = self.__getSliceId(matching[0])
                    if sliceId == '0':
                        matching.remove(matching[0])
                        slice_ass_numb = len(matching)

                    #After clearing the scene without slice number the first potential matching scene can be set.
                    tempMatching = [matching[0]]
                    counter = 0
                    for x in range(len(matching)-1):
                        if counter > x:
                            continue
                        if self.__isPairValid(matching[x], matching[x + 1]):
                            tempMatching = self.__getValidScene(matching[x],matching[x+1])
                            continue
                        elif x+2 < len(matching) and self.__isPairValid(matching[x], matching[x + 2]):
                            tempMatching = self.__getValidScene(matching[x],matching[x+2])
                            counter = x+2

                    matching = tempMatching

                if not matching:
                    uniqueId = '_' + ac_info[j, 8] if self.__WITH_SCENE_ID else ""
                    date1_str = ac_info[j, 3][0: ac_info[j, 3].index("T")]
                    file_out=date1_str + '_' + ac_info[j,1] + '_' + ac_info[j,
                    2] + '_' + ac_info[j,6] + '_' + \
                             ac_info[j,7] + uniqueId + '_' + outputProduct
                    line=[ac_info[j,0], file_out]
                    array.append(line)

                    test=str(ac_info[j,1])       # used below for check HH appearence
                    test2=[] if test.find('1SDH') == -1 else test2
                if matching:
                    # Create string attachment for output file name with unique id suffix
                    # for each relevant scene.
                    uniqueId = ""
                    for scene in matching:
                        sceneIdList = scene.replace('/', "").replace(".SAFE", "").split("_")
                        uniqueId = uniqueId + '_' + sceneIdList[len(sceneIdList) - 1]

                    matchStr=str(matching)
                    matchStr=matchStr.replace("'","")
                    date1_str=ac_info[j,3][0 : ac_info[j,3].index("T")]
                    file_out=date1_str + '_' + ac_info[j,1] + '_' + ac_info[j,2] + '_' + ac_info[j,6] + '_' + \
                             ac_info[j,7] + uniqueId + '_' + outputProduct
                    matchStr=matchStr.replace("[","")
                    matchStr=matchStr.replace("]","")
                    line=[matchStr, file_out]
                    array.append(line)

                # for SLC date: write coherence input file
                if productType == 'SLC':
                    match = self.__getCohMatching(ac_info[j], tiles)
                    matching_SLC_6d = match[0]
                    matching_SLC_12d = match[1]

                    matching = matching if matching else [ac_info[j, 0]]

                    if matching_SLC_6d:
                        # check, if list includes SDV and SDH => skip  / maybe cross-pol is possible, to be checked
                        test1 = [s for s in matching_SLC_6d if '1SDH' in s]

                        if len(test1) == 0 and len(test2) == 0:
                            array_coh_6d.append(self.__getMultSlicedCohMatchingLines(matching, matching_SLC_6d, ac_info[j],
                                                                         6))

                    if matching_SLC_12d:
                        test1 = [s for s in matching_SLC_12d if '1SDH' in s]
                        if len(test1) == 0 and len(test2) == 0:
                            array_coh_12d.append(
                                self.__getMultSlicedCohMatchingLines(matching, matching_SLC_12d, ac_info[j],
                                                                     12))

                if slice_ass_numb == 0:
                    j=j+1
                else:
                    j=j+slice_ass_numb

        array.reverse()
        array_coh_12d.reverse()
        array_coh_6d.reverse()

        if productType == 'GRD':
            self.writeGrdListToFile(array, resultPath + fileName)
            return array
        if productType == 'SLC':
            self.writeSlcListToFile(array, array_coh_6d, array_coh_12d, resultPath + fileName, resultPath +
                                    fileNameCoh1, resultPath + fileNameCoh2)
            return array, array_coh_12d, array_coh_6d

    def __isPairValid(self, scene1, scene2):
        if GeoPosition().areaOverlap(scene1 + "/manifest.safe", scene2 + "/manifest.safe") < 1 and GeoPosition(
        ).roundedIntersect(scene1 + "/manifest.safe", scene2 + "/manifest.safe"):
            return True
        return False

    def writeGrdListToFile(self, array, resultFileName):
        # Delete files if exist
        if os.path.exists(resultFileName):
            os.remove(resultFileName)

        writeArray = open(resultFileName, "w")
        for item in array:
            writeArray.write(str(item) + "\n")
        writeArray.close()

    def writeSlcListToFile(self, array, array_coh_6d, array_coh_12d, resultFileName, resultFileNameCoh1,
                           resultFileNameCoh2):

        if os.path.exists(resultFileName):
            os.remove(resultFileName)
        if os.path.exists(resultFileNameCoh2):
            os.remove(resultFileNameCoh2)
        if os.path.exists(resultFileNameCoh1):
            os.remove(resultFileNameCoh1)
        if os.path.exists(resultFileNameCoh2):
            os.remove(resultFileNameCoh2)

        input2_6d = open(resultFileNameCoh1, 'w')
        input2_12d = open(resultFileNameCoh2, 'w')
        writeArray = open(resultFileName, "w")

        for item in array:
            writeArray.write(str(item) + "\n")

        for item in array_coh_6d:
            input2_6d.write(str(item) + "\n")

        for item in array_coh_12d:
            input2_12d.write(str(item) + "\n")

        writeArray.close()
        input2_6d.close()
        input2_12d.close()

    def readFileToList(self, listFileName):
        result = []
        with open(listFileName, 'r') as file:
            for line in file:
                entryList = line.replace("\n", "").split("', '")
                entryList = [entry.replace("'", "").replace("[", "").replace("]", "") for entry in entryList]
                result.append(entryList)
        return result

    def updateDuplicatePositions(self, indexDuplicates, acInfo):
        result = []
        for pos in indexDuplicates:
            newId = self.getInvalidSliceId(acInfo[pos-1][0], acInfo[pos][0], pos-1, pos)
            result.append(newId)
        return result

    def getInvalidSliceId(self, scene, scene2, index, index2):
        sliceId = self.__getSliceId(scene)
        sliceId2 = self.__getSliceId(scene2)
        return index if sliceId == 0 else index2

    def __getValidScene(self, scene, scene2):
        sliceId = self.__getSliceId(scene)
        sliceId2 = self.__getSliceId(scene2)

        result = []
        if sliceId != '0':
            result.append(scene)
        if sliceId2 != '0':
            result.append(scene2)

        return result
    
    def __getSliceId(self, scene):
        tree = etree.parse(scene + "/manifest.safe")
        root = tree.getroot()
        result = root.findall('.//{http://www.esa.int/safe/sentinel-1.0/sentinel-1/sar/level-1}sliceNumber')
        sliceNumber = result[0].text if result is not None and len(result) > 0 else None
        return sliceNumber

    def __getCohMatching(self, tile, tiles):
        dateAndTime = tile[3]
        time = dateAndTime[9:11]
        date1_str = tile[3][0: tile[3].index("T")]
        date1 = datetime.datetime.strptime(date1_str, "%Y%m%d")

        # date 2nd SLC pair
        d = datetime.timedelta(days=6)
        date2 = date1 + d
        date3 = date2 + d
        date2 = datetime.datetime.strftime(date2, "%Y%m%d")
        date3 = datetime.datetime.strftime(date3, "%Y%m%d")

        # print(date1_str, date2)

        # find 2nd SLC pair in input file list
        matching_SLC_6d = [s for s in tiles if date2 in s]
        matching_SLC_12d = [s for s in tiles if date3 in s]
        ### auch Orbit, Aufnahmezeitpunkt muss passen!!! Ausschnitt so gross, dass Frueh- und Nachmittagsaufnahmen
        time6d = date2 + 'T' + time
        matching_SLC_6d = [s for s in matching_SLC_6d if time6d in s]
        time12d = date3 + 'T' + time
        matching_SLC_12d = [s for s in matching_SLC_12d if time12d in s]
        return  matching_SLC_6d, matching_SLC_12d

    def __getMultipleCohMatchingLines(self, tile, elements, days):
        # check, if list includes SDV and SDH => skip  / maybe cross-pol is possible, to be checked
        test1 = [s for s in elements if '1SDH' in s]
        test = str(tile[0])
        test2 = test.find('1SDH')

        date1_str = tile[3][0: tile[3].index("T")]
        date1 = datetime.datetime.strptime(date1_str, "%Y%m%d")

        # date 2nd SLC pair
        d = datetime.timedelta(days=6)
        date2 = date1 + d
        date3 = date2 + d

        date = datetime.datetime.strftime(date2, "%Y%m%d") if days == 6 else datetime.datetime.strftime(date3,"%Y%m%d")
        outputProduct = "coh6d" if days == 6 else "coh12d"

        validElements = []
        for scene in elements:
            if len(test1) == 0 and test2 == -1 and GeoPosition().areaOverlap(tile[0] + "/manifest.safe", \
                    str(scene) + "/manifest.safe") > 0:
                uniqueId1 = '_' + tile[8]

                sceneIdList = scene.replace('/', "").replace(".SAFE", "").split("_")
                uniqueId2 = '_' + sceneIdList[len(sceneIdList)-1]

                uniqueId = uniqueId1 + uniqueId2 if self.__WITH_SCENE_ID else ""

                file_out = date1_str + '_' + date + '_' + tile[1] + '_' + tile[2] + '_' + \
                           tile[6] + '_' + tile[7] + uniqueId + '_' + outputProduct

                validElements.append([tile[0], scene, file_out])

        return validElements

    def __getMultSlicedCohMatchingLines(self, sliceMatching, cohMatching, tile, days):

        #This only works for AOIs that overlap max two scenes -> size sliceMatching, size cohMatching max 2
        if len(sliceMatching) == 1 and len(cohMatching) == 2:
            overlapS1Coh1 = GeoPosition().areaOverlap(str(sliceMatching[0]).strip(" ") + "/manifest.safe",
                                                      str(cohMatching[0]).strip(" ") + "/manifest.safe") > 1

            overlapS1Coh2 = GeoPosition().areaOverlap(str(sliceMatching[0]).strip(" ") + "/manifest.safe",
                                                      str(cohMatching[1]).strip(" ") + "/manifest.safe") > 1

            if overlapS1Coh1 and overlapS1Coh2:
                sliceMatching = [sliceMatching[0],sliceMatching[0]]

        elif len(sliceMatching) == 2 and len(cohMatching) == 1:
            overlapS1Coh1 = GeoPosition().areaOverlap(str(sliceMatching[0]).strip(" ") + "/manifest.safe",
                                                      str(cohMatching[0]).strip(" ") + "/manifest.safe") > 1

            overlapS2Coh1 = GeoPosition().areaOverlap(str(sliceMatching[1]) + "/manifest.safe",
                                                      str(cohMatching[0]).strip(" ") + "/manifest.safe") > 1

            if overlapS1Coh1 and overlapS2Coh1:
                cohMatching = [cohMatching[0],cohMatching[0]]

        elif len(sliceMatching) == 2 and len(cohMatching) == 2:

            overlapS1Coh1 = GeoPosition().areaOverlap(str(sliceMatching[0]).strip(" ") + "/manifest.safe",
                                                      str(cohMatching[0]).strip(" ") + "/manifest.safe") > 1.5

            overlapS1Coh2 = GeoPosition().areaOverlap(str(sliceMatching[0]).strip(" ") + "/manifest.safe",
                                                      str(cohMatching[1]).strip(" ") + "/manifest.safe") > 1.5

            overlapS2Coh1 = GeoPosition().areaOverlap(str(sliceMatching[1]).strip(" ") + "/manifest.safe",
                                                      str(cohMatching[0]).strip(" ") + "/manifest.safe") > 1.5

            overlapS2Coh2 = GeoPosition().areaOverlap(str(sliceMatching[1]).strip(" ") + "/manifest.safe",
                                                      str(cohMatching[1]).strip(" ") + "/manifest.safe") > 1.2

            if not overlapS1Coh1 and not overlapS1Coh2 and overlapS2Coh1 and overlapS2Coh2:
                sliceMatching = [sliceMatching[1],sliceMatching[1]]
            elif not overlapS2Coh1 and not overlapS2Coh2 and overlapS1Coh1 and overlapS1Coh2:
                sliceMatching = [sliceMatching[0],sliceMatching[0]]
            elif not overlapS1Coh1 and not overlapS2Coh1 and overlapS1Coh2 and overlapS2Coh2:
                cohMatching = [cohMatching[1],cohMatching[1]]
            elif not overlapS1Coh2 and not overlapS2Coh2 and overlapS1Coh1 and overlapS2Coh1:
                cohMatching = [cohMatching[0],cohMatching[0]]
            elif overlapS1Coh2:
                sliceMatching = [sliceMatching[0]]
                cohMatching = [cohMatching[1]]
            elif overlapS2Coh1:
                sliceMatching = [sliceMatching[1]]
                cohMatching = [cohMatching[0]]

        # Create string attachment for output file name with unique id suffix
        # for each relevant scene.
        uniqueId = ""
        sceneCollection = sliceMatching + cohMatching
        for col in sceneCollection:
            sceneIdList = col.replace('/', "").replace(".SAFE", "").split("_")
            uniqueId = uniqueId + '_' + sceneIdList[len(sceneIdList) - 1]

        uniqueId = uniqueId if self.__WITH_SCENE_ID else ""
        date1_str = tile[3][0: tile[3].index("T")]
        date1 = datetime.datetime.strptime(date1_str, "%Y%m%d")

        # date 2nd SLC pair
        d = datetime.timedelta(days=days)
        date2 = date1 + d
        date2 = datetime.datetime.strftime(date2, "%Y%m%d")

        outputProduct = "coh6d" if days == 6 else "coh12d"

        matchStr = str(sliceMatching)
        matchStr = matchStr.replace("'", "")
        matchStr = matchStr.replace("[", "")
        matchStr = matchStr.replace("]", "")

        cohMatching = str(cohMatching)
        cohMatching = cohMatching.replace("'", "")
        cohMatching = cohMatching.replace("[", "")
        cohMatching = cohMatching.replace("]", "")
        file_out = date1_str + '_' + date2 + '_' + tile[1] + '_' + tile[2] + '_' + \
                   tile[6] + '_' + tile[7] + uniqueId + '_' + outputProduct

        # write to array
        return [matchStr, cohMatching, file_out]
