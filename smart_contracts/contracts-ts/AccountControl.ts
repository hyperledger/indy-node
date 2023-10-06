import { BigNumberish } from 'ethers'
import { Account } from '../utils/account'
import { Contract } from '../utils/contract'
import { BytesLike } from 'ethers/src.ts/utils'

export interface Transaction {
  sender: string,
	target: string,
	value: BigNumberish,
	gasPrice: BigNumberish,
	gasLimit: BigNumberish,
	bytes: BytesLike
}

export class AccountControl extends Contract {
	public static readonly defaultAddress = '0x0000000000000000000000000000000000008888'

	constructor(sender?: any) {
		super(AccountControl.name, sender)
	}

	public async transactionAllowed(transaction: Transaction) {
		return await this.instance.transactionAllowed(
			transaction.sender, 
			transaction.target,
			transaction.value, 
			transaction.gasPrice, 
			transaction.gasLimit, 
			transaction.bytes
		)
	}
}