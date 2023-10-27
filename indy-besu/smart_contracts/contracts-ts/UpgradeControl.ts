import { Contract } from '../utils/contract'

export class UpgradeControl extends Contract {
  public static readonly defaultAddress = '0x0000000000000000000000000000000000009999'

  constructor(sender?: any) {
    super(UpgradeControl.name, sender)
  }

  public async propose(proxy: string, implementation: string) {
    const tx = await this.instance.propose(proxy, implementation)
    return tx.wait()
  }

  public async approve(proxy: string, implementation: string) {
    const tx = await this.instance.approve(proxy, implementation)
    return tx.wait()
  }

  public async ensureSufficientApprovals(proxy: string, implementation: string): Promise<boolean> {
    return await this.instance.ensureSufficientApprovals(proxy, implementation)
  }
}
