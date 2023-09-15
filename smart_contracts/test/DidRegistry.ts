import { loadFixture } from '@nomicfoundation/hardhat-toolbox/network-helpers';
import { expect } from 'chai';
import { ethers } from 'hardhat';
import { DidRegistry } from '../typechain-types';
import { getBaseDidDocument, signDidDocument } from './utils';

describe('DIDContract', function () {
	// We define a fixture to reuse the same setup in every test.
	// We use loadFixture to run this setup once, snapshot that state,
	// and reset Hardhat Network to that snapshot in every test.
	async function deployDidContractixture() {
		// Contracts are deployed using the first signer/account by default
		const [owner, otherAccount] = await ethers.getSigners();

		const DidRegistry = await ethers.getContractFactory("DidRegistry");
		const didRegistry = await DidRegistry.deploy();

		ethers.deployContract("DidRegistry")

		return { didRegistry, owner, otherAccount };
	}

	describe('Create DID', function () {
		it('Should create DID document', async function () {
			const { didRegistry } = await loadFixture(deployDidContractixture);

			const did: string = 'did:indy2:testnet:SEp33q43PsdP7nDATyySSH'
			const didDocument = getBaseDidDocument(did)
			const signature = signDidDocument(didDocument);

			await didRegistry.createDid(didDocument, [signature])

			const didStorage = await didRegistry.dids(did)

			expect(didStorage.document.id).to.equals(didDocument.id);
			expect(didStorage.document.authentication[0].id).to.equals(didDocument.authentication[0].id);
			expect(didStorage.document.verificationMethod[0].id)
				.to.equals(didDocument.verificationMethod[0].id);
			expect(didStorage.document.verificationMethod[0].verificationMethodType)
				.to.equals(didDocument.verificationMethod[0].verificationMethodType);
			expect(didStorage.document.verificationMethod[0].controller)
				.to.equals(didDocument.verificationMethod[0].controller);
			expect(didStorage.document.verificationMethod[0].publicKeyMultibase)
				.to.equals(didDocument.verificationMethod[0].publicKeyMultibase);
		});

		it('Should fail if the DID being created already exists', async function () {
			const { didRegistry } = await loadFixture(deployDidContractixture);

			const did: string = 'did:indy2:testnet:SEp33q43PsdP7nDATyySSH'
			const didDocument = getBaseDidDocument(did)
			const signature = signDidDocument(didDocument);

			await didRegistry.createDid(didDocument, [signature])

			await expect(didRegistry.createDid(didDocument, [signature])).to.be.revertedWith('DID has already exist')
		});

		it('Should fail if provided did with incorrect schema', async function () {
			const { didRegistry } = await loadFixture(deployDidContractixture);

			const did: string = 'indy:indy2:testnet:SEp33q43PsdP7nDATyySSH'
			const didDocument = getBaseDidDocument(did)
			const signature = signDidDocument(didDocument);

			await expect(didRegistry.createDid(didDocument, [signature])).to.be.revertedWith('Incorrect DID schema')
		});

		it('Should fail if provided did with unsupported DID method', async function () {
			const { didRegistry } = await loadFixture(deployDidContractixture);

			const did: string = 'did:indy3:testnet:SEp33q43PsdP7nDATyySSH'
			const didDocument = getBaseDidDocument(did)
			const signature = signDidDocument(didDocument);

			await expect(didRegistry.createDid(didDocument, [signature])).to.be.revertedWith('Unsupported DID method')
		});
	});

	describe('Update DID', function () {
		it('Should update DID document', async function () {
			const { didRegistry } = await loadFixture(deployDidContractixture);

			const did: string = 'did:indy2:testnet:SEp33q43PsdP7nDATyySSH'
			let didDocument = getBaseDidDocument(did)
			let signature = signDidDocument(didDocument);

			await didRegistry.createDid(didDocument, [signature])
			
			const verificationMethod: DidRegistry.VerificationMethodStruct = {
				id: `${did}#KEY-2`,
				verificationMethodType: 'X25519KeyAgreementKey2019',
				controller: 'did:indy2:testnet:N22SEp33q43PsdP7nDATyySSH',
				publicKeyMultibase: 'FbQWLPRhTH95MCkQUeFYdiSoQt8zMwetqfWoxqPgaq7x',
				publicKeyJwk: '',
			}

			didDocument.verificationMethod.push(verificationMethod)
			signature = signDidDocument(didDocument);

			await didRegistry.updateDid(didDocument, [signature])

			const didStorage = await didRegistry.dids(did)

			expect(didStorage.document.verificationMethod.length).to.equals(2);
		});

		it('Should fail if the DID being updated does not exists', async function () {
			const { didRegistry } = await loadFixture(deployDidContractixture);

			const did: string = 'did:indy2:testnet:SEp33q43PsdP7nDATyySSH'
			let didDocument = getBaseDidDocument(did)
			let signature = signDidDocument(didDocument);

			await expect(didRegistry.updateDid(didDocument, [signature])).to.be.revertedWith('DID not found')
		});

		it('Should fail if the DID being updated is deactivated', async function () {
			const { didRegistry } = await loadFixture(deployDidContractixture);

			const did: string = 'did:indy2:testnet:SEp33q43PsdP7nDATyySSH'
			let didDocument = getBaseDidDocument(did)
			let signature = signDidDocument(didDocument);

			await didRegistry.createDid(didDocument, [signature])
			await didRegistry.deactivateDid(did, [signature])

			await expect(didRegistry.updateDid(didDocument, [signature])).to.be.revertedWith('DID has been deactivated')
		});


	});
});