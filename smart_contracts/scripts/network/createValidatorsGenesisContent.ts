import { BN } from 'bn.js'
import * as fs from 'fs'
import { sha3, padLeft } from 'web3-utils'

function main() {
    const data = fs.readFileSync("./initialValidators.json", "utf-8");
    const validators = JSON.parse(data)

    const storage: any = {}

    let validatorIndex = 0;
    let records = [];

    for (let i = 0; i < validators.length; i++) {
        records[i] = {
            account: validators[i].account.trim(),
            validator: validators[i].validator.trim(),
            validatorIndex
        };
        validatorIndex++;
    }

    // length of the validator array is stored in slot 0
    storage["0000000000000000000000000000000000000000000000000000000000000000"] = padLeft(validatorIndex, 64).substring(2);

    // validator array records are stored beginning at slot sha3(slot(0))
    let slot0 = sha3("0x0000000000000000000000000000000000000000000000000000000000000000")!.substring(2);
    for (let i = 0; i < records.length; i++) {
        let slot = new BN(slot0, 16).add(new BN(records[i].validatorIndex)).toString(16);
        storage[padLeft(slot, 64)] = padLeft(records[i].validator.substring(2).toLowerCase(), 64);
    }

    // mappings for the validator infos are stored in slot sha3(validator | slot(1))
    let slot1 = "0000000000000000000000000000000000000000000000000000000000000001";
    for (let i = 0; i < records.length; i++) {
        let validator = padLeft(records[i].validator.substring(2), 64);
        let slot = sha3('0x' + validator + slot1)!.substring(2).toLowerCase();
        storage[padLeft(slot, 64)] = padLeft(records[i].account.substring(2).toLowerCase() + records[i].validatorIndex.toString(16) + "01", 64); // account | validatorIndex(hex) | activeValidator:true(0x01)
    }

    const section = {
        "<Address of Contract>": {
            comment: "Smart contract to manage validator nodes",
            balance: "0",
            code: "0x<Contract Code>",
            storage
        }
    }

    let content = JSON.stringify(section, null, "\t");
    fs.writeFileSync("ValidatorsGenesis.json", content);
}

if (require.main === module) {
    main();
}
