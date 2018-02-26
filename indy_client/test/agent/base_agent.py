import os
import signal
from os.path import expanduser

from ioflo.base.consoling import Console
from plenum.cli.cli import Exit

from stp_core.common.log import Logger, getlogger
from indy_client.agent.run_agent import runBootstrap

from indy_client.test.agent.test_walleted_agent import TestWalletedAgent

from plenum.common.constants import NAME, VERSION

from anoncreds.protocol.types import ID
from indy_client.agent.exception import NonceNotFound
from indy_client.client.client import Client
from indy_client.client.wallet.wallet import Wallet
from indy_client.test.constants import primes
from indy_common.config import agentLoggingLevel
from indy_common.config_util import getConfig


class BaseAgent(TestWalletedAgent):
    def __init__(self,
                 name: str,
                 basedirpath: str,
                 client: Client = None,
                 wallet: Wallet = None,
                 port: int = None,
                 loop=None,
                 config=None,
                 endpointArgs=None):

        config = config or getConfig()
        basedirpath = basedirpath or os.path.expanduser(config.CLI_BASE_DIR)

        portParam, _ = self.getPassedArgs()

        self.logger = getlogger()

        super().__init__(name, basedirpath, client, wallet,
                         portParam or port, loop=loop, config=config,
                         endpointArgs=endpointArgs)

        self.claimVersionNumber = 0.01

        self._invites = {}

        self.updateClaimVersionFile(self.getClaimVersionFileName())

        signal.signal(signal.SIGTERM, self.exit_gracefully)

        self.setupLogging(self.getLoggerFilePath())

    def getLoggerFilePath(self, name=None):
        config = getConfig()
        path = expanduser('{}'.format(config.CLI_BASE_DIR))
        return '{}/{}.log'.format(path,
                                  (name or self.name).replace(" ",
                                                              "-").lower())

    def getClaimVersionFileName(self):
        return self.name.replace(" ", "-").lower() + "-schema-version.txt"

    def updateClaimVersionFile(self, fileName,):
        claimVersionFilePath = '{}/{}'.format(self.basedirpath, fileName)
        # get version number from file
        if os.path.isfile(claimVersionFilePath):
            try:
                with open(claimVersionFilePath, mode='r+') as file:
                    self.claimVersionNumber = float(file.read()) + 0.001
                    file.seek(0)
                    # increment version and update file
                    file.write(str(self.claimVersionNumber))
                    file.truncate()
            except OSError as e:
                self.logger.warning(
                    'Error occurred while reading version file: '
                    'error:{}'.format(e))
                raise e
            except ValueError as e:
                self.logger.warning('Invalid version number')
                raise e
        else:
            try:
                with open(claimVersionFilePath, mode='w') as file:
                    file.write(str(self.claimVersionNumber))
            except OSError as e:
                self.logger.warning('Error creating version file {}'.format(e))
                raise e

    def setupLogging(self, filePath):
        Logger().setLogLevel(agentLoggingLevel)
        Logger().enableFileLogging(filePath)

    def getInternalIdByInvitedNonce(self, nonce):
        if nonce in self._invites:
            return self._invites[nonce]
        else:
            raise NonceNotFound

    def getAvailableClaimList(self, link):
        assert link
        assert link.request_nonce
        assert link.remoteIdentifier
        return self.issuer.wallet.availableClaimsToAll + \
            self.issuer.wallet.availableClaimsByNonce.get(link.request_nonce, []) + \
            self.issuer.wallet.availableClaimsByIdentifier.get(
                link.remoteIdentifier, [])

    def isClaimAvailable(self, link, claimName):
        return claimName in [cl.get("name") for cl in
                             self.getAvailableClaimList(link)]

    def getSchemaKeysToBeGenerated(self):
        raise NotImplemented

    def getSchemaKeysForClaimsAvailableToAll(self):
        return self.getSchemaKeysToBeGenerated()

    def getSchemaKeysForClaimsAvailableToSpecificNonce(self):
        return {}

    def getAttrDefs(self):
        raise NotImplemented

    def getAttrs(self):
        raise NotImplemented

    async def postProofVerif(self, claimName, link, frm):
        pass

    async def initAvailableClaimList(self):
        async def getSchema(schemaKey):
            schema = await self.issuer.wallet.getSchema(ID(schemaKey))
            return {
                NAME: schema.name,
                VERSION: schema.version,
                "schemaSeqNo": schema.seqId
            }

        for schemaKey in self.getSchemaKeysForClaimsAvailableToAll():
            schema = await getSchema(schemaKey)
            self.issuer.wallet.availableClaimsToAll.append(schema)

        for nonce, schemaNames in self.getSchemaKeysForClaimsAvailableToSpecificNonce().items():
            for schemaName in schemaNames:
                schemaKeys = list(
                    filter(
                        lambda sk: sk.name == schemaName,
                        self.getSchemaKeysToBeGenerated()))
                assert len(schemaKeys) == 1, \
                    "no such schema name found in generated schema keys"
                schema = await getSchema(schemaKeys[0])
                oldAvailClaims = self.issuer.wallet.availableClaimsByNonce.get(nonce, [
                ])
                oldAvailClaims.append(schema)
                self.issuer.wallet.availableClaimsByNonce[nonce] = oldAvailClaims

    def _addAttribute(self, schemaKey, proverId, link):
        attr = self.getAttrs()[self.getInternalIdByInvitedNonce(proverId)]
        self.issuer._attrRepo.addAttributes(schemaKey=schemaKey,
                                            userId=proverId,
                                            attributes=attr)

    async def addSchemasToWallet(self):
        for schemaKey in self.getSchemaKeysToBeGenerated():
            matchedAttrDefs = list(filter(lambda ad: ad.name == schemaKey.name,
                                          self.getAttrDefs()))
            assert len(matchedAttrDefs) == 1, \
                "check if agent has attrib def and it's name is equivalent " \
                "to it's corresponding schema key name"
            attrDef = matchedAttrDefs[0]
            if not self.issuer.isSchemaExists(schemaKey):
                self.logger.info("schema not found in wallet, will go and "
                                 "get id from repo: {}".format(str(schemaKey)))
                schema = await self.issuer.genSchema(schemaKey.name,
                                                     schemaKey.version,
                                                     attrDef.attribNames())
                if schema:
                    schemaId = ID(schemaKey=schema.getKey(),
                                  schemaId=schema.seqId, seqId=schema.seqId)
                    p_prime, q_prime = primes["prime2"]
                    await self.issuer.genKeys(schemaId, p_prime=p_prime, q_prime=q_prime)
                    await self.issuer.issueAccumulator(schemaId=schemaId, iA='110', L=5)
            else:
                self.logger.info(
                    "schema is already loaded in wallet: {}".format(
                        str(schemaKey)))
        await self.initAvailableClaimList()

    async def bootstrap(self):
        await runBootstrap(self.addSchemasToWallet)

    def exit_gracefully(self, signum, frame):
        raise Exit("OS process terminated/stopped")
