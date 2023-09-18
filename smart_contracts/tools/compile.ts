import path from "path";
import { readFileSync, readdirSync, outputJsonSync } from "fs-extra";
const solc = require('solc');

const contractsPath = path.resolve(__dirname, '../', 'contracts');

function buildSources() {
  const sources: any = {};
  const contractsFiles = readdirSync(contractsPath);
  contractsFiles.forEach(file => {
    if(file.endsWith(".sol")){
      const contractFullPath = path.resolve(contractsPath, file);
      sources[file] = {
        content: readFileSync(contractFullPath, 'utf8')
      };
    }
  });
  return sources;
}

const input = {
	language: 'Solidity',
	sources: buildSources(),
	settings: {
		evmVersion: 'byzantium',
		optimizer: {
			enabled: true,
			runs: 200,
		},
		outputSelection: {
			'*': {
				'*': [ '*', 'evm.bytecode'  ]
			}
		}
	}
}

function compileContracts() {
  const stringifiedJson = JSON.stringify(input);
	console.log(stringifiedJson)
  const compilationResult = solc.lowlevel.compileStandard(stringifiedJson);
	console.log(compilationResult)
  const output = JSON.parse(compilationResult);
	console.log(output)
	const compiledContracts = output.contracts;
	for (let contract in compiledContracts) {
		for(let contractName in compiledContracts[contract]) {
			console.log(contract)
			outputJsonSync(
				path.resolve(contractsPath, `${contractName}.json`),
				compiledContracts[contract][contractName], { spaces: 2 }
			)
		}
	}
}

const main = () => {
	compileContracts();
}

if (require.main === module) {
  main();
}

module.exports = exports = main


