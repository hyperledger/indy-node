import pytest

from indy_client.test.training.getting_started_future import *

# noinspection PyUnresolvedReferences
from indy_node.test.conftest import tconf


def getting_started(base_dir=None):
    ####################################
    #  Setup
    ####################################

    if base_dir is None:
        base_dir = TemporaryDirectory().name

    demo_setup_logging(base_dir)

    pool = create_local_pool(base_dir)
    demo_start_agents(pool, pool, base_dir)
    # ###################################
    #  Alice's Wallet
    # ###################################

    alice_agent = WalletedAgent(name="Alice",
                                basedirpath=base_dir,
                                client=pool.create_client(5403),
                                wallet=Wallet(),
                                port=8786)
    alice_agent.new_identifier()

    pool.add(alice_agent)

    pool.runFor(1)

    ####################################
    #  Faber Invitation
    ####################################

    print(FABER_INVITE)

    link_to_faber = alice_agent.load_request_str(FABER_INVITE)

    print(link_to_faber)

    alice_agent.sync(link_to_faber.name)

    demo_wait_for_sync(pool, link_to_faber)

    print(link_to_faber)

    alice_agent.accept_request(link_to_faber)

    demo_wait_for_accept(pool, link_to_faber)

    print(link_to_faber)

    alice_agent.sendPing("Faber College")

    demo_wait_for_ping(pool)

    ####################################
    #  Transcription Claim
    ####################################

    demo_wait_for_claim_available(pool, link_to_faber, 'Transcript')
    claim_to_request = link_to_faber.find_available_claim(name='Transcript')

    print(claim_to_request)

    pool.run(alice_agent.send_claim(link_to_faber, claim_to_request))

    demo_wait_for_claim_attrs_received(pool, alice_agent, 'Transcript')

    claims = pool.run(alice_agent.prover.wallet.getAllClaimsAttributes())

    print(claims)

    ####################################
    #  Acme Invitation
    ####################################

    print(ACME_INVITE)
    link_to_acme = alice_agent.load_request_str(ACME_INVITE)

    print(link_to_acme)

    alice_agent.sync(link_to_acme.name)

    demo_wait_for_sync(pool, link_to_acme)

    print(link_to_acme)

    alice_agent.accept_request(link_to_acme)

    demo_wait_for_accept(pool, link_to_acme)

    print(link_to_acme)

    job_application_request = link_to_acme.find_proof_request(
        name='Job-Application')

    print(job_application_request)

    alice_agent.sendProof(link_to_acme, job_application_request)

    ####################################
    #  Job-Certificate Claim
    ####################################

    demo_wait_for_claim_available(pool, link_to_acme, 'Job-Certificate')

    print(link_to_acme)

    job_certificate = link_to_acme.find_available_claim(name='Job-Certificate')

    print(job_certificate)

    pool.run(alice_agent.send_claim(link_to_acme, job_certificate))

    demo_wait_for_claim_attrs_received(pool, alice_agent, 'Job-Certificate')

    claims = pool.run(alice_agent.prover.wallet.getAllClaimsAttributes())

    print(claims)

    ####################################
    #  Thrift Invitation
    ####################################

    link_to_thrift = alice_agent.load_request_str(THRIFT_INVITE)

    print(link_to_thrift)

    alice_agent.sync(link_to_thrift.name)

    demo_wait_for_sync(pool, link_to_thrift)

    print(link_to_thrift)

    alice_agent.accept_request(link_to_thrift)

    demo_wait_for_accept(pool, link_to_thrift)

    print(link_to_thrift)

    ####################################
    #  Proof to Thrift
    ####################################

    load_basic_request = link_to_thrift.find_proof_request(
        name='Loan-Application-Basic')

    print(load_basic_request)

    alice_agent.sendProof(link_to_thrift, load_basic_request)

    demo_wait_for_proof(pool, load_basic_request)

    #######

    load_kyc_request = link_to_thrift.find_proof_request(
        name='Loan-Application-KYC')

    print(load_kyc_request)

    alice_agent.sendProof(link_to_thrift, load_kyc_request)

    demo_wait_for_proof(pool, load_kyc_request)


if __name__ == "__main__":
    getting_started()
