import fs from "fs";

export function readJson(file: string) {
    const data = fs.readFileSync(file, 'utf-8')
    return JSON.parse(data)
}

export function writeJson(data: Record<string, unknown>, outFile: string) {
    const content = JSON.stringify(data, null, '\t')
    fs.writeFileSync(outFile, content)
}
