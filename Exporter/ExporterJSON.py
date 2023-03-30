from Utils.Logger import Logger
import Utils.UI as UI
import Utils.StatusCodes as StatusCodes
import Utils.Exporting as Folders
from datetime import datetime
import os
import json

class ExporterJSON:

    def __init__(self, showLog, path):
        self.logger = Logger(showLog, "EXPORTER")
        self.path = path
        self.backupFolder = ''
    
    def CreateExportFolders(self):
        self.logger.ShowMessage("Creating backup folders...")

        date = datetime.now().strftime("%Y%m%d %H.%M.%S")
        self.backupFolder = os.path.join('.','{}'.format(date)) if (self.path is None) else os.path.join(self.path, '{}'.format(date))

        self.__CreateFolder(self.backupFolder)
        self.__CreateFolder(os.path.join(self.backupFolder, '{}'.format(Folders.RATINGS_FOLDER)))
        self.__CreateFolder(os.path.join(self.backupFolder, '{}'.format(Folders.WATCHED_FOLDER)))
        self.__CreateFolder(os.path.join(self.backupFolder, '{}'.format(Folders.WATCHLIST_FOLDER)))
        self.__CreateFolder(os.path.join(self.backupFolder, '{}'.format(Folders.COLLECTION_FOLDER)))
        self.__CreateFolder(os.path.join(self.backupFolder, '{}'.format(Folders.LISTS_FOLDER)))

    def __CreateFolder(self, folder):
        try:
            if (not os.path.exists(folder)):
                os.mkdir(folder)
                self.logger.ShowMessage("{} folder created".format(folder))
        except OSError as err:
            self.logger.ShowMessage("An error occurred creating folder {}".format(err), UI.ERROR_LOG)

    def ExportData(self, data, folder, filename):
        filePath = os.path.join(self.backupFolder,'{}'.format(folder),'{}.json'.format(filename))
        statusCode = StatusCodes.EXPORTER_OK
        try:
            with open(filePath, 'w', encoding='utf-8') as file:
                json.dump(data, file, ensure_ascii=False, indent=4)
            self.logger.ShowMessage("{} file created".format(filePath))
        except Exception as err:
            self.logger.ShowMessage("An error occured creating the file ({}). {}".format(filePath, err), UI.ERROR_LOG)
            statusCode = StatusCodes.EXPORTER_ERROR
        finally:
            return statusCode
        
    def SetBackupFolder(self, folder):
        self.path = folder