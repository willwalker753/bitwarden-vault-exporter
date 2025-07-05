from Logger import Logger
import os
import json
from typing import List
import subprocess

class BitwardenCmdAgent:
    def __init__(self, 
            bwClientId:str,
            bwClientSecret:str,
            bwPassword:str,
            bwCliPath:str, # path to the bitwarden "bw" command package for linux
            logger:Logger,
        ):
        self._bwCliPath = bwCliPath
        self._logger = logger
        self._env = os.environ.copy()
        self._env = {
            **os.environ.copy(),
            'BW_CLIENTID': bwClientId, # yes the missing underscore is intentional. that is what bw expects
            'BW_CLIENTSECRET': bwClientSecret, 
            'BW_PASSWORD': bwPassword,
        }

    def login(self) -> 'BitwardenCmdAgent':
        self._logger.info('Running bitwarden login command')
        loginRes = self._run_cmd([
            self._bwCliPath, 
            'login', 
            '--apikey', 
            '--raw'
        ], capture_output=True)
        sessionKey = loginRes.strip()
        self._env['BW_SESSION'] = sessionKey
        return self

    def logout(self) -> 'BitwardenCmdAgent':
        self._logger.info('Running bitwarden logout command')
        self._enforce_auth('logout')
        self._run_cmd([
            self._bwCliPath, 
            'logout'
        ], capture_output=False)
        if 'BW_SESSION' in self._env:
            del self._env['BW_SESSION']
        return self

    def unlock(self) -> 'BitwardenCmdAgent':
        self._logger.info('Running bitwarden unlock command')
        self._enforce_auth('unlock')
        unlockRes = self._run_cmd([
            self._bwCliPath, 
            'unlock',
            '--passwordenv', 'BW_PASSWORD',
            '--raw'
        ], capture_output=True)
        self._env['BW_SESSION'] = unlockRes.strip()
        return self

    def export(self, targetJsonFilePath) -> dict:
        self._logger.info('Running bitwarden export command')
        self._enforce_auth('export')
        self._run_cmd([
            self._bwCliPath, 
            'export',
            '--format', 'json',
            '--output', targetJsonFilePath
        ], capture_output=False)
        os.chmod(targetJsonFilePath, 0o666) # set file permissions to 666
        with open(targetJsonFilePath, mode='r') as targetF:
            data = json.load(targetF)
        return data

    def _enforce_auth(self, commandName):
        if not 'BW_SESSION' in self._env:
            raise Exception(f'Must login before running the {commandName} command')

    def _run_cmd(self, command:List[str], capture_output:bool):
        try:
            result = subprocess.run(
                command,
                check=True,
                text=True,
                stdout=subprocess.PIPE if capture_output else None,
                stderr=subprocess.PIPE,
                env=self._env
            )
            return result.stdout.strip() if capture_output else None
        except subprocess.CalledProcessError as e:
            self._logger.error(f'Command failed: {' '.join(command)}')
            self._logger.error(f'Error output of command: {e.stderr.strip()}')
            raise e
