import Web3 from 'web3'

export const environment = {
  besu: {
    rpcnode: {
      name: 'rpcnode',
      url: 'http://127.0.0.1:8545',
      wsUrl: 'ws://127.0.0.1:8546',
      nodekey: '0e93a540518eeb673d94fb496b746008ab56605463cb9212493997f5755124d1',
      accountAddress: 'c9c913c8c3c1cd416d80a0abf475db2062f161f6',
      accountPrivateKey: '0x60bbe10a196a4e71451c0f6e9ec9beab454c2a5ac0542aa5b8b733ff5719fec3',
    },
    member1: {
      name: 'member1',
      url: 'http://127.0.0.1:20000',
      wsUrl: 'ws://127.0.0.1:20001',
      privateUrl: 'http://127.0.0.1:9081',
      nodekey: '0xb9a4bd1539c15bcc83fa9078fe89200b6e9e802ae992f13cd83c853f16e8bed4',
      accountAddress: '0xf0e2db6c8dc6c681bb5d6ad121a107f300e9b2b5',
      accountPrivateKey: '8bbbb1b345af56b560a5b20bd4b0ed1cd8cc9958a16262bc75118453cb546df7',
    },
    member2: {
      name: 'member2',
      url: 'http://127.0.0.1:20002',
      wsUrl: 'ws://127.0.0.1:20003',
      privateUrl: 'http://127.0.0.1:9082',
      nodekey: 'f18166704e19b895c1e2698ebc82b4e007e6d2933f4b31be23662dd0ec602570',
      accountAddress: '0xca843569e3427144cead5e4d5999a3d0ccf92b8e',
      accountPrivateKey: '4762e04d10832808a0aebdaa79c12de54afbe006bfffd228b3abcc494fe986f9',
    },
    member3: {
      name: 'member3',
      url: 'http://127.0.0.1:20004',
      wsUrl: 'ws://127.0.0.1:20005',
      privateUrl: 'http://127.0.0.1:9083',
      nodekey: '4107f0b6bf67a3bc679a15fe36f640415cf4da6a4820affaac89c8b280dfd1b3',
      accountAddress: '0x0fbdc686b912d7722dc86510934589e0aaf3b55a',
      accountPrivateKey: '61dced5af778942996880120b303fc11ee28cc8e5036d2fdff619b5675ded3f0',
    },
  },
  accounts: {
    account1: {
      address: '0xfe3b557e8fb62b89f4916b721be55ceb828dbd73',
      privateKey: '0x8f2a55949038a9610f50fb23b5883af3b4ecb3c3bb792cbcefbd1542c692be63',
    },
    account2: {
      address: '0x627306090abaB3A6e1400e9345bC60c78a8BEf57',
      privateKey: '0xc87509a1c067bbde78beb793e6fa76530b6382a4c0241e5e4a9ec0a0f44dc0d3',
    },
    account3: {
      address: '0xf17f52151EbEF6C7334FAD080c5704D77216b732',
      privateKey: '0xae6ae8e5ccbfb04590405997ee2d52d2b330726137b875053c36d94e974d162f',
    },
  },
  network: {
    name: 'testnet'
  },
  did: {
    method: 'indy2'
  }
}

export const host = environment.besu.rpcnode.url

export const web3 = new Web3(host)

export default environment
