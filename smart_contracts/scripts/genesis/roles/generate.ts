import * as fs from 'fs'
import { sha3, padLeft } from 'web3-utils'

interface Config {
    accounts: Array<{ account: string, role: number }>,
    roleOwners: Map<string, string>
}

function main() {
    const data = fs.readFileSync("./roles/data.json", "utf-8");
    const config: Config = JSON.parse(data)

    const storage: any = {}

    // mappings for the account to role are stored in slot sha3(account | slot(0))
    let slot0 = "0000000000000000000000000000000000000000000000000000000000000000";
    for (let i = 0; i < config.accounts.length; i++) {
        let account = padLeft(config.accounts[i].account.substring(2), 64);
        let slot = sha3('0x' + account + slot0)!.substring(2).toLowerCase();
        storage[padLeft(slot, 64)] = padLeft(config.accounts[i].role.toString(16), 64);
    }

    // mappings for the account to role are stored in slot sha3(role | slot(1))
    let slot1 = "0000000000000000000000000000000000000000000000000000000000000001";
    for (let [role, owner] of Object.entries(config.roleOwners)) {
        let role_ = padLeft(parseInt(role).toString(16), 64);
        let slot = sha3('0x' + role_ + slot1)!.substring(2).toLowerCase();
        storage[padLeft(slot, 64)] = padLeft(parseInt(owner).toString(16), 64);
    }

    const section = {
        "<Address of Contract>": {
            comment: "Smart contract to manage account roles",
            balance: "0",
            code: "0x<Contract Code>",
            storage
        }
    }

    let content = JSON.stringify(section, null, "\t");
    fs.writeFileSync("RoleControl.json", content);
}

if (require.main === module) {
    main();
}
