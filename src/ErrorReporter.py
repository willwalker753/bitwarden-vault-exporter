from Logger import Logger
import sentry_sdk
from sentry_sdk import capture_exception

class ErrorReporter:
    def __init__(self, 
            glitchtipDsn,
            logger:Logger,
        ):
        self.glitchtipDsn = glitchtipDsn
        self.logger = logger
        sentry_sdk.init(
            dsn=self.glitchtipDsn,
            # debug=True, # commented out because it very verbose, but it is good for debugging if errors aren't being sent to glitchtip
        )

    def sendError(self, e:Exception):
        self.logger.error(f'Caught exception and reporting it to GlitchTip: {e}')
        capture_exception(e)
        return self