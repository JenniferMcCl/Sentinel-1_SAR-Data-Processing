#--------------------------------------------------------------------------------------------------------------------------------
# Name:        create_user_setting
# Purpose:
#
# Author:      jennifer.mcclelland
#
# Created:     2022
# Copyright:   (c) jennifer.mcclelland 2022
#
# ----This class creates a file outside of the repository folder to define all user specific paths necessary for processing
#-----the Sentinel-1 SAR data.
#-----In this .xml file named "user_settings" the user must set the main path for the processing as well as a path for each processing sequence.
#-----The Area of interest must be set, either as wkt string, as path to geojson file or as path the a folder containing multiple geojson files.
#-----The start and end date must be set to define the time range within to aquire the data in.
#-----A name extension can be set to be added to each output file name.
#-----The processing sequence must be set.
#-----All these settings must be saved in the user_settings.xml file and are accessed during processing.
#--------------------------------------------------------------------------------------------------------------------------------

import os
from os.path import exists
from lxml import etree


class CreateUserSetting:

    dataPath = ""
    cohOutputPath = ""
    backscatterOutputPath = ""
    dpVegIndexPath = ""
    calculationStartDate = ""
    calculationEndDate = ""
    aoiLocation = ""
    areaName = ""
    processingSequence = ""
    currentAoi = ""
    processingList = ""
    processingMode = ""

    def __init__(self):

        # Get the repository folder path
        workingPath = os.getcwd()
        self.userFolder = workingPath.split("/Sentinel-1-SLC-process")

        # Create user setting file if not available
        file_exists = exists(self.userFolder[0] + "/user_settings.xml")

        if not file_exists:

            root = etree.Element("root")
            paths = etree.SubElement(root, "paths")
            etree.SubElement(paths, "data", name="sentinel data").text = ""
            etree.SubElement(paths, "cohOutput", name="coherence output").text = ""
            etree.SubElement(paths, "backscatterOutput", name="backscatter result").text = ""
            etree.SubElement(paths, "vegIdOutput", name="dp veg id output").text = ""
            etree.SubElement(paths, "calculationStartDate", name="start date for calculation").text = ""
            etree.SubElement(paths, "calculationEndDate", name="end date for calculation").text = ""
            etree.SubElement(paths, "aoiLocation", name="coordinates of Aoi for calculation").text = ""
            etree.SubElement(paths, "areaName", name="name of area").text = ""
            etree.SubElement(paths, "processingSequence", name="sequence to process").text = ""
            etree.SubElement(paths, "folderToProcessByList", name="scene list folder containing lists of scenes as txt file").text = ""
            etree.SubElement(paths, "processingMode", name="Mode to handle derived scenes").text = ""

            etree.ElementTree(root)
            prettyString = etree.tostring(root, pretty_print=True, encoding='unicode')

            with open(self.userFolder[0] + "/user_settings.xml", "w") as f:
                f.write(prettyString)

            print("User setting file has been created at: " + self.userFolder[0] + "/user_settings.xml")
            print("User folder paths and attributes must now be set in user_settings.xml file")
        else:
            print("User setting file available at: " + self.userFolder[0] + "/user_settings.xml")
            tree = etree.parse(self.userFolder[0] + '/user_settings.xml')
            root = tree.getroot()

            paths = root.find("paths")
            if len(root.find("paths")) < 11:
                etree.SubElement(paths, "folderToProcessByList", name="scene list folder containing lists of scenes as txt file").text = ""
                etree.SubElement(paths, "processingMode", name="Mode to handle derived scenes").text = ""
                etree.ElementTree(root)
                prettyString = etree.tostring(root, pretty_print=True, encoding='unicode')

                with open(self.userFolder[0] + "/user_settings.xml", "w") as f:
                    f.write(prettyString)

        if len(root.find("paths")) == 11:
            self.dataPath = root[0][0].text
            self.cohOutputPath = root[0][1].text
            self.backscatterOutputPath = root[0][2].text
            self.dpVegIndexPath = root[0][3].text
            self.calculationStartDate = root[0][4].text
            self.calculationEndDate = root[0][5].text
            self.aoiLocation = root[0][6].text
            self.areaName = root[0][7].text
            self.processingSequence = root[0][8].text
            self.processingList = root[0][9].text
            self.processingMode = root[0][10].text
        else:
            print("user_settings.xml file Error")

    def setAttribute(self, attribute, value):
        tree = etree.parse(self.userFolder[0] + '/user_settings.xml')
        root = tree.getroot()
        read = root.xpath("//" + attribute)
        read[0].text = value
        prettyString = etree.tostring(root, pretty_print=True, encoding='unicode')
        with open(self.userFolder[0] + '/user_settings.xml', "w") as f:
            f.write(prettyString)
