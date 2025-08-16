from Logger import Logger
import datetime
import os
import math

class FileRotator:
    def __init__(self,
            dirPath:str,
            fileNamePrepend:str,
            fileExtension:str,
            minCopies:int,            
            ttlHours:int,
            logger:Logger
        ):
        self._dirPath = dirPath
        self._fileNamePrepend = fileNamePrepend
        self._fileExtension = fileExtension
        self._minCopies = minCopies
        self._ttlHours = ttlHours
        self._logger = logger
        self._dtFormat = '%Y%m%d_%H%M%S%z'
    
    def createNewFilePath(self) -> str:
        timestamp = datetime.datetime.now(datetime.UTC).strftime(self._dtFormat)
        fileName = f'{self._fileNamePrepend}-{timestamp}.{self._fileExtension.strip('.')}'
        filePath = os.path.join(self._dirPath, fileName)
        self._logger.info(f'New rotator file path: {filePath}')
        return filePath

    def rotateFiles(self) -> 'FileRotator':
        allFilePaths = []
        delFilePaths = []
        for fileName in os.listdir(self._dirPath):
            filePath = os.path.join(self._dirPath, fileName)
            if not fileName.startswith(self._fileNamePrepend) or not fileName.endswith(self._fileExtension):
                self._logger.warning(f'Found unexpected file in the "{self._fileNamePrepend}" file rotator directory. filePath: {filePath}')
                continue

            allFilePaths.append(filePath)
            nowDt = datetime.datetime.now(datetime.UTC)
            fileDtRaw = fileName.replace(self._fileNamePrepend, '').replace(self._fileExtension, '').strip('-').strip('.')
            fileDt = datetime.datetime.strptime(fileDtRaw, self._dtFormat)
            seconds = math.floor((nowDt - fileDt).total_seconds())
            hours = math.floor(seconds / 60 / 60)
            if hours >= self._ttlHours:
                delFilePaths.append(filePath)

        # ensure the files are sorted by date desc
        allFilePaths.sort(reverse=True)
        delFilePaths.sort(reverse=True)
        
        if len(allFilePaths) < self._minCopies:
            self._logger.warning(f'Unable to rotate "{self._fileNamePrepend}" files. Only found {len(allFilePaths)} files but at least {self._minCopies} must exist before they can be rotated.')
            return self

        if len(allFilePaths) == len(delFilePaths):
            self._logger.warning(f'Unable to rotate "{self._fileNamePrepend}" files. Script is wanting to remove all {len(allFilePaths)} files. This can mean that new files are not being generated.')
            return self

        # if by removing all files to remove the min copies requirement is not satified
        # then only delete the oldest files without going under the min copies
        fileCountRemaining = len(allFilePaths) - len(delFilePaths)
        if fileCountRemaining < self._minCopies:
            fileCountToNotDel = self._minCopies - fileCountRemaining
            delFilePaths = delFilePaths[fileCountToNotDel:]

        for i, delFilePath in enumerate(delFilePaths):
            self._logger.info(f'[{i+1}/{len(delFilePaths)}] Deleting old file that is past the ttlHours value of {self._ttlHours}. filePath: {delFilePath}')
            os.remove(delFilePath)
        return self
