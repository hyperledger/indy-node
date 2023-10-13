# Proxy Smart Contracts

A proxy contract is a smart contract that forwards function calls to another contract, known as the implementation contract. The proxy contract holds the state, while the implementation contract contains the logic. When you want to upgrade the contract, you deploy a new implementation and update the proxy to point to this new address. This way, you can change the contract’s behavior without affecting its address. There are several common patterns of proxy implementation.

## Proxy Smart Contract Patterns

### Transparent proxy pattern (EIP-1538)
In the transparent proxy pattern used for upgrade smart contracts, the implementation of updates resides on the proxy side. The proxy utilizes its own memory to store both the state of the contract and the address of the current implementation. The proxy implemets a fallback function that uses `delegatecall` to invoke the appropriate function in the linked implementation. Usually, only the admin or owner of this contract has the authority to update the implementation. A notable challenge with this pattern is the potential for function clashes. This occurs when the 4-byte hash of a function signature in the implementation matches that of a function in the proxy, leading to unintentional behavior and potential vulnerabilities. One common solution to mitigate this problem is to ensure that only the contract administrator has the rights to call proxy-specific methods, while other accounts are restricted to calling methods from the implementation.

**Pros**: Relatively straidforward to implement
**Cons**: Deployment can be gas inefficent

## UUPS proxy pattern (EIP-1822)
The UUPS proxy pattern is similar to the transparent proxy pattern. However, a distinct difference lies in where the update logic is implemented. In the UUPS pattern, the update logic is placed within the implementation contract, allowing for the possibility to modify this logic or even remove it entirely in the future. This introduces potential risks. If a bug is present in a new implementation,  the contract update logic can be broken. While it's advisable to implement safeguards against unintentional breakdown of the update functionality, it's essential to note that these can't guard against intentional breakdowns.

**Pros**: Offers the options to update or eliminate upgrade logic.
**Cons**: Upgrade should be executed carefally as it can break upgrage logic.

## Beacon (EIP-1967)
Beacon proxy is a proxy pattern which is a separate contract that holds the logic address for one or more proxy contracts. In this setup, the proxy contract doesn’t store the address of the logic contract directly. Instead, it points to a beacon contract, which in turn points to the logic contract. This allows multiple proxy contracts to share a single logic contract through a common beacon, making it easier to manage upgrades for a group of proxy contracts.

**Pros**: Highly efficient for deploying contracts with similar logic and reduces costs by using one implementation and beacon proxy.
**Cons**: Complex to implement and maintain

## Diamond proxy pattern (EIP-2535)
Diamond proxy pattern introduces the concept of "Diamonds" which are a more modular approach to smart contract upgrades. A Diamond is a contract that delegates calls to multiple function implementations, known as “facets.” Facets can be added, replaced, or removed, allowing for more flexible and modular upgrades. This standard also includes a way to query which facets are currently active.

**Pros**: Helps in addressing smart contract size limitations and functionality can be upgraded incrementally.
**Cons**: Complex to implement and maintain