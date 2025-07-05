import datetime

class Logger:
    def debug(self, message):
        self._log('DEBUG', message)
        return self

    def info(self, message):
        self._log('INFO', message)
        return self
    
    def warning(self, message):
        self._log('WARNING', message)
        return self

    def error(self, message):
        self._log('ERROR', message)
        return self

    def _log(self, level, message):
        utcStr = datetime.datetime.now(datetime.UTC).strftime('%Y-%m-%d %H:%M:%S')
        print(f'{utcStr} UTC - {level}: {message}')
        return self