import '@nomicfoundation/hardhat-toolbox';
import 'hardhat-storage-layout';
import { HardhatUserConfig } from 'hardhat/config';

const config: HardhatUserConfig = {
    solidity: {
        version: '0.8.20',
        settings: {
            optimizer: {
                enabled: false,
                runs: 200
            },
        },
    }
};

export default config;
