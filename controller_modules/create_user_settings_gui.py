#--------------------------------------------------------------------------------------------------------------------------------
# Name:        create_user_setting_gui
# Purpose:
#
# Author:      jennifer.mcclelland
#
# Created:     2022
# Copyright:   (c) jennifer.mcclelland 2022
#
# ----This class offers a graphical access to the user_settings-xml file
#-----Here all user_settings can be set over a gui.
#-----The defined processing sequence can be triggered via a button.
#-----User information is displayed if any relevant are missing.
#-----All settings are saved in the settings file via the start button.
#-----If the area of interest is entered as wkt, an equivalent geojson file is created and saved in the test_file folder.
#-----Either a wkt or geojson must be set to avoid inconsistencies.
#-----If a json file is already given and loaded the equivalent wkt is displayed in the graphfical window as convienience.
#--------------------------------------------------------------------------------------------------------------------------------

from tkinter import *
import threading

from controller_modules.create_user_setting_file import CreateUserSetting
from controller_modules.geo_position import GeoPosition


class CreateUserSettingsGui:

    userSettings = None
    entryStartDate = None
    entryEndDate = None
    entryWkt = None
    entryGeoJson = None
    entryNameExt = None
    entryOutputPath = None
    entryBackscatterPath = None
    entryCohPath = None
    entryVegIdPath = None
    entryProcessingList = None
    varProcessingSpinbox = None
    varProcessingModeSpinbox = None
    displayLabelVar = None
    executionfunction = None

    def __init__(self, executionFunction):
        self.userSettings = CreateUserSetting()
        self.executionfunction = executionFunction
        self.processingThread = threading.Thread(target=self.executionfunction, args=(self.userSettings,))

    def runGui(self):
        self.makeGui()
        self.loadSettings()
        mainloop()

    def makeGui(self):

        master = Tk()
        master.geometry("800x450")
        Label(master,text="Enter All Attributes for processing").grid(row=0, column = 1, padx=5, pady=5)

        Label(master,text="Start Date in Format 'YYYY-MM-DD'").grid(row=1, column=0, sticky = 'w', padx=5, pady=5)
        self.entryStartDate = Entry(master, width = 25)
        self.entryStartDate.grid(row=1, column=1,sticky = 'w', padx=5, pady=5)

        Label(master,text="End Date in Format 'YYYY-MM-DD'").grid(row=2, column=0, sticky = 'w', padx=5, pady=5)
        self.entryEndDate = Entry(master, width = 25)
        self.entryEndDate.grid(row=2, column=1, sticky = 'w', padx=5, pady=5)

        Label(master,text="AOI as Wkt").grid(row=3, column=0, sticky = 'w', padx=5, pady=5)
        self.entryWkt = Entry(master, width = 75)
        self.entryWkt.grid(row=3, column=1, sticky = 'w', padx=5, pady=5)

        Label(master,text="AOI GeoJson File or Folder").grid(row=4, column=0, sticky = 'w', padx=5, pady=5)
        self.entryGeoJson = Entry(master, width = 75)
        self.entryGeoJson.grid(row=4, column=1, sticky = 'w', padx=5, pady=5)

        Label(master,text="AOI Output File Name Extension").grid(row=5, column=0, sticky = 'w', padx=5, pady=5)
        self.entryNameExt = Entry(master, width = 50)
        self.entryNameExt.grid(row=5, column=1, sticky = 'w', padx=5, pady=5)

        Label(master,text="Output Result Folder path").grid(row=6, column=0, sticky = 'w', padx=5, pady=5)
        self.entryOutputPath = Entry(master, width = 75)
        self.entryOutputPath.grid(row=6, column=1)

        Label(master,text="Backscatter Folder path").grid(row=7, column=0, sticky = 'w', padx=5, pady=5)
        self.entryBackscatterPath = Entry(master, width = 75)
        self.entryBackscatterPath.grid(row=7, column=1, padx=5, pady=5)

        Label(master,text="Coherence Folder path").grid(row=8, column=0, sticky = 'w', padx=5, pady=5)
        self.entryCohPath = Entry(master, width = 75)
        self.entryCohPath.grid(row=8, column=1, padx=5, pady=5)

        Label(master,text="Vegetation Index path").grid(row=9, column=0, sticky = 'w', padx=5, pady=5)
        self.entryVegIdPath = Entry(master, width = 75)
        self.entryVegIdPath.grid(row=9, column=1, padx=5, pady=5)

        Label(master, text="Folder with Lists as txt to process").grid(row=10, column=0, sticky='w', padx=5, pady=5)
        self.entryProcessingList = Entry(master, width=75)
        self.entryProcessingList.grid(row=10, column=1, padx=5, pady=5)

        Label(master,text="Processing Sequence").grid(row=11, column=0, sticky = 'w', padx=5, pady=5)

        data = ['Coherence', 'Radar Vegetation Index', 'Backscatter', 'All']
        self.varProcessingSpinbox = StringVar(master)
        processingSequence = Spinbox(master, values=data, textvariable=self.varProcessingSpinbox, width=50, font="Calibri, 12")
        self.varProcessingSpinbox.set('All')
        processingSequence.grid(row=11, column=1, sticky = 'w', padx=5, pady=5)

        Label(master, text="Processing Mode").grid(row=12, column=0, sticky='w', padx=5, pady=5)
        data = ['AOI Processing', 'Scene Processing']
        self.varProcessingModeSpinbox = StringVar(master)
        processingMode = Spinbox(master, values=data, textvariable=self.varProcessingModeSpinbox, width=50,
                                     font="Calibri, 12")
        self.varProcessingModeSpinbox.set('AOI Processing')
        processingMode.grid(row=12, column=1, sticky='w', padx=5, pady=5)

        Button(master, text='Save All and execute', command=self.saveAllSettings).grid(row=13, column=0, sticky='',
                                                                                       padx=10, pady=10)

        self.displayLabelVar = StringVar(master)
        Label(master, textvariable = self.displayLabelVar, bg = 'yellow', fg='red', width = 70, height = 3).grid(
            row=13, column=1, columnspan = 10, rowspan = 10, sticky = 'w', padx=5, pady=5)

    def loadSettings(self):
        if (self.userSettings.calculationStartDate != None and self.userSettings.calculationStartDate != ""):
            self.entryStartDate.insert(0, self.userSettings.calculationStartDate)

        if (self.userSettings.calculationEndDate != None and self.userSettings.calculationEndDate != ""):
            self.entryEndDate.insert(0, self.userSettings.calculationEndDate)

        if (self.userSettings.aoiLocation != None and self.userSettings.aoiLocation != "" and
                ".geojson" in self.userSettings.aoiLocation):
            self.entryWkt.insert(0, GeoPosition().loadWktFromGeojson(self.userSettings.aoiLocation))

        if (self.userSettings.aoiLocation != None and self.userSettings.aoiLocation != ""):
            self.entryGeoJson.insert(0, self.userSettings.aoiLocation)

        if (self.userSettings.areaName != None and self.userSettings.areaName != ""):
            self.entryNameExt.insert(0, self.userSettings.areaName)

        if (self.userSettings.dataPath != None and self.userSettings.dataPath != ""):
            self.entryOutputPath.insert(0, self.userSettings.dataPath)

        if (self.userSettings.backscatterOutputPath != None and self.userSettings.backscatterOutputPath != ""):
            self.entryBackscatterPath.insert(0, self.userSettings.backscatterOutputPath)

        if (self.userSettings.cohOutputPath != None and self.userSettings.cohOutputPath != ""):
            self.entryCohPath.insert(0, self.userSettings.cohOutputPath)

        if (self.userSettings.dpVegIndexPath != None and self.userSettings.dpVegIndexPath != ""):
            self.entryVegIdPath.insert(0, self.userSettings.dpVegIndexPath)

        if (self.userSettings.processingList != None and self.userSettings.processingList != ""):
            self.entryProcessingList.insert(0, self.userSettings.processingList)

        if (self.userSettings.processingSequence != None and self.userSettings.processingSequence != ""):
            self.varProcessingSpinbox.set(self.userSettings.processingSequence)

        if (self.userSettings.processingMode != None and self.userSettings.processingMode != ""):
            self.varProcessingModeSpinbox.set(self.userSettings.processingMode)

    def saveAllSettings(self):
        entriesComplete = ""
        if (self.entryStartDate.get() != "" and self.entryEndDate.get() != ""):
            self.userSettings.setAttribute("calculationStartDate", self.entryStartDate.get())
            self.userSettings.setAttribute("calculationEndDate", self.entryEndDate.get())
            self.userSettings.calculationStartDate = self.entryStartDate.get()
            self.userSettings.calculationEndDate = self.entryEndDate.get()
        else:
            entriesComplete = "Dates"

        if (self.entryGeoJson.get() != "" and self.entryWkt.get() != ""):
            self.displayLabelVar.set("Enter only one type of Aoi. Either wkt or geojson")
            entriesComplete = "Aoi"
        elif (self.entryGeoJson.get() != ""):
            self.userSettings.setAttribute("aoiLocation", self.entryGeoJson.get())
            self.userSettings.aoiLocation = self.entryGeoJson.get()
            self.userSettings.currentAoi = self.entryGeoJson.get()
        elif (self.entryWkt.get() != "" and self.entryOutputPath.get() != ""):
            geoJson = GeoPosition().wktToGeojsonShapely(self.entryWkt.get())
            with open(self.entryOutputPath.get() + 'aoi.geojson', 'w') as f:
                f.writelines(str(geoJson))
                f.close()
            self.displayLabelVar.set("Geojson: " + self.entryOutputPath.get() + "\naoi.geojson" + " saved.")
            self.userSettings.setAttribute("aoiLocation", self.entryOutputPath.get() + 'aoi.geojson')
            self.userSettings.aoiLocation = self.entryOutputPath.get() + 'aoi.geojson'
            self.userSettings.currentAoi = self.entryOutputPath.get() + 'aoi.geojson'
            self.entryGeoJson.insert(0, self.entryOutputPath.get() + 'aoi.geojson')
            return
        elif (self.entryGeoJson.get() == "" and self.entryWkt.get() == ""):
            entriesComplete = "Aoi"

        if (self.entryOutputPath.get() !=""):
            self.userSettings.setAttribute("data", self.entryOutputPath.get())
            self.userSettings.cohOutputPath = self.entryOutputPath.get()
        else:
            entriesComplete = "Output Result Folder path"

        if (self.entryBackscatterPath.get() == "" and (self.varProcessingSpinbox.get() == "Backscatter" or self.varProcessingSpinbox.get() == "All")):
            entriesComplete = "Backscatter"
        else:
            self.userSettings.setAttribute("backscatterOutput", self.entryBackscatterPath.get())
            self.userSettings.backscatterOutputPath = self.entryBackscatterPath.get()

        if (self.entryCohPath.get() =="" and (self.varProcessingSpinbox.get() == "Coherence" or self.varProcessingSpinbox.get() == "All")):
            entriesComplete = "Coherence"
        else:
            self.userSettings.setAttribute("cohOutput", self.entryCohPath.get())
            self.userSettings.cohOutputPath = self.entryCohPath.get()

        if (self.entryVegIdPath.get() =="" and (self.varProcessingSpinbox.get() == "Radar Vegetation Index" or self.varProcessingSpinbox.get() == "All")):
            entriesComplete = "Vegetation Index"
        else:
            self.userSettings.setAttribute("vegIdOutput", self.entryVegIdPath.get())
            self.userSettings.dpVegIndexPath = self.entryVegIdPath.get()

        if (self.entryProcessingList.get() !="" ):
            self.userSettings.setAttribute("folderToProcessByList", self.entryProcessingList.get())
            self.userSettings.processingList = self.entryProcessingList.get()

        if (self.entryNameExt.get() !=""):
            self.userSettings.setAttribute("areaName", self.entryNameExt.get())
            self.userSettings.areaName = self.entryNameExt.get()

        if (self.varProcessingSpinbox.get() !=""):
            self.userSettings.setAttribute("processingSequence", self.varProcessingSpinbox.get())
            self.userSettings.processingSequence = self.varProcessingSpinbox.get()

        if (self.varProcessingSpinbox.get() != ""):
            self.userSettings.setAttribute("processingMode", self.varProcessingModeSpinbox.get())
            self.userSettings.processingMode = self.varProcessingModeSpinbox.get()

        if (entriesComplete != ""):
            if entriesComplete == "Aoi": 
                self.displayLabelVar.set("Aoi Entry not Correct.\n EITHER Aoi in Wkt format OR path must be set.")
            else:
                self.displayLabelVar.set("Missing " + entriesComplete + " entry for processing.\n Ensure all entries are set for selected processing sequence.")
            return
        else:
            self.processingThread.start()
            self.displayLabelVar.set("Processing sequence '" + str(self.varProcessingSpinbox.get()) + "' has started")

