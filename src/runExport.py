
'''
Bitwarden Vault Export Script
Requirements:
    - Docker
    - Configured GlitchTip/Sentry DSN
    - Environment variables: 
        - GLITCHTIP_DSN  # e.g. http://asdfasdf@glitchtip-web-service:5040/1
        - EXPORT_DIR_PATH  # remember, this path is inside the container. you'll need to access it with a docker volume
        - EXPORT_ROTATE_MIN_FILES
        - EXPORT_ROTATE_TTL_HOURS
        - BW_CLIENT_ID
        - BW_CLIENT_SECRET
        - BW_PASSWORD
        - BW_CLI_PATH  # this is set for you by the dockerfile
'''

import json
import sentry_sdk

from Logger import Logger
logger = Logger()

from ConfigLoader import ConfigLoader
configLoader = ConfigLoader()

from ErrorReporter import ErrorReporter
glitchtipDsn = configLoader.get('GLITCHTIP_DSN').strip() 
errorReporter = ErrorReporter(
    glitchtipDsn,
    logger
)

def main():
    try:
        from FileRotator import FileRotator
        exportDirPath = configLoader.get('EXPORT_DIR_PATH').strip()
        exportMinFiles = int(configLoader.get('EXPORT_ROTATE_MIN_FILES').strip())
        exportTtlHours = int(configLoader.get('EXPORT_ROTATE_TTL_HOURS').strip())
        exportRotator = FileRotator(
            exportDirPath,
            'bitwarden_export',
            'json',
            exportMinFiles,            
            exportTtlHours,
            logger
        )

        from BitwardenCmdAgent import BitwardenCmdAgent
        bwClientId = configLoader.get('BW_CLIENT_ID').strip()
        bwClientSecret = configLoader.get('BW_CLIENT_SECRET').strip()
        bwPassword = configLoader.get('BW_PASSWORD').strip()
        bwCliPath = configLoader.get('BW_CLI_PATH').strip()
        bwCmdAgent = BitwardenCmdAgent(
            bwClientId,
            bwClientSecret,
            bwPassword,
            bwCliPath,
            logger
        )

        logger.info('Starting Bitwarden backup process')            
        bwCmdAgent.login()
        bwCmdAgent.unlock()
        exportFilePath = exportRotator.createNewFilePath()
        bwCmdAgent.export(exportFilePath)
        bwCmdAgent.logout()
        
        # delete old files
        exportRotator.rotateFiles()

        # validate the export
        with open(exportFilePath, 'r') as f:
            data = json.load(f)
            if data.get('encrypted') or not data.get('items'):
                raise ValueError(f'Validation failed. Invalid export file structure. exportFilePath: {exportFilePath}')
            logger.info(f'Success! Exported {len(data['items'])} items')

    except Exception as e:
        logger.error(f'Caught exception and reporting it to GlitchTip: {e}')
        sentry_sdk.capture_exception(e)
        exit(1)
    exit(0)

if __name__ == "__main__":
    main()