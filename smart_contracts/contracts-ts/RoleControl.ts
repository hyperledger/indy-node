import { Account } from '../utils/account'
import { Contract } from '../utils/contract'

export enum ROLES {
  EMPTY,
  TRUSTEE,
  ENDORSER,
  STEWARD,
}

export class RoleControl extends Contract {
  public static readonly defaultAddress = '0x0000000000000000000000000000000000006666'

  constructor(sender?: Account) {
    super(RoleControl.name, sender)
  }

  public async getRole(account: string) {
    return this.instance.getRole(account)
  }

  public async hasRole(role: number, account: string) {
    return this.instance.hasRole(role, account)
  }

  public async assignRole(role: number, account: string) {
    const tx = await this.instance.assignRole(role, account)
    return tx.wait()
  }

  public async revokeRole(role: number, account: string) {
    const tx = await this.instance.revokeRole(role, account)
    return await tx.wait()
  }

  public async getRoleCount(role: number) {
    return this.instance.getRoleCount(role)
  }
}
