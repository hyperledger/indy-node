import json
import pytest

from indy_client.agent.walleted_agent import WalletedAgent
from indy_client.test.agent.mock_backend_system import MockBackendSystem

import anoncreds.protocol.types
from indy_client.client.wallet.wallet import Wallet
from indy_client.test.constants import primes
from indy_common.identity import Identity
from indy_common.constants import TRUST_ANCHOR
from indy_node.pool.local_pool import create_local_pool

# noinspection PyUnresolvedReferences
from indy_node.test.conftest import tdir, nodeSet, tconf, \
    updatedPoolTxnData, updatedDomainTxnFile, txnPoolNodeSet, poolTxnData, \
    dirName, tdirWithDomainTxns, tdirWithPoolTxns, \
    domainTxnOrderedFields, genesisTxns, stewardWallet, poolTxnStewardData, \
    poolTxnStewardNames, trusteeWallet, trusteeData, poolTxnTrusteeNames, \
    patchPluginManager, txnPoolNodesLooper, tdirWithPoolTxns, \
    poolTxnNodeNames, allPluginsPath, tdirWithNodeKeepInited, testNodeClass, \
    genesisTxns

BANK_SEED = b'BANK0000000000000000000000000000'


class RefAgent(WalletedAgent):

    def create_connection_request(self, internal_id, name):

        nonce = str(self.verifier.generateNonce())
        # endpoint = self.endpoint.host_address()
        # TODO: this should be done by endpoint
        endpoint = "127.0.0.1" + ":" + str(self.endpoint.ha[1])

        msg = {'connection-request': {
            'name': self.name,
            'identifier': self._wallet.defaultId,
            'nonce': nonce,
            'endpoint': endpoint,
            'verkey': self._wallet.getVerkey(self.wallet.defaultId)
        },
            'sig': None
        }

        self._invites[nonce] = (internal_id, name)

        signature = self.wallet.signMsg(msg, self.wallet.defaultId)

        msg['sig'] = signature

        return json.dumps(msg)


