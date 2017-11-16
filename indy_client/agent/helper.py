import os

from plenum.common.signer_did import DidSigner
from plenum.common.util import friendlyToRaw, rawToFriendly
from indy_client.client.wallet.wallet import Wallet
from indy_common.config_util import getConfig

from stp_core.crypto.util import ed25519PkToCurve25519


def processInvAccept(wallet, msg):
    pass


def rawVerkeyToPubkey(raw_verkey):
    return ed25519PkToCurve25519(raw_verkey)


def friendlyVerkeyToPubkey(verkey):
    vkRaw = friendlyToRaw(verkey)
    pkraw = ed25519PkToCurve25519(vkRaw)
    return rawToFriendly(pkraw)


def getClaimVersionFileName(agentName):
    return agentName.replace(" ", "-").lower() + "-schema-version.txt"


def updateAndGetNextClaimVersionNumber(basedirpath, fileName):
    claimVersionFilePath = '{}/{}'.format(basedirpath, fileName)
    # get version number from file
    claimVersionNumber = 0.01
    if os.path.isfile(claimVersionFilePath):
        with open(claimVersionFilePath, mode='r+') as file:
            claimVersionNumber = float(file.read()) + 0.001
            file.seek(0)
            # increment version and update file
            file.write(str(claimVersionNumber))
            file.truncate()
    else:
        with open(claimVersionFilePath, mode='w') as file:
            file.write(str(claimVersionNumber))
    return claimVersionNumber


def build_wallet_core(wallet_name, seed_file):
    config = getConfig()
    baseDir = os.path.expanduser(config.CLI_BASE_DIR)

    seedFilePath = '{}/{}'.format(baseDir, seed_file)
    seed = wallet_name + '0' * (32 - len(wallet_name))

    # if seed file is available, read seed from it
    if os.path.isfile(seedFilePath):
        with open(seedFilePath, mode='r+') as file:
            seed = file.read().strip(' \t\n\r')
    wallet = Wallet(wallet_name)

    seed = bytes(seed, encoding='utf-8')
    wallet.addIdentifier(signer=DidSigner(seed=seed))

    return wallet


async def bootstrap_schema(agent, attrib_def_name, schema_name, schema_version, p_prime, q_prime):
    schema_id = await agent.publish_schema(attrib_def_name,
                                           schema_name=schema_name,
                                           schema_version=schema_version)

    _, _ = await agent.publish_issuer_keys(schema_id, p_prime=p_prime, q_prime=q_prime)

    # TODO not fully implemented yet!
    # await agent.publish_revocation_registry(schema_id=schema_id)

    return schema_id


def buildAgentWallet(name, seed):
    wallet = Wallet(name)
    wallet.addIdentifier(signer=DidSigner(seed=seed))
    return wallet
