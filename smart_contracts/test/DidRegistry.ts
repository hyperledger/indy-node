import { loadFixture } from '@nomicfoundation/hardhat-toolbox/network-helpers';
import { expect } from 'chai';
import { ethers } from 'hardhat';
import { DidRegistry } from '../typechain-types';

describe('DIDContract', function () {
	// We define a fixture to reuse the same setup in every test.
	// We use loadFixture to run this setup once, snapshot that state,
	// and reset Hardhat Network to that snapshot in every test.
	async function deployDidContractixture() {
		// Contracts are deployed using the first signer/account by default
		const [owner, otherAccount] = await ethers.getSigners();

		const DidRegistry = await ethers.getContractFactory('DidRegistry');
		const didRegistry = await DidRegistry.deploy();

		ethers.deployContract('DidRegistry')

		return { didRegistry, owner, otherAccount };
	}

	describe('Create DID', function () {
		it('Should create DID document', async function () {
			const { didRegistry } = await loadFixture(deployDidContractixture);

			const did: string = 'did:indy2:testnet:SEp33q43PsdP7nDATyySSH'

			const verificationMethod: DidRegistry.VerificationMethodStruct = {
				id: did,
				verificationMethodType: 'Ed25519VerificationKey2018',
				controller: 'did:indy2:testnet:N22SEp33q43PsdP7nDATyySSH',
				publicKeyMultibase: 'zAKJP3f7BD6W4iWEQ9jwndVTCBq8ua2Utt8EEjJ6Vxsf',
				publicKeyJwk: '',
			}

			const authentication: DidRegistry.VerificationRelationshipStruct = {
				id: did,
				verificationMethod: {
					id: '',
					verificationMethodType: '',
					controller: '',
					publicKeyMultibase: '',
					publicKeyJwk: '',
				}
			}

			const didDocument: DidRegistry.DidDocumentStruct = {
				context: [],
				id: did,
				controller: [],
				verificationMethod: [verificationMethod],
				authentication: [authentication],
				assertionMethod: [],
				capabilityInvocation: [],
				capabilityDelegation: [],
				keyAgreement: [],
				service: [],
				alsoKnownAs: [],
			}

			const signature: DidRegistry.SignatureStruct = { 
				id: did, 
				value: '4X3skpoEK2DRgZxQ9PwuEvCJpL8JHdQ8X4HDDFyztgqE15DM2ZnkvrAh9bQY16egVinZTzwHqznmnkaFM4jjyDgd' 
			}

			await didRegistry.createDid(didDocument, [signature])

			const savedDid = await didRegistry.dids(did)

			expect(savedDid.document.id).to.equals(didDocument.id);
			expect(savedDid.document.authentication[0].id).to.equals(didDocument.authentication[0].id);
			expect(savedDid.document.verificationMethod[0].id)
				.to.equals(didDocument.verificationMethod[0].id);
			expect(savedDid.document.verificationMethod[0].verificationMethodType)
				.to.equals(didDocument.verificationMethod[0].verificationMethodType);
			expect(savedDid.document.verificationMethod[0].controller)
				.to.equals(didDocument.verificationMethod[0].controller);
			expect(savedDid.document.verificationMethod[0].publicKeyMultibase)
				.to.equals(didDocument.verificationMethod[0].publicKeyMultibase);
		});

		it('Should fail if the DID being created already exists', async function () {
			const { didRegistry } = await loadFixture(deployDidContractixture);

			const did: string = 'did:indy2:testnet:SEp33q43PsdP7nDATyySSH'

			const verificationMethod: DidRegistry.VerificationMethodStruct = {
				id: did,
				verificationMethodType: 'Ed25519VerificationKey2018',
				controller: 'did:indy2:testnet:N22SEp33q43PsdP7nDATyySSH',
				publicKeyMultibase: 'zAKJP3f7BD6W4iWEQ9jwndVTCBq8ua2Utt8EEjJ6Vxsf',
				publicKeyJwk: '',
			}

			const authentication: DidRegistry.VerificationRelationshipStruct = {
				id: did,
				verificationMethod: {
					id: '',
					verificationMethodType: '',
					controller: '',
					publicKeyMultibase: '',
					publicKeyJwk: '',
				}
			}

			const didDocument: DidRegistry.DidDocumentStruct = {
				context: [],
				id: did,
				controller: [],
				verificationMethod: [verificationMethod],
				authentication: [authentication],
				assertionMethod: [],
				capabilityInvocation: [],
				capabilityDelegation: [],
				keyAgreement: [],
				service: [],
				alsoKnownAs: [],
			}

			const signature: DidRegistry.SignatureStruct = { 
				id: did, 
				value: '4X3skpoEK2DRgZxQ9PwuEvCJpL8JHdQ8X4HDDFyztgqE15DM2ZnkvrAh9bQY16egVinZTzwHqznmnkaFM4jjyDgd' 
			}

			var tx = await didRegistry.createDid(didDocument, [signature])
			await tx.wait()

			await expect(didRegistry.createDid(didDocument, [signature])).to.be.revertedWith('DID has already exist')
		});

		it('Should fail if provided did with incorrect schema', async function () {
			const { didRegistry } = await loadFixture(deployDidContractixture);

			const did: string = 'indy:indy2:testnet:SEp33q43PsdP7nDATyySSH'

			const verificationMethod: DidRegistry.VerificationMethodStruct = {
				id: did,
				verificationMethodType: 'Ed25519VerificationKey2018',
				controller: 'did:indy2:testnet:N22SEp33q43PsdP7nDATyySSH',
				publicKeyMultibase: 'zAKJP3f7BD6W4iWEQ9jwndVTCBq8ua2Utt8EEjJ6Vxsf',
				publicKeyJwk: '',
			}

			const authentication: DidRegistry.VerificationRelationshipStruct = {
				id: did,
				verificationMethod: {
					id: '',
					verificationMethodType: '',
					controller: '',
					publicKeyMultibase: '',
					publicKeyJwk: '',
				}
			}

			const didDocument: DidRegistry.DidDocumentStruct = {
				context: [],
				id: did,
				controller: [],
				verificationMethod: [verificationMethod],
				authentication: [authentication],
				assertionMethod: [],
				capabilityInvocation: [],
				capabilityDelegation: [],
				keyAgreement: [],
				service: [],
				alsoKnownAs: [],
			}

			const signature: DidRegistry.SignatureStruct = { 
				id: did, 
				value: '4X3skpoEK2DRgZxQ9PwuEvCJpL8JHdQ8X4HDDFyztgqE15DM2ZnkvrAh9bQY16egVinZTzwHqznmnkaFM4jjyDgd' 
			}

			await expect(didRegistry.createDid(didDocument, [signature])).to.be.revertedWith('Incorrect DID schema')
		});

		it('Should fail if provided did with unsupported DID method', async function () {
			const { didRegistry } = await loadFixture(deployDidContractixture);

			const did: string = 'did:indy3:testnet:SEp33q43PsdP7nDATyySSH'

			const verificationMethod: DidRegistry.VerificationMethodStruct = {
				id: did,
				verificationMethodType: 'Ed25519VerificationKey2018',
				controller: 'did:indy2:testnet:N22SEp33q43PsdP7nDATyySSH',
				publicKeyMultibase: 'zAKJP3f7BD6W4iWEQ9jwndVTCBq8ua2Utt8EEjJ6Vxsf',
				publicKeyJwk: '',
			}

			const authentication: DidRegistry.VerificationRelationshipStruct = {
				id: did,
				verificationMethod: {
					id: '',
					verificationMethodType: '',
					controller: '',
					publicKeyMultibase: '',
					publicKeyJwk: '',
				}
			}

			const didDocument: DidRegistry.DidDocumentStruct = {
				context: [],
				id: did,
				controller: [],
				verificationMethod: [verificationMethod],
				authentication: [authentication],
				assertionMethod: [],
				capabilityInvocation: [],
				capabilityDelegation: [],
				keyAgreement: [],
				service: [],
				alsoKnownAs: [],
			}

			const signature: DidRegistry.SignatureStruct = { 
				id: did, 
				value: '4X3skpoEK2DRgZxQ9PwuEvCJpL8JHdQ8X4HDDFyztgqE15DM2ZnkvrAh9bQY16egVinZTzwHqznmnkaFM4jjyDgd' 
			}

			await expect(didRegistry.createDid(didDocument, [signature])).to.be.revertedWith('Unsupported DID method')
		});
	});

	describe('Update DID', function () {
		
	});

	describe('Deactivate DID', function () {
	});
});