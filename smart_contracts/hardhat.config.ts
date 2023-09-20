import '@nomicfoundation/hardhat-toolbox';
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
    },
    networks: {
        hardhat: {
            allowUnlimitedContractSize: true,
        }
    }
};

export default config;
