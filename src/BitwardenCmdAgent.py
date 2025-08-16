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
            'BW_CLIENTID': bwClientId, # the missing underscore is intentional. that is what bw expects
            'BW_CLIENTSECRET': bwClientSecret, 
            'BW_PASSWORD': bwPassword,
        }

    def safeLogin(self) -> 'BitwardenCmdAgent':
        try:
            self.login()
            return self
        except subprocess.CalledProcessError as e:
            # logout before logging in if there is already a session
            if ('already logged in' in e.stderr.strip().lower()):
                self.logout()
                self.login()
                return self
            raise e

    def login(self) -> 'BitwardenCmdAgent':
        self._logger.info('Running bitwarden login command')
        loginOutput = self._run_cmd([
            self._bwCliPath, 
            'login', 
            '--apikey', 
            '--raw'
        ], capture_output=True)
        print(f'Login cmd output: {loginOutput}')
        sessionKey = loginOutput.strip()
        self._env['BW_SESSION'] = sessionKey
        return self

    def logout(self) -> 'BitwardenCmdAgent':
        self._logger.info('Running bitwarden logout command')
        self._enforce_auth('logout')
        logoutOutput = self._run_cmd([
            self._bwCliPath, 
            'logout'
        ], capture_output=True)
        print(f'Logout cmd output: {logoutOutput}')
        if 'BW_SESSION' in self._env:
            del self._env['BW_SESSION']
        return self

    def unlock(self) -> 'BitwardenCmdAgent':
        self._logger.info('Running bitwarden unlock command')
        self._enforce_auth('unlock')
        unlockOutput = self._run_cmd([
            self._bwCliPath, 
            'unlock',
            '--passwordenv', 'BW_PASSWORD',
            '--raw'
        ], capture_output=True)
        print(f'Unlock cmd output: {unlockOutput}')
        self._env['BW_SESSION'] = unlockOutput.strip()
        return self

    def export(self, targetJsonFilePath) -> dict:
        self._logger.info('Running bitwarden export command')
        self._enforce_auth('export')
        exportOutput = self._run_cmd([
            self._bwCliPath, 
            'export',
            '--format', 'json',
            '--output', targetJsonFilePath
        ], capture_output=True)
        print(f'Export cmd output: {exportOutput}')
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
