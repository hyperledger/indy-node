import { Contract } from '../utils/contract'

export class ValidatorControl extends Contract {
  protected static readonly defaultAddress = '0x0000000000000000000000000000000000007777'
  protected static readonly path = 'network'

  constructor(sender?: any, address?: string) {
    super(ValidatorControl.name, ValidatorControl.path, sender, address || ValidatorControl.defaultAddress)
  }

  async getValidators() {
    return this.instance.getValidators()
  }

  async addValidator(address: string) {
    const tx = await this.instance.addValidator(address)
    return tx.wait()
  }

  async removeValidator(address: string) {
    return this.instance.removeValidator(address)
  }
}
