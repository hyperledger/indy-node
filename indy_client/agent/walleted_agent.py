import errno
import os

from plenum.client.wallet import WalletStorageHelper
from plenum.common.util import normalizedWalletFileName, \
    getLastSavedWalletFileName, getWalletFilePath
from indy_client.agent.agent import Agent
from indy_client.agent.caching import Caching
from indy_client.agent.walleted import Walleted
from indy_client.anon_creds.indy_issuer import IndyIssuer
from indy_client.anon_creds.indy_prover import IndyProver
from indy_client.anon_creds.indy_verifier import IndyVerifier
from indy_client.client.client import Client
from indy_client.client.wallet.wallet import Wallet
from indy_common.config_util import getConfig

from anoncreds.protocol.repo.attributes_repo import AttributeRepoInMemory


class WalletedAgent(Walleted, Agent, Caching):
    def __init__(self,
                 name: str = None,
                 basedirpath: str = None,
                 client: Client = None,
                 wallet: Wallet = None,
                 port: int = None,
                 loop=None,
                 attrRepo=None,
                 config=None,
                 endpointArgs=None):

        Agent.__init__(self, name, basedirpath, client, port, loop=loop,
                       config=config, endpointArgs=endpointArgs)

        self.config = getConfig(basedirpath)

        self._wallet = None
        self._walletSaver = None

        # restore any active wallet belonging to this agent
        self._restoreWallet()

        # if no persisted wallet is restored and a wallet is passed,
        # then use given wallet, else ignore the given wallet
        if not self.wallet and wallet:
            self.wallet = wallet

        # if wallet is not yet set, then create a wallet
        if not self.wallet:
            self.wallet = Wallet(name)

        self._attrRepo = attrRepo or AttributeRepoInMemory()

        Walleted.__init__(self)

        if self.client:
            self._initIssuerProverVerifier()

        self._restoreIssuerWallet()

    def _initIssuerProverVerifier(self):
        self.issuer = IndyIssuer(client=self.client, wallet=self._wallet,
                                 attrRepo=self._attrRepo)
        self.prover = IndyProver(client=self.client, wallet=self._wallet)
        self.verifier = IndyVerifier(client=self.client, wallet=self._wallet)

    @property
    def wallet(self):
        return self._wallet

    @wallet.setter
    def wallet(self, newWallet):
        self._wallet = newWallet

    @property
    def walletSaver(self):
        if self._walletSaver is None:
            self._walletSaver = WalletStorageHelper(
                self.getWalletsBaseDir(),
                dmode=self.config.WALLET_DIR_MODE,
                fmode=self.config.WALLET_FILE_MODE)
        return self._walletSaver

    @Agent.client.setter
    def client(self, client):
        Agent.client.fset(self, client)
        if self.client:
            self._initIssuerProverVerifier()

    def start(self, loop):
        super().start(loop)

    def stop(self, *args, **kwargs):
        self._saveAllWallets()
        super().stop(*args, **kwargs)

    def getWalletsBaseDir(self):
        return os.path.expanduser(os.path.join(self.config.CLI_BASE_DIR, self.config.walletsDir))

    def getContextDir(self):
        return os.path.join(
            self.getWalletsBaseDir(),
            "agents", self.name.lower().replace(" ", "-"))

    def _getIssuerWalletContextDir(self):
        return os.path.join(self.getContextDir(), "issuer")

    def _saveAllWallets(self):
        self._saveWallet(self._wallet, self.getContextDir())
        self._saveIssuerWallet()
        # TODO: There are some other wallets for prover and verifier,
        # which we may also have to persist/restore as need arises

    def _saveIssuerWallet(self):
        if self.issuer:
            self.issuer.prepareForWalletPersistence()
            self._saveWallet(
                self.issuer.wallet,
                self._getIssuerWalletContextDir(),
                walletName="issuer")

    def _saveWallet(self, wallet: Wallet, contextDir, walletName=None):
        try:
            walletName = walletName or wallet.name
            fileName = normalizedWalletFileName(walletName)
            walletFilePath = self.walletSaver.saveWallet(
                wallet, getWalletFilePath(contextDir, fileName))
            self.logger.info('Active wallet "{}" saved ({})'.
                             format(walletName, walletFilePath))
        except IOError as ex:
            self.logger.info("Error occurred while saving wallet. " +
                             "error no.{}, error.{}"
                             .format(ex.errno, ex.strerror))

    def _restoreWallet(self):
        restoredWallet, walletFilePath = self._restoreLastActiveWallet(
            self.getContextDir())
        if restoredWallet:
            self.wallet = restoredWallet
            self.logger.info('Saved wallet "{}" restored ({})'.
                             format(self.wallet.name, walletFilePath))

    def _restoreIssuerWallet(self):
        if self.issuer:
            restoredWallet, walletFilePath = self._restoreLastActiveWallet(
                self._getIssuerWalletContextDir())
            if restoredWallet:
                self.issuer.restorePersistedWallet(restoredWallet)
                self.logger.info('Saved wallet "issuer" restored ({})'.
                                 format(walletFilePath))

    def _restoreLastActiveWallet(self, contextDir):
        walletFilePath = None
        try:
            walletFileName = getLastSavedWalletFileName(contextDir)
            walletFilePath = os.path.join(contextDir, walletFileName)
            wallet = self.walletSaver.loadWallet(walletFilePath)
            # TODO: What about current wallet if any?
            return wallet, walletFilePath
        except ValueError as e:
            if not str(e) == "max() arg is an empty sequence":
                self.logger.info("No wallet to restore")
        except (ValueError, AttributeError) as e:
            self.logger.info(
                "error occurred while restoring wallet {}: {}".
                format(walletFilePath, e))
        except IOError as exc:
            if exc.errno == errno.ENOENT:
                self.logger.debug("no such wallet file exists ({})".
                                  format(walletFilePath))
            else:
                raise exc
        return None, None
