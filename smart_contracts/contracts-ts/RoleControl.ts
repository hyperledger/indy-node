import { Contract } from '../utils/contract'

export enum ROLES {
  EMPTY,
  TRUSTEE,
  ENDORSER,
  STEWARD,
}

export class RoleControl extends Contract {
  protected static readonly defaultAddress = '0x0000000000000000000000000000000000006666'

  constructor(sender?: any, address?: string) {
    super(RoleControl.name, 'auth', sender, address || RoleControl.defaultAddress)
  }

  async getRole(account: string) {
    return this.instance.getRole(account)
  }

  async hasRole(role: number, account: string) {
    return this.instance.hasRole(role, account)
  }

  async assignRole(role: number, account: string) {
    const tx = await this.instance.assignRole(role, account)
    return tx.wait()
  }

  async revokeRole(role: number, account: string) {
    const tx = await this.instance.revokeRole(role, account)
    return await tx.wait()
  }
}
