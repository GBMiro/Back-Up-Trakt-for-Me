from Utils.Logger import Logger
import Utils.StatusCodes as StatusCodes
import Utils.Exporting as Folders
from datetime import datetime
import os
import json

class ExporterJSON:

    def __init__(self, showLog):
        self.logger = Logger(showLog, "EXPORTER")
        self.path = ''
    
    def CreateExportFolders(self):
        self.logger.ShowMessage("Creating backup folders...")

        date = datetime.now().strftime("%Y%m%d %H.%M.%S")
        self.path = '.\\{}'.format(date)

        self.__CreateFolder(self.path)
        self.__CreateFolder(self.path + '\\{}'.format(Folders.RATINGS_FOLDER))
        self.__CreateFolder(self.path + '\\{}'.format(Folders.WATCHED_FOLDER))
        self.__CreateFolder(self.path + '\\{}'.format(Folders.LISTS_FOLDER))
        self.__CreateFolder(self.path + '\\{}'.format(Folders.COLLECTION_FOLDER))
        self.__CreateFolder(self.path + '\\{}'.format(Folders.HISTORY_FOLDER))

    def __CreateFolder(self, folder):
        try:
            if (not os.path.exists(folder)):
                os.mkdir(folder)
                self.logger.ShowMessage("{} folder created".format(folder))
        except OSError as err:
            self.logger.ShowMessage("An error occurred creating folder {}".format(err))

    def ExportData(self, data, folder, filename):
        filePath = self.path + '\\{}\\{}.json'.format(folder, filename)
        statusCode = StatusCodes.EXPORTER_OK
        try:
            with open(filePath, 'w', encoding='utf-8') as file:
                json.dump(data, file, ensure_ascii=False, indent=4)
            message = "{} file created".format(filePath)  
        except Exception as err:
            message = "An error occured creating the file ({}). {}".format(filePath, err)
            statusCode = StatusCodes.EXPORTER_ERROR
        finally:
            self.logger.ShowMessage(message)
            return statusCode