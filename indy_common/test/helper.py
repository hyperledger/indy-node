import os
import shutil
import psutil

from stp_core.common.log import getlogger

logger = getlogger()


class TempStorage:
    @staticmethod
    def getOpenFdsUnder(dirPath):
        proc = psutil.Process()
        # return {f.fd for f in proc.open_files()
        #         if os.path.dirname(f.path) == dirPath}
        r = set()
        for f in proc.open_files():
            if os.path.dirname(f.path) == dirPath:
                logger.debug(
                    'Going to close before deleting: {}'.format(f.path))
                r.add(f.fd)
        return r

    @staticmethod
    def closeFdsUnder(dirPath):
        for fd in TempStorage.getOpenFdsUnder(dirPath):
            os.close(fd)

    @staticmethod
    def cleanupDirectory(dirPath):
        try:
            # Uncommenting the next line causes random socket failures, from
            # Python docs, "This function is intended for low-level I/O and
            # must be applied to a file descriptor as returned by
            # os.open() or pipe()"
            # TempStorage.closeFdsUnder(dirPath)
            shutil.rmtree(dirPath)
        except Exception as ex:
            logger.debug(
                "Error while removing temporary directory {}".format(ex))

    def cleanupDataLocation(self):
        self.cleanupDirectory(self.dataLocation)
        try:
            odbClient = self.graphStore.client
            odbClient.db_drop(self.name)
            logger.debug("Dropped db {}".format(self.name))
        except Exception as ex:
            logger.debug("Error while dropping db {}: {}".format(self.name,
                                                                 ex))
