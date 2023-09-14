import { BN } from 'bn.js'
import * as fs from 'fs'
import { sha3, padLeft } from 'web3-utils'

interface Config {
    validators: Array<{ account: string, validator: string }>,
    roleControlContractAddress: string
}

function main() {
    const data = fs.readFileSync("./validators/data.json", "utf-8");
    const config: Config = JSON.parse(data)

    let records = [];

    for (let i = 0; i < config.validators.length; i++) {
        records[i] = {
            account: config.validators[i].account.trim(),
            validator: config.validators[i].validator.trim(),
            index: i
        };
    }

    const storage: any = {}

    // length of the validator array is stored in slot 0
    storage["0000000000000000000000000000000000000000000000000000000000000000"] = padLeft(config.validators.length, 64).substring(2);

    // validator array records are stored beginning at slot sha3(slot(0))
    let slot0 = sha3("0x0000000000000000000000000000000000000000000000000000000000000000")!.substring(2);
    for (let i = 0; i < records.length; i++) {
        let slot = new BN(slot0, 16).add(new BN(records[i].index)).toString(16);
        storage[padLeft(slot, 64)] = padLeft(records[i].validator.substring(2).toLowerCase(), 64);
    }

    // mappings for the validator infos are stored in slot sha3(validator | slot(1))
    let slot1 = "0000000000000000000000000000000000000000000000000000000000000001";
    for (let i = 0; i < records.length; i++) {
        let validator = padLeft(records[i].validator.substring(2), 64);
        let slot = sha3('0x' + validator + slot1)!.substring(2).toLowerCase();
        storage[padLeft(slot, 64)] = padLeft(records[i].account.substring(2).toLowerCase() + records[i].index.toString(16) + "01", 64); // account | index(hex) | activeValidator:true(0x01)
    }

    // address of role control contact stored in slot 2
    storage["0000000000000000000000000000000000000000000000000000000000000002"] = padLeft(config.roleControlContractAddress, 64);

    const section = {
        "<Address of Contract>": {
            comment: "Smart contract to manage validator nodes",
            balance: "0",
            code: "0x<Contract Code>",
            storage
        }
    }

    let content = JSON.stringify(section, null, "\t");
    fs.writeFileSync("ValidatorsControlGenesis.json", content);
}

if (require.main === module) {
    main();
}
