import { environment } from '../../environment'
import { Contract } from '../../utils/contract'

export class ValidatorControl {
  private readonly name = 'ValidatorControl'
  private readonly address = '0x0000000000000000000000000000000000007777'
  private instance: any

  constructor(sender: any, address?: string) {
    this.instance = Contract.getInstance(sender, this.name, address || this.address)
  }

  async getValidators() {
    const validators = await this.instance.getValidators()
    console.log(`Validators: \n ${JSON.stringify(validators, null, 2)}`)
  }
}

async function demo() {
  const sender = environment.accounts.account1
  const contract = new ValidatorControl(sender)
  await contract.getValidators()
}

if (require.main === module) {
  demo()
}

module.exports = exports = demo
