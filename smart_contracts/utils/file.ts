import fs from 'fs';

export function writeJson(data: Record<string, unknown>, outFile: string) {
    const content = JSON.stringify(data, null, '\t')
    fs.writeFileSync(outFile, content)
}