@pytest.mark.skip("Broken logic of placing of nodes and clients.")
def test_end_to_end(tconf):
    base_dir = tconf.CLI_BASE_DIR

    print('*' * 20)
    print(base_dir)
    print('*' * 20)

    with create_local_pool(base_dir) as network:

        print(network.genesis_transactions)

        network.runFor(5)

        client = network.create_client(5555)

        bank_wallet = Wallet()
        bank_agent = RefAgent(name="bank",
                              basedirpath=base_dir,
                              client=client,
                              wallet=bank_wallet,
                              port=8787,
                              endpointArgs={'seed': BANK_SEED,
                                            'onlyListener': True})

        network.add(bank_agent)

        bank_id, bank_verkey = bank_agent.new_identifier(seed=BANK_SEED)

        print(bank_id)
        print(bank_verkey)

        s1_agent = network.steward_agent()

        s1_agent.publish_trust_anchor(Identity(identifier=bank_id,
                                               verkey=bank_verkey,
                                               role=TRUST_ANCHOR))
        network.runFor(5)

        # this allows calling asynchronous functions from a synchronous context
        run_async = network.run

        bank_attribute_definition = anoncreds.protocol.types.AttribDef(
            'basic', [
                anoncreds.protocol.types.AttribType(
                    'title', encode=True), anoncreds.protocol.types.AttribType(
                    'first_name', encode=True), anoncreds.protocol.types.AttribType(
                    'last_name', encode=True), anoncreds.protocol.types.AttribType(
                        'address_1', encode=True), anoncreds.protocol.types.AttribType(
                            'address_2', encode=True), anoncreds.protocol.types.AttribType(
                                'address_3', encode=True), anoncreds.protocol.types.AttribType(
                                    'postcode_zip', encode=True), anoncreds.protocol.types.AttribType(
                                        'date_of_birth', encode=True), anoncreds.protocol.types.AttribType(
                                            'account_type', encode=True), anoncreds.protocol.types.AttribType(
                                                'year_opened', encode=True), anoncreds.protocol.types.AttribType(
                                                    'account_status', encode=True)])

        bank_agent.add_attribute_definition(bank_attribute_definition)

        backend = MockBackendSystem(bank_attribute_definition)

        alices_id_in_banks_system = 1999891343
        bobs_id_in_banks_system = 2911891343

        backend.add_record(alices_id_in_banks_system,
                           title='Mrs.',
                           first_name='Alicia',
                           last_name='Garcia',
                           address_1='H-301',
                           address_2='Street 1',
                           address_3='UK',
                           postcode_zip='G61 3NR',
                           date_of_birth='December 28, 1990',
                           account_type='savings',
                           year_opened='2000',
                           account_status='active')
        backend.add_record(bobs_id_in_banks_system,
                           title='Mrs.',
                           first_name='Jay',
                           last_name='Raj',
                           address_1='222',
                           address_2='Baker Street',
                           address_3='UK',
                           postcode_zip='G61 3NR',
                           date_of_birth='January 15, 1980',
                           account_type='savings',
                           year_opened='1999',
                           account_status='active')

        bank_agent.set_issuer_backend(backend)

        schema_id = run_async(
            bank_agent.publish_schema('basic',
                                      schema_name='Bank Membership',
                                      schema_version='1.0'))

        # NOTE: do NOT use known primes in a non-test environment

        issuer_pub_key, revocation_pub_key = run_async(
            bank_agent.publish_issuer_keys(schema_id,
                                           p_prime=primes["prime1"][0],
                                           q_prime=primes["prime1"][1]))
        print(issuer_pub_key)
        print(revocation_pub_key)

        # TODO: Not implemented yet
        # accPK = run_async(bank_agent.publish_revocation_registry(
        #     schema_id=schema_id))

        # print(accPK)

        run_async(bank_agent._set_available_claim_by_internal_id(
            alices_id_in_banks_system, schema_id))
        run_async(bank_agent._set_available_claim_by_internal_id(
            bobs_id_in_banks_system, schema_id))

        alice_wallet = Wallet()
        alice_agent = RefAgent(name="Alice",
                               basedirpath=base_dir,
                               client=client,
                               wallet=alice_wallet,
                               port=8786)

        network.add(alice_agent)

        network.runFor(1)

        request = bank_agent.create_connection_request(
            alices_id_in_banks_system, "Alice")

        # Transfer of this request happens out-of-band (website, QR code, etc)

        alices_link_to_bank = alice_agent.load_request_str(request)

        # notice the link is not accepted
        print(alices_link_to_bank)

        alice_agent.accept_request(alices_link_to_bank)

        network.runFor(10)

        # notice that the link is accepted
        print(alices_link_to_bank)

        banks_link_to_alice = bank_agent.get_link_by_name(
            alices_id_in_banks_system)

        # note the available claims are now there
        print(banks_link_to_alice)

        claim_to_request = alices_link_to_bank.find_available_claim(
            name='Bank Membership')

        print(claim_to_request)

        run_async(alice_agent.send_claim(alices_link_to_bank,
                                         claim_to_request))
        network.runFor(5)

        claim = run_async(alice_agent.get_claim(schema_id))
        print(claim)

        # ########
        # # PROOF
        # ########
        # bank_agent._proofRequestsSchema['Address'] = {
        #     "name": "Address",
        #     "version": "0.2",
        #     "attributes": {
        #         "address_1": "string",
        #         "address_2": "string",
        #         "address_3": "string",
        #         "state": "string",
        #         "postcode_zip": "string",
        #     },
        #     "verifiableAttributes": ["postcode_zip"]
        # }
        #
        # bank_agent.sendProofReq(banks_link_to_alice, 'Address')
        #
        # network.runFor(3)
        # print()
