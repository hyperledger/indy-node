import { writeJson } from "../../utils/file";
import { generate as credentialDefinitions } from "./credentialDefinitions/generate";
import { generate as dids } from "./dids/generate";
import { generate as roles } from "./roles/generate";
import { generate as schemas } from "./schemas/generate";
import { generate as validators } from "./validators/generate";

const outFile = 'ContractsGenesis.json'

function main() {
    const contracts = {
        ...credentialDefinitions(),
        ...dids(),
        ...roles(),
        ...schemas(),
        ...validators(),
    }
    writeJson(contracts, outFile)
}

if (require.main === module) {
    main()
}
