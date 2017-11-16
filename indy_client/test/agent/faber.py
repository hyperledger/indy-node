import os
from anoncreds.protocol.exceptions import SchemaNotFoundError

from indy_common.config_util import getConfig
from plenum.common.signer_did import DidSigner
from indy_client.agent.helper import bootstrap_schema, buildAgentWallet
from indy_client.client.wallet.wallet import Wallet
from indy_client.test.client.TestClient import TestClient
from indy_client.test.constants import primes

from stp_core.common.log import getlogger
from indy_client.agent.runnable_agent import RunnableAgent
from indy_client.agent.agent import create_client
from indy_client.test.agent.mock_backend_system import MockBackendSystem

from anoncreds.protocol.types import AttribType, AttribDef, ID, SchemaKey
from indy_client.agent.walleted_agent import WalletedAgent

logger = getlogger()

FABER_SEED = b'Faber000000000000000000000000000'
FABER_SIGNER = DidSigner(seed=FABER_SEED)
FABER_ID = FABER_SIGNER.identifier
FABER_VERKEY = FABER_SIGNER.verkey


def create_faber(name=None, wallet=None, base_dir_path=None,
                 port=5555, client=None):

    if client is None:
        client = create_client(base_dir_path=base_dir_path, client_class=TestClient)

    endpoint_args = {'onlyListener': True}
    if wallet:
        endpoint_args['seed'] = wallet._signerById(wallet.defaultId).seed
    else:
        wallet = Wallet(name)
        wallet.addIdentifier(signer=FABER_SIGNER)
        endpoint_args['seed'] = FABER_SEED

    agent = WalletedAgent(name=name or "Faber College",
                          basedirpath=base_dir_path,
                          client=client,
                          wallet=wallet,
                          port=port,
                          endpointArgs=endpoint_args)

    agent._invites = {
        "b1134a647eb818069c089e7694f63e6d": (1, "Alice"),
        "2a2eb72eca8b404e8d412c5bf79f2640": (2, "Carol"),
        "7513d1397e87cada4214e2a650f603eb": (3, "Frank"),
        "710b78be79f29fc81335abaa4ee1c5e8": (4, "Bob")
    }

    transcript_def = AttribDef('Transcript',
                               [AttribType('student_name', encode=True),
                                AttribType('ssn', encode=True),
                                AttribType('degree', encode=True),
                                AttribType('year', encode=True),
                                AttribType('status', encode=True)])

    agent.add_attribute_definition(transcript_def)

    backend = MockBackendSystem(transcript_def)

    backend.add_record(1,
                       student_name="Alice Garcia",
                       ssn="123-45-6789",
                       degree="Bachelor of Science, Marketing",
                       year="2015",
                       status="graduated")

    backend.add_record(2,
                       student_name="Carol Atkinson",
                       ssn="783-41-2695",
                       degree="Bachelor of Science, Physics",
                       year="2012",
                       status="graduated")

    backend.add_record(3,
                       student_name="Frank Jeffrey",
                       ssn="996-54-1211",
                       degree="Bachelor of Arts, History",
                       year="2013",
                       status="dropped")

    backend.add_record(4,
                       student_name="Bob Richards",
                       ssn="151-44-5876",
                       degree="MBA, Finance",
                       year="2015",
                       status="graduated")

    agent.set_issuer_backend(backend)

    return agent


async def bootstrap_faber(agent):
    schema_id = ID(SchemaKey("Transcript", "1.2",
                             "FuN98eH2eZybECWkofW6A9BKJxxnTatBCopfUiNxo6ZB"))

    try:
        schema = await agent.issuer.wallet.getSchema(schema_id)
    except SchemaNotFoundError:
        schema_id = await bootstrap_schema(agent,
                                           'Transcript',
                                           'Transcript',
                                           '1.2',
                                           primes["prime1"][0],
                                           primes["prime1"][1])

    await agent._set_available_claim_by_internal_id(1, schema_id)
    await agent._set_available_claim_by_internal_id(2, schema_id)
    await agent._set_available_claim_by_internal_id(3, schema_id)
    await agent._set_available_claim_by_internal_id(4, schema_id)


if __name__ == "__main__":
    args = RunnableAgent.parser_cmd_args()
    name = "Faber College"
    port = args.port
    if port is None:
        port = 5555
    network = args.network or 'sandbox'
    with_cli = args.withcli

    config = getConfig()
    base_dir_path = os.path.expanduser(
        os.path.join(
            config.CLI_NETWORK_DIR, network
        ))

    agent = create_faber(name=name, wallet=buildAgentWallet(
        name, FABER_SEED), base_dir_path=base_dir_path, port=port)
    RunnableAgent.run_agent(
        agent, bootstrap=bootstrap_faber(agent), with_cli=with_cli)
