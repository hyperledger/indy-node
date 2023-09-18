import * as fs from 'fs'
import * as path from "path";

export const slots = {
    0: '0000000000000000000000000000000000000000000000000000000000000000',
    1: '0000000000000000000000000000000000000000000000000000000000000001',
    2: '0000000000000000000000000000000000000000000000000000000000000002',
}

export function buildSection(comment: string, storage: any) {
    return {
        '<Address of Contract>': {
            comment,
            balance: '0',
            code: '0x<Contract Code>',
            storage,
        },
    }
}

export function readConfig(file: string) {
    const data = fs.readFileSync(file, 'utf-8')
    return JSON.parse(data)
}

export function writeResult(data: Record<string, unknown>, outFile: string) {
    const content = JSON.stringify(data, null, '\t')
    fs.writeFileSync(outFile, content)
}
