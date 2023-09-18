export const slots = {
  0: '0000000000000000000000000000000000000000000000000000000000000000',
  1: '0000000000000000000000000000000000000000000000000000000000000001',
  2: '0000000000000000000000000000000000000000000000000000000000000002',
}

export function buildSection(comment: string, storage: Record<string, string>) {
  return {
    '<Address of Contract>': {
      comment,
      balance: '0',
      code: '0x<Contract Code>',
      storage,
    },
  }
}
