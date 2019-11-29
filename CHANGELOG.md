# Hyperledger Indy Node Release Notes

* [1.12.0](#1120)

* [1.11.0](#1110)

* [1.10.0](#1100)

* [1.9.2](#192)

* [1.9.1](#191)

* [1.9.0](#190)

* [1.8.1](#181)

* [1.8.0](#180)

* [1.7.1](#171)

* [1.6.83](#1683)

* [1.6.82](#1682)

* [1.6.80](#1680)

* [1.6.79](#1679)

* [1.6.78](#1678)

* [1.6.73](#1673)

* [1.6.70](#1670)

* [1.5.68](#1568)

* [1.4.66](#1466)

* [1.3.62](#1362)

* [1.3.57](#1357)

* [1.3.55](#1355)

* [1.2.50](#1250)

* [1.1.43](#1143)

* [1.1.37](#1137)

* [1.0](#10)

#### Disclosure

Although every attempt has been made to make this information as accurate as possible, please know there may be things that are omitted, not fully developed yet, or updates since this publication that were not included in the information below. Only the most pressing or significant items have been listed. For the entire list of tickets and or specific information about any given item, please visit the list at [Hyperleder Indy's Jira](https://jira.hyperledger.org/). Once logged in, simply navigate to Projects > Indy.

## 1.12.0
### Release date: Nov 29th, 2019

### Component Version Information
| Components | Version Numbers |
| --- | --- |
| indy-plenum | 1.12.0 |
| indy-node | 1.12.0 |
| sovrin | 1.1.63 |

### Additional Information:

**There are possible OOM issues during 3+ hours of target load or large catch-ups at 8 GB RAM nodes pool so 32 GB is recommended.**

### Major Changes
- Improve primary selection algorithm
- Take into account transaction history when recovering state for new nodes
- Fix new nodes adding when there are old AUTH_RULE or plugin transactions

### Detailed Changelog

#### Major Fixes
| Description | Additional Information | Ticket Number |
| --- | --- | --- |
| The problem with a config state | | [INDY-2283](https://jira.hyperledger.org/browse/INDY-2283) |
| Node loses consensus and unreachable by clients | | [INDY-2287](https://jira.hyperledger.org/browse/INDY-2287) |
| A new added node failed to reach consensus | | [INDY-2254](https://jira.hyperledger.org/browse/INDY-2254) |

#### Changes and Additions
| Description | Additional Information | Ticket Number |
| --- | --- | --- |
| All nodes need to select the same primary during view change | | [INDY-2262](https://jira.hyperledger.org/browse/INDY-2262) |
| Take into account txn history when recovering state from the ledger for new nodes | | [INDY-2292](https://jira.hyperledger.org/browse/INDY-2292) |
| Do not restore Primaries from the audit ledger | | [INDY-2298](https://jira.hyperledger.org/browse/INDY-2298) |
| Start View change on receiving a quorum of ViewChange messages | | [INDY-2236](https://jira.hyperledger.org/browse/INDY-2236) |
| PBFT View change: cleanup and debug Part 3 | | [INDY-2267](https://jira.hyperledger.org/browse/INDY-2267) |
| A Node missing a View Change may not be able to finish it if NODE txns have been sent | | [INDY-2275](https://jira.hyperledger.org/browse/INDY-2275) |
| PrePrepare's Digest need to take into account all PrePrepare's fields | | [INDY-2285](https://jira.hyperledger.org/browse/INDY-2285) |
| Investigate reasons of hundreds VCs during 15 txns per sec production load | | [INDY-2295](https://jira.hyperledger.org/browse/INDY-2295) |
| Support historical req handlers for non-config ledgers | | [INDY-2307](https://jira.hyperledger.org/browse/INDY-2307) |

#### Known Issues
| Description | Additional Information | Ticket Number |
| --- | --- | --- |
| A node lagging behind may not be able to finish view change if nodes have been added/demoted | | [INDY-2308](https://jira.hyperledger.org/browse/INDY-2308) |
| GET_CRED_DEF for a Schema with a lot of attributes may fail with Timeout | | [INDY-2306](https://jira.hyperledger.org/browse/INDY-2306) |
| Only Trustee or Node owner can be the author of NODE demotion txn regardless of endorsement or auth constraint rules set | | [INDY-2024](https://jira.hyperledger.org/browse/INDY-2024) |

## 1.11.0
### Release date: Nov 1st, 2019

### Component Version Information
| Components | Version Numbers |
| --- | --- |
| indy-plenum | 1.11.0 |
| indy-node | 1.11.0 |
| sovrin | 1.1.60 |

### Additional Information:

**Please be careful with demoting/promoting/adding nodes (see Known Issues for details).**

**There are possible OOM issues during 3+ hours of target load or large catch-ups at 8 GB RAM nodes pool so 32 GB is recommended.**

### Major Changes
- Switch to PBFT View Change protocol
- Stability fixes

### Detailed Changelog

#### Major Fixes
| Description | Additional Information | Ticket Number |
| --- | --- | --- |
| One node doesn't catch up after promotion | | [INDY-2222](https://jira.hyperledger.org/browse/INDY-2222) |
| A Replica may process messages from other Replicas | | [INDY-2248](https://jira.hyperledger.org/browse/INDY-2248) |
| Up to F nodes are out of consensus after >3 hours of load | | [INDY-2268](https://jira.hyperledger.org/browse/INDY-2268) |
| A Node may not connect to another Node after restart | | [INDY-2274](https://jira.hyperledger.org/browse/INDY-2274) |
| Two View Changes happen during master or backup primary demotion | | [INDY-2247](https://jira.hyperledger.org/browse/INDY-2247) |

#### Changes and Additions
| Description | Additional Information | Ticket Number |
| --- | --- | --- |
| Debug: Integrate PBFT viewchanger service into current codebase | | [INDY-2140](https://jira.hyperledger.org/browse/INDY-2140) |
| Request missing ViewChange messages when receiving NewView | | [INDY-2178](https://jira.hyperledger.org/browse/INDY-2178) |
| Basic integration tests with a new View Change protocol need to pass | | [INDY-2223](https://jira.hyperledger.org/browse/INDY-2223) |
| Recover from a situation when View Change is finished on >= N-F of other nodes | | [INDY-2224](https://jira.hyperledger.org/browse/INDY-2224) |
| A Primary lagging behind a stable chedkpoints should not send NewView | | [INDY-2230](https://jira.hyperledger.org/browse/INDY-2230) |
| Do not stabilize checkpoint after the view change if a Replica doesn't have this checkpoint | | [INDY-2231](https://jira.hyperledger.org/browse/INDY-2231) |
| Save PrePrepare's BatchID in audit ledger and restore list of preprepares and prepares on node startup | | [INDY-2235](https://jira.hyperledger.org/browse/INDY-2235) |
| PBFT View Change Debug: Part 2 | | [INDY-2244](https://jira.hyperledger.org/browse/INDY-2244) |
| Optimize Propagate logic | | [INDY-2257](https://jira.hyperledger.org/browse/INDY-2257) |

#### Known Issues
| Description | Additional Information | Ticket Number |
| --- | --- | --- |
| All nodes need to select the same primary during view change | | [INDY-2262](https://jira.hyperledger.org/browse/INDY-2262) |
| A Node missing a View Change may not be able to finish it if NODE txns have been sent | | [INDY-2275](https://jira.hyperledger.org/browse/INDY-2275) |
| A new node joining the pool during the view change may not be able to start ordering immediately | | [INDY-2276](https://jira.hyperledger.org/browse/INDY-2276) |
Summary: If there are NODE txns for adding/removing nodes interleaved with View Changes (not any view changes, but a specific subset), then either up to F or all Nodes may not be able to finish view change. Please see the details and conditions when it may happen in INDY-2262.

## 1.10.0
### Release date: Oct 4th, 2019

### Component Version Information
| Components | Version Numbers |
| --- | --- |
| indy-plenum | 1.10.0 |
| indy-node | 1.10.0 |
| sovrin | 1.1.58 |

### Additional Information:
**There are possible OOM issues during 3+ hours of target load or large catch-ups at 8 GB RAM nodes pool so 32 GB is recommended.**
**PBFT View Change was implemented but not enabled so old View Change is active now.**

### Major Changes
- PBFT View Change implementation (not enabled yet) and corresponding code improvements 
- BLS multi-signature fixes and improvements
- The latest version of ZMQ library support
- Stability fixes

### Detailed Changelog

#### Major Fixes
| Description | Additional Information | Ticket Number |
| --- | --- | --- |
| GET_TXN doesn't work with old libindy | | [INDY-2233](https://jira.hyperledger.org/browse/INDY-2233) |
| Need to improve error message with invalid signature | | [INDY-2103](https://jira.hyperledger.org/browse/INDY-2103) |
| A node may not be able to connect to another node if another node was able to connect | | [INDY-2183](https://jira.hyperledger.org/browse/INDY-2183) |
| ZMQError: Address already in use when restarting client stack | | [INDY-2212](https://jira.hyperledger.org/browse/INDY-2212) |

#### Changes and Additions
| Description | Additional Information | Ticket Number |
| --- | --- | --- |
| All ledgers in a batch need to be BLS multi-signed | | [INDY-2228](https://jira.hyperledger.org/browse/INDY-2228) |
| Drop ppSeqNo on Backups after View Change | | [INDY-2226](https://jira.hyperledger.org/browse/INDY-2226) |
| Move 3PC Message Request logic into a separate service | | [INDY-2220](https://jira.hyperledger.org/browse/INDY-2220) |
| Bump pyzmq to the latest version | | [INDY-2213](https://jira.hyperledger.org/browse/INDY-2213) |
| Integration of Services: Cleanup | | [INDY-2208](https://jira.hyperledger.org/browse/INDY-2208) |
| Integrate Checkpointer Service into Replica | | [INDY-2179](https://jira.hyperledger.org/browse/INDY-2179) |
| Use audit ledger in Checkpoints | | [INDY-2177](https://jira.hyperledger.org/browse/INDY-2177) |
| Integrate OrderingService into Replica | | [INDY-2169](https://jira.hyperledger.org/browse/INDY-2169) |
| Integrate PrimarySelector into View Change Service | | [INDY-2167](https://jira.hyperledger.org/browse/INDY-2167) |
| Integrate view change property-based tests into CI | | [INDY-2150](https://jira.hyperledger.org/browse/INDY-2150) |
| Integrate and run PBFT View Changer simulation tests with a real implementation | | [INDY-2149](https://jira.hyperledger.org/browse/INDY-2149) |
| Implement PBFT viewchanger service with most basic functionality | | [INDY-2147](https://jira.hyperledger.org/browse/INDY-2147) |
| Extract and integrate ConsensusDataProvider from Replica | | [INDY-2139](https://jira.hyperledger.org/browse/INDY-2139) |
| Extract Checkpointer service from Replica | | [INDY-2137](https://jira.hyperledger.org/browse/INDY-2137) |
| Extract Orderer service from Replica | | [INDY-2136](https://jira.hyperledger.org/browse/INDY-2136) |
| Simulation tests for View Changer (no integration) | | [INDY-2135](https://jira.hyperledger.org/browse/INDY-2135) |
| Implementation: Make PBFT view change working | | [INDY-1340](https://jira.hyperledger.org/browse/INDY-1340) |
| Implement network, executor, orderer and checkpointer as adaptors for existing codebase | | [INDY-1339](https://jira.hyperledger.org/browse/INDY-1339) |
| Define Interfaces needed for View Change Service | | [INDY-1338](https://jira.hyperledger.org/browse/INDY-1338) |
| Modify WriteReqManager to meet Executor interface needs | | [INDY-1337](https://jira.hyperledger.org/browse/INDY-1337) |
| Stop resetting ppSeqNo (and relying on this) in new view | | [INDY-1336](https://jira.hyperledger.org/browse/INDY-1336) |
| Enable full ordering of batches from last view that have been already ordered, make execution on replicas that executed them no-op | | [INDY-1335](https://jira.hyperledger.org/browse/INDY-1335) |

#### Known Issues
| Description | Additional Information | Ticket Number |
| --- | --- | --- |
| One node doesn't catch up after promotion | | [INDY-2222](https://jira.hyperledger.org/browse/INDY-2222) |

## 1.9.2
### Release date: Aug 30th, 2019

### Component Version Information
| Components | Version Numbers |
| --- | --- |
| indy-plenum | 1.9.2 |
| indy-node | 1.9.2 |
| sovrin | 1.1.56 |

### Additional Information:
**Migration script will be applied for buildernet only and will return error message in python shell for any other pools (if manual migration will be performed).**
**There are possible OOM issues during 3+ hours of target load or large catch-ups at 8 GB RAM nodes pool so 32 GB is recommended.**

### Major Changes
- Stability fixes
- Endorser support fixes and improvements
- Improving GET_TXN to be able to query just one node the same way as for other GET requests

### Detailed Changelog

#### Major Fixes
| Description | Additional Information | Ticket Number |
| --- | --- | --- |
| New nodes added after last upgrade (1.9.1) are not in consensus | | [INDY-2211](https://jira.hyperledger.org/browse/INDY-2211) |
| indy-node broken by indy-plenum and python-dateutil | | [INDY-2176](https://jira.hyperledger.org/browse/INDY-2176) |
| Issue with non utf-8 decoding | | [INDY-2218](https://jira.hyperledger.org/browse/INDY-2218) |
| Endorsers must be specified within the transaction | | [INDY-2199](https://jira.hyperledger.org/browse/INDY-2199) |
| One node doesn't catch up | | [INDY-2215](https://jira.hyperledger.org/browse/INDY-2215) |

#### Changes and Additions
| Description | Additional Information | Ticket Number |
| --- | --- | --- |
| As a user, I need to be able to know what was the last update time of the ledger when querying a txn via GET_TXN request | | [INDY-1954](https://jira.hyperledger.org/browse/INDY-1954) |
| Endorser field can contian a DID with a known role only | | [INDY-2198](https://jira.hyperledger.org/browse/INDY-2198) |

## 1.9.1
### Release date: Aug 02nd, 2019

### Component Version Information
| Components | Version Numbers |
| --- | --- |
| indy-plenum | 1.9.1 |
| indy-node | 1.9.1 |
| sovrin | 1.1.52 |

### Additional Information:
**There are possible OOM issues during 3+ hours of target load or large catch-ups at 8 GB RAM nodes pool so 32 GB is recommended.**

### Major Changes
- New DIDs can be created without endorsers
- Transaction authors don't need to be endorsers
- TAA acceptance should use date, not time
- Bug fixes

### Detailed Changelog

#### Major Fixes
| Description | Additional Information | Ticket Number |
| --- | --- | --- |
| Incorrect request validation | | [INDY-2164](https://jira.hyperledger.org/browse/INDY-2164) |
| Need to make "reask_ledger_status" repeatable | | [INDY-2112](https://jira.hyperledger.org/browse/INDY-2112) |
| When view change takes too long instance change should be sent periodically | | [INDY-2143](https://jira.hyperledger.org/browse/INDY-2143) |

#### Changes and Additions
| Description | Additional Information | Ticket Number |
| --- | --- | --- |
| New DIDs can be created without endorsers | | [INDY-2171](https://jira.hyperledger.org/browse/INDY-2171) |
| Transaction authors don't need to be endorsers | | [INDY-2173](https://jira.hyperledger.org/browse/INDY-2173) |
| Grab pool data for failed system tests | | [INDY-2141](https://jira.hyperledger.org/browse/INDY-2141) |
| Memory profiling needs to be removed from GET_VALIDATOR_INFO output | | [INDY-2182](https://jira.hyperledger.org/browse/INDY-2182) |
| Implement PBFT viewchanger service with most basic functionality | | [INDY-2147](https://jira.hyperledger.org/browse/INDY-2147) |
| Extract Orderer service from Replica | | [INDY-2136](https://jira.hyperledger.org/browse/INDY-2136) |
| Extract and integrate ConsensusDataProvider from Replica | | [INDY-2139](https://jira.hyperledger.org/browse/INDY-2139) |
| TAA acceptance should use date, not time | | [INDY-2157](https://jira.hyperledger.org/browse/INDY-2157) |
| Clean-up Pluggable Request Handlers | | [INDY-2154](https://jira.hyperledger.org/browse/INDY-2154) |

## 1.9.0
### Release date: July 04th, 2019

### Component Version Information
| Components | Version Numbers |
| --- | --- |
| indy-plenum | 1.9.0 |
| indy-node | 1.9.0 |
| sovrin | 1.1.50 |

### Additional Information:
**There are possible OOM issues during 3+ hours of target load or large catch-ups at 8 GB RAM nodes pool so 32 GB is recommended.**
**Some nodes can fail to send a REJECT or REPLY to client under specific network conditions. See Know Issues for more details.**

### Major Changes
- Pluggable Request Handlers have been implemented 

### Detailed Changelog

#### Major Fixes
| Description | Additional Information | Ticket Number |
| --- | --- | --- |
| Propagates with invalid requests can lead to node crashes | | [INDY-2144](https://jira.hyperledger.org/browse/INDY-2144)  |
| There is no validation of the ISSUANCE_TYPE field for the transaction REVOC_REG_DEF | | [INDY-2142](https://jira.hyperledger.org/browse/INDY-2142) |
| Reduce CONS_PROOF timeout to speed up catchup under the load | | [INDY-2083](https://jira.hyperledger.org/browse/INDY-2083) |

#### Changes and Additions
| Description | Additional Information | Ticket Number |
| --- | --- | --- |
| As a Trustee(s), I need to have a way to set multiple AUTH_RULES by one command | | [INDY-2087](https://jira.hyperledger.org/browse/INDY-2087) |
| Make more system tests to be ready for Indy Node CD pipeline | | [INDY-2127](https://jira.hyperledger.org/browse/INDY-2127) |
| Integrate new handlers into the codebase | | [INDY-1861](https://jira.hyperledger.org/browse/INDY-1861) |
| Define Interfaces needed for View Change Service | | [INDY-1338](https://jira.hyperledger.org/browse/INDY-1338) |
| Rename TRUST_ANCHOR to ENDORSER | | [INDY-1950](https://jira.hyperledger.org/browse/INDY-1950) |
| Update PBFT view change plan of attack | | [INDY-2134](https://jira.hyperledger.org/browse/INDY-2134) |
| Apply a new Docker-in-docker approach for system tests | | [INDY-2131](https://jira.hyperledger.org/browse/INDY-2131) |
| More tests for pluggable request handlers | | [INDY-2108](https://jira.hyperledger.org/browse/INDY-2108) |
| Remove ANYONE_CAN_WRITE | | [INDY-1956](https://jira.hyperledger.org/browse/INDY-1956) |
| [Design] ViewChange protocol must be as defined in PBFT | | [INDY-1290](https://jira.hyperledger.org/browse/INDY-1290) |
| Batch containing some already executed requests should be applied correctly | | [INDY-1405](https://jira.hyperledger.org/browse/INDY-1405) |
| Update Pluggable Req Handlers | | [INDY-2097](https://jira.hyperledger.org/browse/INDY-2097) |
| As a Network Admin, I need to be able to forbid an action in AUTH_RULE, so that no changes in code are needed | | [INDY-2077](https://jira.hyperledger.org/browse/INDY-2077) |
| Create Builders for handlers | | [INDY-1860](https://jira.hyperledger.org/browse/INDY-1860) |

#### Known Issues
| Description | Additional Information | Ticket Number |
| --- | --- | --- |
| Incorrect request validation || [INDY-2164](https://jira.hyperledger.org/browse/INDY-2164) |

## 1.8.1
### Release date: June 06th, 2019

### Component Version Information
| Components | Version Numbers |
| --- | --- |
| indy-plenum | 1.8.1 |
| indy-node | 1.8.1 |
| sovrin | 1.1.46 |


### Major Fixes
| Description | Additional Information | Ticket Number |
| --- | --- | --- |
| All BuilderNet nodes are restarting every 30-50 seconds | |[INDY-2128](https://jira.hyperledger.org/browse/INDY-2128) |
| Primaries are not updated in audit ledger if one of the primaries is demoted | |[INDY-2129](https://jira.hyperledger.org/browse/INDY-2129) |
| A client may receive NACK for a payment transfer request, but the transaction will be eventually ordered (payment transferred) | |[INDY-2122](https://jira.hyperledger.org/browse/INDY-2122) |

## 1.8.0 
### Release date: May 31th, 2019

### Component Version Information
| Components | Version Numbers |
| --- | --- |
| indy-plenum | 1.8.0 |
| indy-node | 1.8.0 |
| sovrin | 1.1.45 |

### Additional Information:
**Payment transaction can return NACK from the pool but in fact it will be eventually ordered (see more details below).**
**There are possible OOM issues during 3+ hours of target load or large catch-ups at 8 GB RAM nodes pool so 32 GB is recommended.**
**Pool upgrade to sovrin 1.1.32 and above should be performed simultaneously for all nodes due to txn format changes.**
**Pool upgrade to indy-node 1.8.0 should be performed simultaneously for all nodes due to audit ledger.**

### Major Changes
- Add Transaction Author Agreement Acceptance Mechanisms and Transaction Author Agreement support
- Configurable Auth rules improvements
- Stability fixes

### Detailed Changelog

#### Major Fixes
| Description | Additional Information | Ticket Number |
| --- | --- | --- |
| Issues with catch up and ordering under the load |  | [INDY-2064](https://jira.hyperledger.org/browse/INDY-2064) |
| Editing of CLAIM_DEF uses auth rules for Adding a Claim Def |  | [INDY-2078](https://jira.hyperledger.org/browse/INDY-2078) |
| Faulty primary can order and write already ordered and written request |  | [INDY-1709](https://jira.hyperledger.org/browse/INDY-1709) |

#### Changes and Additions
| Description | Additional Information | Ticket Number |
| --- | --- | --- |
| As a Network Admin, I would like to use GET_AUTH_RULE output as an input for AUTH_RULE |  | [INDY-2102](https://jira.hyperledger.org/browse/INDY-2102) |
| Get Transaction Author Agreement Acceptance Mechanisms from the Config Ledger |  | [INDY-2071](https://jira.hyperledger.org/browse/INDY-2071) |
| Support Transaction Author Agreement in Write Requests |  | [INDY-2072](https://jira.hyperledger.org/browse/INDY-2072) |
| Validate transaction author agreement as part of consensus |  | [INDY-2073](https://jira.hyperledger.org/browse/INDY-2073) |
| Write Transaction Author Agreement to Config Ledger |  | [INDY-2066](https://jira.hyperledger.org/browse/INDY-2066) |
| Get Transaction Author Agreement from the config ledger |  | [INDY-2067](https://jira.hyperledger.org/browse/INDY-2067) |
| Write Transaction Author Agreement Acceptance Mechanisms to the Config Ledger |  | [INDY-2068](https://jira.hyperledger.org/browse/INDY-2068) |
| Catch-up should take into account state of other nodes when sending requests |  | [INDY-2053](https://jira.hyperledger.org/browse/INDY-2053) |

#### Known Issues
| Description | Additional Information | Ticket Number |
| --- | --- | --- |
| A client may receive NACK for a payment transfer request, but the transaction will be eventually ordered (payment transferred) |  | [INDY-2122](https://jira.hyperledger.org/browse/INDY-2122) |
| Incorrect auth constraint for node demotion |  | [INDY-2024](https://jira.hyperledger.org/browse/INDY-2024) |

## 1.7.1 
### Release date: Apr 30th, 2019

### Component Version Information
| Components | Version Numbers |
| --- | --- |
| indy-plenum | 1.7.1 |
| indy-node | 1.7.1 |
| sovrin | 1.1.41 |

### Additional Information:
**There are possible OOM issues during 3+ hours of target load or large catch-ups at 8 GB RAM nodes pool so 32 GB is recommended.**
**Pool upgrade to sovrin 1.1.32 and above should be performed simultaneously for all nodes due to txn format changes.**
**Pool upgrade to indy-node 1.7.1 should be performed simultaneously for all nodes due to audit ledger.**

### Major Changes
- Audit Ledger
  - helps keeping all other ledgers in sync
  - helps recovering of pool state by new or restarted nodes
  - can be used for external audit
- Correct support of multi-signatures
- Configurable Auth Rules in config state
- Stability fixes

### Detailed Changelog

#### Major Fixes
| Description | Additional Information | Ticket Number |
| --- | --- | --- |
| Validator-info doesn't show view change information and sometimes shows node info as unknown |  | [INDY-2008](https://jira.hyperledger.org/browse/INDY-2008) |
| Schema can't be written with error "'Version' object has no attribute 'dev'" |  | [INDY-2020](https://jira.hyperledger.org/browse/INDY-2020) |
| Node fails to start after the load |  | [INDY-2018](https://jira.hyperledger.org/browse/INDY-2018) |
| POA: Sovrin TestNet lost consensus |  | [INDY-2022](https://jira.hyperledger.org/browse/INDY-2022) |
| Nodes can fail on first start after upgrading from version without audit ledger to version with audit ledger |  | [INDY-2047](https://jira.hyperledger.org/browse/INDY-2047) |
| Pool is getting out of consensus after a forced view change and writes to all the ledgers |  | [INDY-2035](https://jira.hyperledger.org/browse/INDY-2035) |
| View Change processing - replica ends up with incorrect primaries |  | [INDY-1720](https://jira.hyperledger.org/browse/INDY-1720) |
| Validator node shows False for consensus |  | [INDY-2031](https://jira.hyperledger.org/browse/INDY-2031) |
| Watermarks may not be updated correctly after view change by a lagging node |  | [INDY-2060](https://jira.hyperledger.org/browse/INDY-2060) |
| ATTRIB doesn't have auth rules in auth map |  | [INDY-2061](https://jira.hyperledger.org/browse/INDY-2061) |
| Some nodes are stalled and throw an error under load |  | [INDY-2050](https://jira.hyperledger.org/browse/INDY-2050) |
| Some nodes failed to join consensus after upgrade |  | [INDY-2055](https://jira.hyperledger.org/browse/INDY-2055) |

#### Changes and Additions
| Description | Additional Information | Ticket Number |
| --- | --- | --- |
| Implementation: Restore current 3PC state from audit ledger |  | [INDY-1946](https://jira.hyperledger.org/browse/INDY-1946) |
| Implementation (not active): As a user/steward I want to have better understanding of release version and changelog |  | [INDY-1992](https://jira.hyperledger.org/browse/INDY-1992) |
| Implement auth rule maps in config ledger |  | [INDY-2001](https://jira.hyperledger.org/browse/INDY-2001) |
| Add audit ledger |  | [INDY-1944](https://jira.hyperledger.org/browse/INDY-1944) |
| INSTANCE_CHANGE messages should be persisted between restarts |  | [INDY-1984](https://jira.hyperledger.org/browse/INDY-1984) |
| Add updateState method for ConfigReqHandler |  | [INDY-2006](https://jira.hyperledger.org/browse/INDY-2006) |
| Use auth constraints from config ledger for validation |  | [INDY-2002](https://jira.hyperledger.org/browse/INDY-2002) |
| Implementation: Improve catch-up to use audit ledger for consistency |  | [INDY-1945](https://jira.hyperledger.org/browse/INDY-1945) |
| Implement a command to set auth constraints |  | [INDY-2003](https://jira.hyperledger.org/browse/INDY-2003) |
| Debug and validation: Move the auth_map structure to the config ledger |  | [INDY-1995](https://jira.hyperledger.org/browse/INDY-1995) |
| Need to enhance write permissions for Revocation transactions |  | [INDY-1554](https://jira.hyperledger.org/browse/INDY-1554) |
| Implement a command to get auth constraint |  | [INDY-2010](https://jira.hyperledger.org/browse/INDY-2010) |
| Integrate testinfra-based system tests to Indy CD |  | [INDY-2016](https://jira.hyperledger.org/browse/INDY-2016) |
| Debug and Validation: As a user/steward I want to have better understanding of release version and changelog |  | [INDY-2019](https://jira.hyperledger.org/browse/INDY-2019) |
| As a QA I want system tests to be run in parallel in CD pipeline |  | [INDY-2028](https://jira.hyperledger.org/browse/INDY-2028) |
| Debug and Validation: Audit Ledger and improving catch-up to use audit ledger for consistency |  | [INDY-1993](https://jira.hyperledger.org/browse/INDY-1993) |
| Need to track same transactions with different multi-signatures |  | [INDY-1757](https://jira.hyperledger.org/browse/INDY-1757) |
| Debug and Validation: Restore current 3PC state from audit ledger - Phase 1 |  | [INDY-2025](https://jira.hyperledger.org/browse/INDY-2025) |
| A Node need to be able to order stashed requests after long catch-ups |  | [INDY-1983](https://jira.hyperledger.org/browse/INDY-1983) |
| Need to account fields from PLUGIN_CLIENT_REQUEST_FIELDS when calculating digest |  | [INDY-1674](https://jira.hyperledger.org/browse/INDY-1674) |
| Debug and validation: Multi-signature support |  | [INDY-2046](https://jira.hyperledger.org/browse/INDY-2046) |
| Debug and Validation: Restore current 3PC state from audit ledger - Phase 2 |  | [INDY-2051](https://jira.hyperledger.org/browse/INDY-2051) |

## 1.6.83 
### Release date: Feb 11th, 2019

### Component Version Information
| Components | Version Numbers |
| --- | --- |
| indy-plenum | 1.6.58 |
| indy-node | 1.6.83 |

### Additional Information:
**There are possible OOM issues during 3+ hours of target load or large catch-ups at 8 GB RAM nodes pool so 32 GB is recommended.**
**Pool upgrade to sovrin 1.1.32 and above should be performed simultaneously for all nodes due to txn format changes.**

### Major Fixes
| Description | Additional Information | Ticket Number |
| --- | --- | --- |
| Validator-info to client times out if there are many upgrade attempts by node |  | [INDY-1922](https://jira.hyperledger.org/browse/INDY-1922) |
| Node on Sovrin TestNet did not upgrade automatically |  | [INDY-1919](https://jira.hyperledger.org/browse/INDY-1919) |
| Node that does not upgrade spams the config ledger |  | [INDY-1918](https://jira.hyperledger.org/browse/INDY-1918) |
| Incorrect pool upgrade txn validation |  | [INDY-1953](https://jira.hyperledger.org/browse/INDY-1953) |
| Upgrade appears to have broken "validator-info --nagios" |  | [INDY-1920](https://jira.hyperledger.org/browse/INDY-1920) |
| Node can't order after view change and catch up |  | [INDY-1955](https://jira.hyperledger.org/browse/INDY-1955) |
| Unclear error messages when Trustee send a NYM with the same verkey |  | [INDY-1963](https://jira.hyperledger.org/browse/INDY-1963) |
| A role that has been removed can't be added back |  | [INDY-1971](https://jira.hyperledger.org/browse/INDY-1971) |

### Changes and Additions
| Description | Additional Information | Ticket Number |
| --- | --- | --- |
| Limit the number of attributes in schema |  | [INDY-1914](https://jira.hyperledger.org/browse/INDY-1914) |
| Enable Clear Request Queue strategy |  | [INDY-1836](https://jira.hyperledger.org/browse/INDY-1836) |
| A Node needs to be able to order requests received during catch-up |  | [INDY-1876](https://jira.hyperledger.org/browse/INDY-1876) |
| Network maintenance role |  | [INDY-1916](https://jira.hyperledger.org/browse/INDY-1916) |
| There should always be fresh enough signature of a state |  | [INDY-933](https://jira.hyperledger.org/browse/INDY-933) |
| Node stops working without any services failure |  | [INDY-1949](https://jira.hyperledger.org/browse/INDY-1949) |
| As a user of Valdiator Info script, I need to know whether the pool has write consensus and when the state was updated the last time |  | [INDY-1928](https://jira.hyperledger.org/browse/INDY-1928) |
| Endorser permission not needed for ledger writes |  | [INDY-1528](https://jira.hyperledger.org/browse/INDY-1528) |

## 1.6.82 
### Release date: Dec 24th, 2018

### Component Version Information
| Components | Version Numbers |
| --- | --- |
| indy-plenum | 1.6.57 |
| indy-node | 1.6.82 |

### Additional Information:
**There are possible OOM issues during 3+ hours of target load or large catch-ups at 8 GB RAM nodes pool so 32 GB is recommended.**

### Changes - Additions
| Description | Additional Information | Ticket Number |
| --- | --- | --- |
| Add old instance change messages discarding |  | [INDY-1909](https://jira.hyperledger.org/browse/INDY-1909) |
| Increase ToleratePrimaryDisconnection and bind re-try time |  | [INDY-1836](https://jira.hyperledger.org/browse/INDY-1836) |
| Add check for None of replica's primary name during logging |  | [INDY-1926](https://jira.hyperledger.org/browse/INDY-1926) |

## 1.6.80 
### Release date: Dec 13th, 2018

### Component Version Information
| Components | Version Numbers |
| --- | --- |
| indy-plenum | 1.6.55 |
| indy-node | 1.6.80 |

### Additional Information:
**There are possible OOM issues during 3+ hours of target load or large catch-ups at 8 GB RAM nodes pool so 32 GB is recommended.**

### Major Fixes
| Description | Additional Information | Ticket Number |
| --- | --- | --- |
| Issuing a pool restart does not work if there is no consensus |  | [INDY-1896](https://jira.hyperledger.org/browse/INDY-1896) |
| Intermittent test failure: test_primary_selection_increase_f |  | [INDY-1872](https://jira.hyperledger.org/browse/INDY-1872) |
| Fix throughput class creation bug |  | [INDY-1888](https://jira.hyperledger.org/browse/INDY-1888) |

## 1.6.79
### Release date: Dec 6th, 2018

### Component Version Information

| Components | Version Numbers |
| --- | --- |
| indy-plenum | 1.6.54 |
| indy-anoncreds | dependency is not required anymore |
| indy-node | 1.6.79 |

### Additional Information:

**Warning: Embedded command-line tool _indy_ is no longer available.** For further pool interaction use _indy-cli_ package https://github.com/hyperledger/indy-sdk/tree/master/cli

[**indy-test-automation repo**](https://github.com/hyperledger/indy-test-automation) has been created for end-to-end tests and additional test tools [**(INDY-1766)**](https://jira.hyperledger.org/browse/INDY-1766)

**The** [**INDY-1818**](https://jira.hyperledger.org/browse/INDY-1818) **(Init Indy Node should output Base58-encrypted verkey already) affects nodes adding.**

**validator-info output has been changed.**  If you use validator-info as data source make sure that you have done necessary changes for compatibility

**There are possible OOM issues during 3+ hours of target load or large catch-ups at 8 GB RAM nodes pool so 32 GB is recommended.**

### Major Fixes

| Description | Additional Information | Ticket Number |
| --- | --- | --- |
| Intermittent test failure: test_primary_selection_increase_f |  | [INDY-1872](https://jira.hyperledger.org/browse/INDY-1872) |
| Pool stopped writing after production load with fees |  | [INDY-1867](https://jira.hyperledger.org/browse/INDY-1867) |
| Node does not validate CLAIM_DEF's filed ref |  | [INDY-1862](https://jira.hyperledger.org/browse/INDY-1862) |
| Sovrin package can't be upgraded |  | [INDY-1850](https://jira.hyperledger.org/browse/INDY-1850) |
| Expected object or value error during batch handling |  | [INDY-1849](https://jira.hyperledger.org/browse/INDY-1849) |
| Node that is not on network is shown as 'unreachable' |  | [INDY-1842](https://jira.hyperledger.org/browse/INDY-1842) |
| Not enough information about upgrade in journalctl |  | [INDY-1834](https://jira.hyperledger.org/browse/INDY-1834) |
| Need to fix 'aws_manage' playbook that fails when inventory directory is not specified |  | [INDY-1827](https://jira.hyperledger.org/browse/INDY-1827) |
| Validator on Sovrin MainNet fails to upgrade, then fails to revert |  | [INDY-1824](https://jira.hyperledger.org/browse/INDY-1824) |
| Pool stops writing during load testing against domain and pool ledgers together |  | [INDY-1823](https://jira.hyperledger.org/browse/INDY-1823) |
| Node service stops during node key validation |  | [INDY-1820](https://jira.hyperledger.org/browse/INDY-1820) |
| Init Indy Node should output Base58-encrypted verkey already |  | [INDY-1818](https://jira.hyperledger.org/browse/INDY-1818) |
| Investigate slowness on TestNet due to demotion |  | [INDY-1816](https://jira.hyperledger.org/browse/INDY-1816) |
| New instance was removed after creating |  | [INDY-1815](https://jira.hyperledger.org/browse/INDY-1815) |
| Upgrade from 1.6.645+ version result errors about packages versions in journalctl |  | [INDY-1781](https://jira.hyperledger.org/browse/INDY-1781) |
| RequestQueue in Replica doesn't clear after View Change |  | [INDY-1765](https://jira.hyperledger.org/browse/INDY-1765) |

### Changes - Additions - Known Issues

| Description | Workaround | Ticket |
| --- | --- | --- |
| Create a Diagram for Components |  | [INDY-1870](https://jira.hyperledger.org/browse/INDY-1870) |
| Create Catch-up Sequence Diagram |  | [INDY-1869](https://jira.hyperledger.org/browse/INDY-1869) |
| Write and Read request flow |  | [INDY-1868](https://jira.hyperledger.org/browse/INDY-1868) |
| Plenum Consensus Protocol Diagram |  | [INDY-1851](https://jira.hyperledger.org/browse/INDY-1851) |
| Change pool state root hash for BLS-signature in Commit messages |  | [INDY-1846](https://jira.hyperledger.org/browse/INDY-1846) |
| 3rd party open source manifest |  | [INDY-1839](https://jira.hyperledger.org/browse/INDY-1839) |
| Enable PreViewChange Strategy |  | [INDY-1835](https://jira.hyperledger.org/browse/INDY-1835) |
| Need to add Names to AWS ec2 instances and security groups |  | [INDY-1828](https://jira.hyperledger.org/browse/INDY-1828) |
| Need to securely automate SSH authenticity checking |  | [INDY-1826](https://jira.hyperledger.org/browse/INDY-1826)- |
| Limit RocksDB memory consumption |  | [INDY-1822](https://jira.hyperledger.org/browse/INDY-1822) |
| Run very long load test on a small local pool |  | [INDY-1821](https://jira.hyperledger.org/browse/INDY-1821) |
| AWS tags for pool automation AWS resources |  | [INDY-1813](https://jira.hyperledger.org/browse/INDY-1813) |
| Adjust last_ordered_3pc and perform GC when detecting lag in checkpoints on backup |  | [INDY-1795](https://jira.hyperledger.org/browse/INDY-1795) |
| Improve usability of current pool automation PoC |  | [INDY-1792](https://jira.hyperledger.org/browse/INDY-1792) |
| As a dev/QA I need to be able to refer different groups in the same namespace using one inventory |  | [INDY-1788](https://jira.hyperledger.org/browse/INDY-1788) |
| Remove security groups at tear-down phase for both tests and playbooks |  | [INDY-1784](https://jira.hyperledger.org/browse/INDY-1784) |
| Clear Requests queue periodically | | [INDY-1780](https://jira.hyperledger.org/browse/INDY-1780) |
| Test ZMQ Memory Consumption with restarting of listener on every X connections |  | [INDY-1776](https://jira.hyperledger.org/browse/INDY-1776) |
| Get information about how many client connections is usually in progress |  | [INDY-1775](https://jira.hyperledger.org/browse/INDY-1775) |
| Do a long test with a load pool can handle |  | [INDY-1774](https://jira.hyperledger.org/browse/INDY-1774) |
| Find out why validation of PrePrepares with Fees takes so long |  | [INDY-1773](https://jira.hyperledger.org/browse/INDY-1773) |
| Check why backup instances stop ordering so often |  | [INDY-1772](https://jira.hyperledger.org/browse/INDY-1772) |
| As a dev I need to be able to perform tests on docker |  | [INDY-1771](https://jira.hyperledger.org/browse/INDY-1771) |
| Test ZMQ Memory Consumption with restricted number of client connections |  | [INDY-1770](https://jira.hyperledger.org/browse/INDY-1770) |
| Run load tests with file storages |  | [INDY-1769](https://jira.hyperledger.org/browse/INDY-1769) |
| Change dependency building for upgrade procedure |  | [INDY-1762](https://jira.hyperledger.org/browse/INDY-1762) |
| Use persisted last_pp_seq_no for recovery of backup primaries |  | [INDY-1759](https://jira.hyperledger.org/browse/INDY-1759) |
| Extend Load Script with GET_TXN |  | [INDY-1756](https://jira.hyperledger.org/browse/INDY-1756) |
| Avoid redundant static validation during signature verification |  | [INDY-1753](https://jira.hyperledger.org/browse/INDY-1753) |
| Find out why max node prod time increases during long load test |  | [INDY-1747](https://jira.hyperledger.org/browse/INDY-1747) |

### Upgrade Scripts:

No further action is required

## 1.6.78
### Release date: Oct 18th, 2018

### Component Version Information

| Components | Version Numbers |
| --- | --- |
| indy-plenum | 1.6.53 |
| indy-anoncreds | 1.0.11 |
| indy-node | 1.6.78 |
|   |   |   |

### Major Fixes

| Description | Additional Information | Ticket Number |
| --- | --- | --- |
| Re-asking for ledger statuses and maximal consistency proofs is not canceled. |   | [INDY-1740](https://jira.hyperledger.org/browse/INDY-1740) |
| Bug in calling notifier methods in Restarter. |   | [INDY-1741](https://jira.hyperledger.org/browse/INDY-1741) |
| 35 view changes were happened during 10 minutes after nodes failure because of invalid request. |   | [INDY-1696](https://jira.hyperledger.org/browse/INDY-1696) |
| Requests queue is not cleared in case of reject-nym transactions. |   | [INDY-1700](https://jira.hyperledger.org/browse/INDY-1700) |
| Throughput critically decreases without causing view_change. |   | [INDY-1672](https://jira.hyperledger.org/browse/INDY-1740) |
| Node can&#39;t catch up large ledger. |   | [INDY-1595](https://jira.hyperledger.org/browse/INDY-1595) |
| Unable to demote node in STN. |   | [INDY-1621](https://jira.hyperledger.org/browse/INDY-1621) |
| View changes happen when all responses should be rejected during load testing scenario. |   | [INDY-1653](https://jira.hyperledger.org/browse/INDY-1653) |
| Node doesn&#39;t write txns after disconnection from the rest nodes. |   | [INDY-1580](https://jira.hyperledger.org/browse/INDY-1580) |
| Throughput is degrading if backup primary is stopped. |   | [INDY-1618](https://jira.hyperledger.org/browse/INDY-1618) |
|   |   |   |   |

### Changes - Additions - Known Issues

| Description | Workaround | Ticket |
| --- | --- | --- |
| Switch off a replica that stopped because disconnected from a backup primary. |   | [INDY-1681](https://jira.hyperledger.org/browse/INDY-1681) |
| Extend load scripts emulating non-smooth load according to the changes in the core script. |   | [INDY-1667](https://jira.hyperledger.org/browse/INDY-1667) |
| Proof of stability under load. |   | [INDY-1607](https://jira.hyperledger.org/browse/INDY-1607) |
| Investigate Out of memory issues with the current load testing. |   | [INDY-1688](https://jira.hyperledger.org/browse/INDY-1688) |
| Do not re-verify signature for Propagates with already verified requests. |   | [INDY-1649](https://jira.hyperledger.org/browse/INDY-1649) |
| POA: Require multiple signatures for important transactions. |   | [INDY-1704](https://jira.hyperledger.org/browse/INDY-1704) |
| Support all FEEs txns in the load script. |   | [INDY-1665](https://jira.hyperledger.org/browse/INDY-1665) |
| Test domain transactions with FEEs. |   | [INDY-1661](https://jira.hyperledger.org/browse/INDY-1661) |
| 3PC Batch should preserve the order of requests when applying PrePrepare on non-primary. |   | [INDY-1642](https://jira.hyperledger.org/browse/INDY-1642) |
| Ability to switch off (remove) replicas with no changes of F value. |   | [INDY-1680](https://jira.hyperledger.org/browse/INDY-1680) |
| A node should be able to participate in BLS multi-signature only if it has a valid proof of possession. |   | [INDY-1589](https://jira.hyperledger.org/browse/INDY-1589) |
| Make validator info as a historical data. |   | [INDY-1637](https://jira.hyperledger.org/browse/INDY-1637) |
|   |   |   | |
| **Known Issue:** Upgrade failed on pool from 1.3.62 to 1.4.66. Note that INDY-1447 was fixed in indy-node 1.5.68, but it still presents in indy-node 1.3.62 and 1.4.66 code. | **So, some of the nodes may not to be upgraded during simultaneous pool-upgrade.** If this problem will appear, stewards should perform manual upgrade of indy-node in accordance with this [instruction:](https://docs.google.com/document/d/1vUvbioL5OsmZMSkwRcu0p0jdttJO5VS8K3GhDLdNaoI)**(!)** To reduce the risk of reproducing INDY-1447, it is **recommended to use old CLI for pool upgrade.** | [INDY-1447](https://jira.hyperledger.org/browse/INDY-1447) |
|   |   |   |   |

### Upgrade Scripts:

**Pool upgrade from indy-node 1.3.62 to indy-node 1.6.78 should be performed simultaneously for all nodes due to txn format changes.**

### Additional Information:

**All indy-cli pools should be recreated with actual genesis files.**

**For more details about txn format changes see** [**INDY-1421**](https://jira.hyperledger.org/browse/INDY-1421) **.**

**There are possible OOM issues during 3+ hours of target load or large catch-ups at 8 GB RAM nodes pool so 32 GB is recommended.**


## 1.6.73
### Release date: Sep 5th, 2018

**Important:** Several iterations were done very rapidly between the last release and this one. All of the changes, upgrades, etc... are included in this new release. Simply upgrading will include them all from 1.6.70 until 1.6.73. To see further, specific numerous changes, please reference the appropriate tickets in the [Hyperledger Jira ticketing system.](https://jira.hyperledger.org/)

### Component Version Information

| Components | Version Numbers |
| --- | --- |
| indy-plenum | 1.6.51 |
| indy-anoncreds | 1.0.11 |
| indy-node | 1.6.73 |
|   |   |   |

### Major Fixes

| Description | Additional Information | Ticket Number |
| --- | --- | --- |
| Fixed and issue where the pool stopped writing after F change. |   | [INDY-1583](https://jira.hyperledger.org/browse/INDY-1583) |
| Fixed an issue where read\_ledger was passing incorrectly formatted stdout and breaks convention |   | [INDY-1645](https://jira.hyperledger.org/browse/INDY-1645) |
| Fixed an issue where the node couldn&#39;t catch up a large ledger. |   | [INDY-1595](https://jira.hyperledger.org/browse/INDY-1595) |
| Fixed an issue where the Validator Info may hang for a couple of minutes. |   | [INDY-1603](https://jira.hyperledger.org/browse/INDY-1603) |
|   |   |   |   |

### Changes - Additions - Known Issues

| Description | Workaround | Ticket |
| --- | --- | --- |
| Made it so that the 3PC Batch should preserve the order of requests when applying PrePrepare on non-primary. |   | [INDY-1642](https://jira.hyperledger.org/browse/INDY-1642) |
| Made it so that Monitor takes into account requests not passing the dynamic validation when triggering view change. |   | [INDY-1643](https://jira.hyperledger.org/browse/INDY-1643) |
| Improved throughput calculation to reduce a chance of false positive View Changes. |   | [INDY-1565](https://jira.hyperledger.org/browse/INDY-1565) |
| Made it so that the performance of monitor is improved. |   | [INDY-1660](https://jira.hyperledger.org/browse/INDY-1660) |
| Made it so that Stewards, can have a script that can generates Proof of possession for their BLS key. That value can now be used in a NODE txn. |   | [INDY-1588](https://jira.hyperledger.org/browse/INDY-1588) |
| Added Support Proof of Possession for BLS keys. |   | [INDY-1389](https://jira.hyperledger.org/browse/INDY-1389) |
| Made it so that the average is not used when calculating total throughput/latency of backups. |   | [INDY-1582](https://jira.hyperledger.org/browse/INDY-1582) |
| Made it so that any client requests are discarded during view change. |   | [INDY-1564](https://jira.hyperledger.org/browse/INDY-1564) |
| Created a simple tool to show graphical representation of some common metrics. |   | [INDY-1568](https://jira.hyperledger.org/browse/INDY-1568) |
| Changed default configs for better performance and stability. |   | [INDY-1549](https://jira.hyperledger.org/browse/INDY-1549) |
|   |   |   | |
| **Known Issue:** Upgrade failed on pool from 1.3.62 to 1.4.66. Note that INDY-1447 was fixed in indy-node 1.5.68, but it still presents in indy-node 1.3.62 and 1.4.66 code. | **So, some of the nodes may not to be upgraded during simultaneous pool-upgrade.** If this problem will appear, stewards should perform manual upgrade of indy-node in accordance with this [instruction:](https://docs.google.com/document/d/1vUvbioL5OsmZMSkwRcu0p0jdttJO5VS8K3GhDLdNaoI)**(!)** To reduce the risk of reproducing INDY-1447, it is **recommended to use old CLI for pool upgrade.** | [INDY-1447](https://jira.hyperledger.org/browse/INDY-1447) |
|   |   |   |   |

### Upgrade Scripts:

**Pool upgrade from indy-node 1.3.62 to indy-node 1.6.73 should be performed simultaneously for all nodes due to txn format changes.**

### Additional Information:

**All indy-cli pools should be recreated with actual genesis files.**

**For more details about txn format changes see** [**INDY-1421**](https://jira.hyperledger.org/browse/INDY-1421) **.**

**There are possible OOM issues during 3+ hours of target load or large catch-ups at 8 GB RAM nodes pool so 32 GB is recommended.**


## 1.6.70
### Release date: Aug 14th, 2018

### Component Version Information

| Components | Version Numbers |
| --- | --- |
| indy-plenum | 1.6.49 |
| indy-anoncreds | 1.0.11 |
| indy-node | 1.6.70 |
|   |   |    |

### Major Fixes

| Description | Additional Information | Ticket Number |
| --- | --- | --- |
| Fixed and issue where several nodes (less than f) were getting ahead the rest ones under load. |   | [INDY-1473](https://jira.hyperledger.org/browse/INDY-1473) |
| Fixed an issue where the pool has stopped to write txns. |   | [INDY-1539](https://jira.hyperledger.org/browse/INDY-1539) |
| Fixed an issue where re-send messages to disconnected remotes. |   | [INDY-1497](https://jira.hyperledger.org/browse/INDY-1497) |
| Fixed an issue where the pool stopped writing under 20txns/sec load. |   | [INDY-1478](https://jira.hyperledger.org/browse/INDY-1478) |
| Fixed an issue where 1.3.62 -\&gt; 1.5.67 forced upgrade without one node in schedule failed. |   | [INDY-1519](https://jira.hyperledger.org/browse/INDY-1519) |
| Fixed an issue where tmp.log must have unique name. |   | [INDY-1502](https://jira.hyperledger.org/browse/INDY-1502) |
| Fixed an issue where a node needed to hook up to a lower viewChange. |   | [INDY-1199](https://jira.hyperledger.org/browse/INDY-1199) |
| Fixed an issue where the one of the nodes lagged behind others after forced view changes. |   | [INDY-1470](https://jira.hyperledger.org/browse/INDY-1470) |
| Made it so that View Change should not be triggered by re-sending Primary disconnected if Primary is not disconnected anymore. |   | [INDY-1544](https://jira.hyperledger.org/browse/INDY-1544) |
|   |   |   |   |

### Changes - Additions - Known Issues

| Description | Workaround | Ticket |
| --- | --- | --- |
| Made it so that as a Trustee running POOL\_UPGRADE txn, you can specify any package depending on indy-node, so that the package with the dependencies get upgraded. |   | [INDY-1491](https://jira.hyperledger.org/browse/INDY-1491) |
| Made it so that Monitor is reset after the view change. |   | [INDY-1555](https://jira.hyperledger.org/browse/INDY-1555) |
| Made it so that GC by Checkpoints are not triggered during View Change. |   | [INDY-1545](https://jira.hyperledger.org/browse/INDY-1545) |
| Made it so that the validator info must show committed and uncommitted roots for all states. |   | [INDY-1542](https://jira.hyperledger.org/browse/INDY-1542) |
| Explored timing and execution time. |   | [INDY-1475](https://jira.hyperledger.org/browse/INDY-1475) |
| Memory leaks profiling. |   | [INDY-1493](https://jira.hyperledger.org/browse/INDY-1493) |
| Bound connection socket to NODE\_IP |   | [INDY-1531](https://jira.hyperledger.org/browse/INDY-1531) |
| Enable TRACK\_CONNECTED\_CLIENTS\_NUM option |   | [INDY-1496](https://jira.hyperledger.org/browse/INDY-1496) |
| Updated revocation registry delta value during REG\_ENTRY\_REVOC writing. |   | [INDY-1378](https://jira.hyperledger.org/browse/INDY-1378) |
| Support latest SDK in Indy Plenum and Node. |   | [INDY-1480](https://jira.hyperledger.org/browse/INDY-1480) |
| Latency measurements in monitor are windowed. |   | [INDY-1468](https://jira.hyperledger.org/browse/INDY-1468) |
| Endorser permissions are not needed for ledger writes. |   | [INDY-1528](https://jira.hyperledger.org/browse/INDY-1528) |
|   |   |   |
| **Known Issue:** Docker pool can&#39;t be built because of new python3-indy-crypto in sdk repo. The problem described in INDY-1517 will be fixed in the next release of indy-node. | Workaround for this problem is to add python3-indy-crypto=0.4.1 to the list of packages to be installed. | [INDY-1517](https://jira.hyperledger.org/browse/INDY-1517) |
| **Known Issue:** Upgrade failed on pool from 1.3.62 to 1.4.66. Note that INDY-1447 was fixed in indy-node 1.5.68, but it still presents in indy-node 1.3.62 and 1.4.66 code. | **So, some of the nodes may not to be upgraded during simultaneous pool-upgrade.** If this problem will appear, stewards should perform manual upgrade of indy-node in accordance with this [instruction:](https://docs.google.com/document/d/1vUvbioL5OsmZMSkwRcu0p0jdttJO5VS8K3GhDLdNaoI)**(!)** To reduce the risk of reproducing INDY-1447, it is **recommended to use old CLI for pool upgrade.** | [INDY-1447](https://jira.hyperledger.org/browse/INDY-1447) |
|   |   |   |  |

### Upgrade Scripts:

**Pool upgrade from indy-node 1.3.62 to indy-node 1.6.70 should be performed simultaneously for all nodes due to txn format changes.**

### Additional Information:

**All indy-cli pools should be recreated with actual genesis files.**

**For more details about txn format changes see** [**INDY-1421**](https://jira.hyperledger.org/browse/INDY-1421) **.**


## 1.5.68


### Component Version Information

| Components | Version Numbers |
| --- | --- |
| indy-plenum | 1.5.48 |
| indy-anoncreds | 1.0.11 |
| indy-node | 1.5.68 |
|   |   |    |

### Major Fixes

| Description | Additional Information | Ticket Number |
| --- | --- | --- |
| Fixed and issue where logs were appearing in the old CLI. |   | [INDY-1471](https://jira.hyperledger.org/browse/INDY-1471) |
| Fixed an issue where there were numerous blacklists under high loads. |   | [INDY-1461](https://jira.hyperledger.org/browse/INDY-1461) |
| Fixed an issue where the pool stopped writing after 1114k txns (different view\_no). |   | [INDY-1460](https://jira.hyperledger.org/browse/INDY-1460) |
| Fixed an issue where the "AttributeError: NoneType object has no attribute 'request' during load"; was appearing. |   | [INDY-1464](https://jira.hyperledger.org/browse/INDY-1464) |
| Fixed an issue where the validator-info was reading an empty file. |   | [INDY-1406](https://jira.hyperledger.org/browse/INDY-1406) |
| Fixed an issue where validator-info -v --json wasn't producing valid JSON. |   | [INDY-1443](https://jira.hyperledger.org/browse/INDY-1443) |
| Fixed an issue where the first Pre-Prepare message had `incorrect state trie` root right after view\_change (on master replica). |   | [INDY-1459](https://jira.hyperledger.org/browse/INDY-1459) |
| Fixed an issue where the pool could not order transactions because Node set incorrect watermarks after its restart. |   | [INDY-1455](https://jira.hyperledger.org/browse/INDY-1455) |
| Fixed an issue where the pool stopped working due to several incomplete view changes. |   | [INDY-1454](https://jira.hyperledger.org/browse/INDY-1454) |
| Fixed an issue where the node crashes on \_remove\_stashed\_checkpoints. |   | [INDY-1427](https://jira.hyperledger.org/browse/INDY-1427) |
| Fixed an issue where memory was running out during non-completed viewChange process (under load). |   | [INDY-1360](https://jira.hyperledger.org/browse/INDY-1360) |
| Fixed an issue where part of nodes continued ordering txns after `incorrect state trie` under load. |   | [INDY-1422](https://jira.hyperledger.org/browse/INDY-1422) |
| Fixed an issue where the upgrade failed on pool from 1.3.62 to 1.4.66.  |   |[INDY-1447](https://jira.hyperledger.org/browse/INDY-1447)   |   
|Fixed an issue where a forced upgrade from 1.3.62 -> 1.5.67 without one node in schedule  failed.   |  |[INDY-1519](https://jira.hyperledger.org/browse/INDY-1519)  |  
|   |  |  |  |



### Changes - Additions - Known Issues

| Description | Workaround | Ticket |
| --- | --- | --- |
| Implemented periodic restart of client stack to allow new clients to connect. |   | [INDY-1431](https://jira.hyperledger.org/browse/INDY-1431) |
| Got rid of peersWithoutRemotes. |   | [INDY-1467](https://jira.hyperledger.org/browse/INDY-1467) |
| High Watermark on backup may be reset to 300. |   | [INDY-1462](https://jira.hyperledger.org/browse/INDY-1462) |
| We now allow optional field in node-to-node and client-to-node. |   | [INDY-1494](https://jira.hyperledger.org/browse/INDY-1494) |
| Catchup during view change may last forever under the load. |   | [INDY-1463](https://jira.hyperledger.org/browse/INDY-1463) |
| Propagate Primary mode should not be set for already started view change. |   | [INDY-1458](https://jira.hyperledger.org/browse/INDY-1458) |
| Catchup needs to be finished during high load. |   | [INDY-1450](https://jira.hyperledger.org/browse/INDY-1450) |
| Included reviewed logging strings in Indy. |   | [INDY-1416](https://jira.hyperledger.org/browse/INDY-1416) |
| Added benchmark performance impact of recorder tool. |   | [INDY-1483](https://jira.hyperledger.org/browse/INDY-1483) |
| Decreased the amount of logging with INFO level. |   | [INDY-1311](https://jira.hyperledger.org/browse/INDY-1311) |
| Made it so that throughput measurements in monitor should are windowed. |   | [INDY-1435](https://jira.hyperledger.org/browse/INDY-1435) |
| Limited the number of requested PROPAGATES in MessageRequests. |   | [INDY-1386](https://jira.hyperledger.org/browse/INDY-1386) |
| Made it so that any client requests during view change are not processed. |   | [INDY-1453](https://jira.hyperledger.org/browse/INDY-1453) |
| Made it so that a node must send LEDGER\_STATUS with correct last ordered 3PC after catch-up. |   | [INDY-1452](https://jira.hyperledger.org/browse/INDY-1452) |
| Fixed calculation of prepared certificates during View Change. |   | [INDY-1385](https://jira.hyperledger.org/browse/INDY-1385) |
| Made it so that catchup should not be interrupted by external events. |   | [INDY-1404](https://jira.hyperledger.org/browse/INDY-1404) |
| **Known Issue:** Upgrade failed on pool from 1.3.62 to 1.4.66. Note that INDY-1447 was fixed in indy-node 1.5.68, but it still presents in indy-node 1.3.62 and 1.4.66 code. So, some of the nodes may not to be upgraded during simultaneous pool-upgrade. If this problem will appear, stewards should perform manual upgrade of indy-node in accordance with this instruction: (!) To reduce the risk of reproducing INDY-1447, it is recommended to use old CLI for pool upgrade.  |   | [INDY-1447](https://jira.hyperledger.org/browse/INDY-1447) |
|   |   |   | |

### Upgrade Scripts:

**Pool upgrade from indy-node 1.3.62 should be performed simultaneously for all nodes due to txn format changes.**

### Additional Information:

**All indy-cli pools should be recreated with actual genesis files.
For more details about txn format changes see INDY-1421.**



## 1.4.66
### Release date: Jul 2nd, 2018


### Component Version Information

| Components | Version Numbers |
| --- | --- |
| indy-plenum | 1.4.45 |
| indy-anoncreds | 1.0.11 |
| indy-node | 1.4.66 |
|   |   |   |

### Major Fixes

| Description | Additional Information | Ticket Number |
| --- | --- | --- |
| Fixed and issues where one of the nodes stopped writing after 44287 txns with errors in status. |   | [INDY-1410](https://jira.hyperledger.org/browse/INDY-1410) |
| Fixed an issue where the pool stopped accepting transactions on 5731 txns (1 sec delays, no logging). |   | [INDY-1365](https://jira.hyperledger.org/browse/INDY-1365) |
| Fixed an issue where the pool stopped writing after ~300,000 txns from 5 clients |   | [INDY-1315](https://jira.hyperledger.org/browse/INDY-1315) |
| Fixed an issue where STN was not accepting transactions with only one node down. |   | [INDY-1351](https://jira.hyperledger.org/browse/INDY-1351) |
| Fixed an issue where the pool stops taking txns at ~178k txns written in ledger. |   | [INDY-1260](https://jira.hyperledger.org/browse/INDY-1260) |
| Fixed an issue where `ReqIdrToTxn` does not store information about the ledger. |   | [INDY-1327](https://jira.hyperledger.org/browse/INDY-1327) |
| Made simple Timeout fixes of the current View Change protocol. |   | [INDY-1341](https://jira.hyperledger.org/browse/INDY-1341) |
| Fixed an issue where the migration fails in case of upgrade to version with new transactions format. |   | [INDY-1379](https://jira.hyperledger.org/browse/INDY-1379) |
| Fixed an issue where `--network parameter of read_ledger ` doesn't work. |   | [INDY-1318](https://jira.hyperledger.org/browse/INDY-1318) |
| Fixed an issue where the /var/log/indy/validator-info.log was inappropriately owned by root. |   | [INDY-1310](https://jira.hyperledger.org/browse/INDY-1310) |
| Created a fix around the issues found in the current logic of catch-up. |   | [INDY-1298](https://jira.hyperledger.org/browse/INDY-1298) |
| Fixed GetValidatorInfo so it has correct validation for signature and permissions. |   | [INDY-1363](https://jira.hyperledger.org/browse/INDY-1363) |
| Fixed an issue where there was an unhandled exception during node working. |   | [INDY-1316](https://jira.hyperledger.org/browse/INDY-1316) |
| Fixed an issue where `validator-info` and `read_ledger` were giving inconsistent responses in node on provisional. |   | [INDY-1219](https://jira.hyperledger.org/browse/INDY-1219) |
| Fixed an issue where the pool stops taking txns at 3000 writing connections. |   | [INDY-1259](https://jira.hyperledger.org/browse/INDY-1259) |
|   |   |   |
|   |   |   |   |

### Changes - Additions - Known Issues

| Description | Workaround | Ticket |
| --- | --- | --- |
| Reviewed and replaced `assert` with exceptions in indy-plenum where needed. |   | [INDY-810](https://jira.hyperledger.org/browse/INDY-810) |
| Tuned RocksDB options for the best performance. |   | [INDY-1245](https://jira.hyperledger.org/browse/INDY-1245) |
| Created a migration guide from Indy-node 1.3 to 1.4. |   | [INDY-1392](https://jira.hyperledger.org/browse/INDY-1392) |
| Сhanged a key in the requests map and field reqIdr in Pre Prepare and Ordered. |   | [INDY-1370](https://jira.hyperledger.org/browse/INDY-1370) |
| Investigated issues found during load testing of 25-nodes pool with increased timeouts for catchups and viewchange. |   | [INDY-1400](https://jira.hyperledger.org/browse/INDY-1400) |
| We now support binding on separate NICs for Client-to-Node and Node-to-Node communication. |   | [INDY-1332](https://jira.hyperledger.org/browse/INDY-1332) |
| Added short checkpoints stabilization without matching digests. |   | [INDY-1329](https://jira.hyperledger.org/browse/INDY-1329) |
| Added indy-crypto package to the hold list. |   | [INDY-1323](https://jira.hyperledger.org/browse/INDY-1323) |
| Removed ledger status based catch-up trigger together with the wrong catch-up workflow. |   | [INDY-1297](https://jira.hyperledger.org/browse/INDY-1297) |
| Read-ledger without storage copy in case of RocksDB (RocksDB read-only mode support). |   | [INDY-1243](https://jira.hyperledger.org/browse/INDY-1243) |
| Applied state machine to Catchup code. |   | [INDY-971](https://jira.hyperledger.org/browse/INDY-971) |
| Refactored the common Request structure. |   | [INDY-1124](https://jira.hyperledger.org/browse/INDY-1124) |
| Refactored the common transactions structure. |   | [INDY-1123](https://jira.hyperledger.org/browse/INDY-1123) |
| We now support the new libindy with changed txn format. |   | [INDY-1319](https://jira.hyperledger.org/browse/INDY-1319) |
| Explored config parameters to find the best performance/stability settings. |   | [INDY-1334](https://jira.hyperledger.org/browse/INDY-1334) |
| Extended the Validator Info tool to provide more information about the current state of the pool. |   | [INDY-1175](https://jira.hyperledger.org/browse/INDY-1175) |
|  A Steward needs to be able to get validator-info from all nodes. |   | [INDY-1184](https://jira.hyperledger.org/browse/INDY-1184) |
| Modified existing load scripts for a better load testing. |   | [INDY-1279](https://jira.hyperledger.org/browse/INDY-1279) |
| Performed a migration from LevelDB to RocksDB |   | [INDY-1244](https://jira.hyperledger.org/browse/INDY-1244) |
| A Trustee needs to be able to restart the pool in critical situations. |   | [INDY-1173](https://jira.hyperledger.org/browse/INDY-1173) |
| Move the log compression into separate process. |   | [INDY-1275](https://jira.hyperledger.org/browse/INDY-1275) |
| **Known Issue:** There's an incorrect read\_ledger info with seq\_no parameter. |   | [INDY-1415](https://jira.hyperledger.org/browse/INDY-1415) |
| **Known Issue:** Pool upgrade should be performed simultaneously for all nodes due to txn format changes. All indy-cli pools should be recreated with actual genesis files. |   |   |
| **List of breaking changes for migration from indy-node 1.3 to 1.4:** |   | [1.3-1.4 Migration Guide](https://github.com/hyperledger/indy-node/blob/master/docs/1.3_to_1.4_migration_guide.md) |

### Upgrade Scripts:

**Pool upgrade should be performed simultaneously for all nodes due to txn format changes.**

**All indy-cli pools should be recreated with actual genesis files.**

#### CLI Upgrading:

**Old CLI (`indy`):**

upgrade from 1.3 to 1.4 version
delete `~.ind-cli/networks/&lt;network_name&gt;/data` folder
replace both old genesis files by new ones (from 1.4 node)

**New CLI (`indy-cli`):**

upgrade from 1.4 to 1.5 version
recreate indy-cli pool using 1.4 pool genesis file (from 1.4 node)

### Additional Information:

**List of breaking changes for migration from indy-node 1.3 to 1.4:**

https://github.com/hyperledger/indy-node/blob/master/docs/1.3\_to\_1.4\_migration\_guide.md

**IndyNode 1.4 and LibIndy 1.5 compatibility:**

_General_

By default LibIndy 1.5 will be compatible with IndyNode 1.3 (current stable), and not 1.4 (the new one).

LibIndy 1.5 can become compatible with IndyNode 1.4 if `indy_set_protocol_version(2)` is called during app initialization.

_Guideline for teams and apps_

Applications can freely update to LibIndy 1.5 and still use stable Node 1.3

If an app wants to work with the latest master or Stable Node 1.4, then they need to support breaking changes (there are not so many, mostly a new reply for write txns as txn format is changed, see 1.3\_to\_1.4\_migration\_guide.md)

call `indy_set_protocol_version(2)` during app initialization

Use https://github.com/hyperledger/indy-sdk/blob/b4a2bb82087e2eafe5e55bddb20a3069e5fb7d0b/cli/README.md#old-python-based-cli-migration to export dids from your old CLI wallet to the new one (new indy-cli).



## 1.3.62
### Release date: May 22th, 2018


### Component Version Information

| Components | Version Numbers |
| --- | --- |
| indy-plenum | 1.2.42 |
| indy-anoncreds | 1.0.11 |
| indy-node | 1.3.62 |
|   |   |    |

### Major Fixes

| Description | Additional Information | Ticket Number |
| --- | --- | --- |
| Fixed an issue where the STN was losing consensus. |   | [INDY-1256](https://jira.hyperledger.org/browse/INDY-1256) |
| Fixed an issue where we were unable to use the read\_ledger tool with the parameter "to". |   | [INDY-1284](https://jira.hyperledger.org/browse/INDY-1284) |
|Fixed the upgrade from 1.2.223 (1.3.55 stable analogue) to 1.3.410 (rocksdb) wasn't working.|    |[INDY-1330](https://jira.hyperledger.org/browse/INDY-1330)  |
|   |   |   |    |   

### Changes - Additions - Known Issues

| Description | Workaround | Ticket |
| --- | --- | --- |
| Support was added for supervisord. |   | [https://github.com/hyperledger/indy-node/pull/588](https://jira.hyperledger.org/browse/INDY-1186) |
| Indy-node dependencies are fixed.  |   |    |
|   |   |   |    |

### Upgrade Scripts:

None for this release.

### Additional Information:

None at this time.


## 1.3.57

### Component Version Information

| Components | Version Numbers |
| --- | --- |
| indy-node | 1.3.57 |
|   |   |   |

### Major Fixes

| Description | Additional Information | Ticket Number |
| --- | --- | --- |
| The Node was restarting because of an &quot;Out of memory&quot; error. |   | [INDY-1238](https://jira.hyperledger.org/browse/INDY-1238) |
| The pool was not working after not simultaneous manual pool upgrades. |   | [INDY-1197](https://jira.hyperledger.org/browse/INDY-1197) |
| When adding a new schema, field &#39;attr\_names&#39; of schema json can be an empty list. |   | [INDY-1169](https://jira.hyperledger.org/browse/INDY-1169) |
| This prevents an Identity Owner from creating a schema or claimDef. |   | [INDY-1111](https://jira.hyperledger.org/browse/INDY-1111) |
| There was the same primary for both instances 0 and 1. |   | [INDY-1112](https://jira.hyperledger.org/browse/INDY-1112) |
| The node logs were being duplicated in syslog. |   | [INDY-1102](https://jira.hyperledger.org/browse/INDY-1102) |
| It was possible to create several nodes with the same alias. |   | [INDY-1148](https://jira.hyperledger.org/browse/INDY-1148) |
| There was ambiguous behavior after node demotion. |   | [INDY-1179](https://jira.hyperledger.org/browse/INDY-1179) |
| One of the nodes were not responding to libindy after several running load tests. |   | [INDY-1180](https://jira.hyperledger.org/browse/INDY-1180) |
| When returning N-F nodes to the pool, &quot;View change&quot; was not occurring if the Primary node was stopped. |   | [INDY-1151](https://jira.hyperledger.org/browse/INDY-1151) |
| There was a failed restart after getting the &quot;unhandled exception (KeyError)&quot;. |   | [INDY-1152](https://jira.hyperledger.org/browse/INDY-1152) |
| Fixed a bug where you were unable to install indy-node if sdk repo is in sources.list   |   |[INDY-1269](https://jira.hyperledger.org/browse/INDY-1269)   |  
|   |   |   |   |

### Changes - Additions - Known Issues

| Description | Workaround | Ticket |
| --- | --- | --- |
| Made it so that a developer can distinguish logs of each replica. |   | [INDY-1186](https://jira.hyperledger.org/browse/INDY-1186) |
| Made it so a developer, can track the path of each request. |   | [INDY-1187](https://jira.hyperledger.org/browse/INDY-1187) |
| Made it so that you can use RocksDB as a key-value storage. |   | [INDY-1205](https://jira.hyperledger.org/browse/INDY-1205) |
| Refactored the common Request structure. |   | [INDY-1124](https://jira.hyperledger.org/browse/INDY-1124) |
| Made it so that it supports anoncreds revocation in Indy. |   | [INDY-680](https://jira.hyperledger.org/browse/INDY-680) |
| Made it so that it supports REVOC\_REG\_DEF transaction. |   | [INDY-1134](https://jira.hyperledger.org/browse/INDY-1134) |
| Made it so that it supports GET\_REVOC\_REG\_DEF request. |   | [INDY-1135](https://jira.hyperledger.org/browse/INDY-1135) |
| Made it so that it supports REVOC\_REG\_ENTRY transaction. |   | [INDY-1136](https://jira.hyperledger.org/browse/INDY-1136) |
| Made it so that it supports GET\_REVOC\_REG request. |   | [INDY-1137](https://jira.hyperledger.org/browse/INDY-1137) |
| Made it so that it supports getting state root by timestamp. |   | [INDY-1138](https://jira.hyperledger.org/browse/INDY-1138) |
| Got rid of the RAET code. |   | [INDY-1057](https://jira.hyperledger.org/browse/INDY-1057) |
| Incubation: Move CI part of pipelines to Hyperledger infrastructure. |   | [INDY-837](https://jira.hyperledger.org/browse/INDY-837) |
| Made it so that a user can revoke a connection by rotating the new key to nothing. |   | [INDY-582](https://jira.hyperledger.org/browse/INDY-582) |
| **Known Issue:** Define the policy how to restore node from the state when it&#39;s stashing all the reqs and there is a risk of running out of memory. |   | [INDY-1250](https://jira.hyperledger.org/browse/INDY-1250) |
| **Known Issue:** Re-promoted node cannot hook up to a lower viewChange. |   | [INDY-1199](https://jira.hyperledger.org/browse/INDY-1199) |
| **Known Issue:** One of the nodes does not respond to libindy after several running load test. |   | [INDY-1180](https://jira.hyperledger.org/browse/INDY-1180) |
| **Known Issue:** One node fails behind others during the load\_test with a high load. |   | [INDY-1188](https://jira.hyperledger.org/browse/INDY-1188) |
|**Known Issue:** Pool can be broken by primary node reboot in case of network issues between nodes. **Note:** RocksDB was added as dependency (INDY-1205). It is used for revocation, but the rest part of node functionality is still using LevelDB.   |   |[INDY-1256](https://jira.hyperledger.org/browse/INDY-1256)       |
|   |   |   |    |

### Upgrade Scripts

None for this release.

### Additional Information:

None at this time.


## 1.3.55
### Release date: Feb 28th, 2018

**Important: Upgrade to this version should be performed simultaneously for all nodes (with `force=True`).**

### Component Version Information

| Components | Version Numbers |
| --- | --- |
| indy-plenum | 1.2.34 |
| indy-anoncreds | 1.0.11 |
| indy-node | 1.3.55 |
|   |   |    |

### Major Fixes

| Description | Additional Information | Ticket Number |
| --- | --- | --- |
| Transactions were missing from the config ledger after the upgrade. |   | [INDY-799](https://jira.hyperledger.org/browse/INDY-799) |
| The node was broken after a load\_test.py run. |   | [INDY-960](https://jira.hyperledger.org/browse/INDY-960) |
| The pool stopped taking transactions after sending 1,000 simultaneous transactions. |   | [INDY-911](https://jira.hyperledger.org/browse/INDY-911) |
| The pool stopped working: Node services stop with 1,000 simultaneous clients doing GET\_NYM reads |   | [INDY-986](https://jira.hyperledger.org/browse/INDY-986) |
| The node is broken after adding it to the pool. |   | [INDY-948](https://jira.hyperledger.org/browse/INDY-948) |
| The generate\_indy\_pool\_transactions command can be run only by an indy user. |   | [INDY-1048](https://jira.hyperledger.org/browse/INDY-1048) |
| Made it so that updates to existing Schemas are not allowed. |   | [INDY-1035](https://jira.hyperledger.org/browse/INDY-1035) |
| The pool was unable to write txns after two nodes adding. |   | [INDY-1018](https://jira.hyperledger.org/browse/INDY-1018) |
| Fixed a bug where it was possible to override CLAIM\_DEF for existing schema-did pair. |   | [INDY-1083](https://jira.hyperledger.org/browse/INDY-1083) |
| Fixed a bug where here was a huge amount of calls and a lot of execution time in kv\_store.py. |   | [INDY-1077](https://jira.hyperledger.org/browse/INDY-1077) |
| One of added nodes wasn&#39;t catching up. |   | [INDY-1029](https://jira.hyperledger.org/browse/INDY-1029) |
| The pool stopped working and lost consensus while new node was performing a catch-up. |   | [INDY-1025](https://jira.hyperledger.org/browse/INDY-1025) |
| Performing a View Change on large pools of 19 or more nodes can cause pool to stop functioning. |   | [INDY-1054](https://jira.hyperledger.org/browse/INDY-1054) |
| Performing a View Change issue stopped the pool from accepting new transactions. |   | [INDY-1034](https://jira.hyperledger.org/browse/INDY-1034) |
| We were unable to send transactions in STN. |   | [INDY-1076](https://jira.hyperledger.org/browse/INDY-1076) [INDY-1079](https://jira.hyperledger.org/browse/INDY-1079) |
| Replica.lastPrePrepareSeqNo may not be reset on view change. |   | [INDY-1061](https://jira.hyperledger.org/browse/INDY-1061) |
| We were unable to send an upgrade transaction without including demoted nodes. |   | [INDY-897](https://jira.hyperledger.org/browse/INDY-897) |
| The Nym request to STN was resulting in inconsistent responses. |   | [INDY-1069](https://jira.hyperledger.org/browse/INDY-1069) |
| The validator node was being re-promoted during view change. |   | [INDY-959](https://jira.hyperledger.org/browse/INDY-959) |
| There was a false cancel message during an upgrade. |   | [INDY-1078](https://jira.hyperledger.org/browse/INDY-1078) |
| Transactions were being added to nodes in STN during system reboot.. |   | [INDY-1045](https://jira.hyperledger.org/browse/INDY-1045) |
| There were problems with nodes demotion during load test. |   | [INDY-1033](https://jira.hyperledger.org/browse/INDY-1033) |
| The node monitoring tool (email plugin) wasn&#39;t working. |   | [INDY-995](https://jira.hyperledger.org/browse/INDY-995) |
| ATTRIB transaction with ENC and HASH wasn&#39;t working. |   | [INDY-1074](https://jira.hyperledger.org/browse/INDY-1074) |
| When returning N-F nodes to the pool, View Change does not occur if Primary node is stopped. |   | [INDY-1151](https://jira.hyperledger.org/browse/INDY-1151) |
| We were unable to recover write consensus at n-f after f+1 descent. |   | [INDY-1166](https://jira.hyperledger.org/browse/INDY-1166) |
| Newly upgraded STN fails to accept transactions (pool has been broken after upgrade because of one not upgraded node).  |   |[INDY-1183](https://jira.hyperledger.org/browse/INDY-1183)   |   
|We were unable to submit upgrade transactions to STN.   |    |[INDY-1190](https://jira.hyperledger.org/browse/INDY-1190)     
|   |    |    |    |

### Changes - Additions - Known Issues

| Description | Workaround | Ticket |
| --- | --- | --- |
| Added indy-sdk test dependency to plenum and use indy-sdk for plenum tests. |   | [INDY-900](https://jira.hyperledger.org/browse/INDY-900) [INDY-901](https://jira.hyperledger.org/browse/INDY-901) |
| Published docker images to dockerhub. |   | [INDY-962](https://jira.hyperledger.org/browse/INDY-962) |
| Simplified the view change code. |   | [INDY-480](https://jira.hyperledger.org/browse/INDY-480) |
| Refactored config.py to reflect file folder re-factoring for Incubation. |   | [INDY-878](https://jira.hyperledger.org/browse/INDY-878) |
| Added Abstract Observers Support. |   | [INDY-628](https://jira.hyperledger.org/browse/INDY-628) |
| Updated information in &quot;Getting Started with Indy&quot;. |   | [INDY-1062](https://jira.hyperledger.org/browse/INDY-1062) |
| Updated information in &quot;Setting Up a Test Indy Network in VMs&quot;. |   | [INDY-1062](https://jira.hyperledger.org/browse/INDY-1062) |
| Add iptables rules to limit the number of clients connections. |   | [INDY-1087](https://jira.hyperledger.org/browse/INDY-1087) |
| Knowledge transfer on Indy build processes. |   | [INDY-1088](https://jira.hyperledger.org/browse/INDY-1088) |
| Incubation: Move CI part of pipelines to Hyperledger infrastructure. |   | [INDY-837](https://jira.hyperledger.org/browse/INDY-837) |
| Made it so that a user can revoke a connection by rotating the new key to nothing. |   | [INDY-582](https://jira.hyperledger.org/browse/INDY-582) |
| Client needs to be able to make sure that we have the latest State Proof. |   | [INDY-928](https://jira.hyperledger.org/browse/INDY-928) |
| Created it so that anyone could have access to an up-to-date Technical overview of plenum and indy. |   | [INDY-1022](https://jira.hyperledger.org/browse/INDY-928) |
| **Known Issue:** Pool has lost consensus after primary demotion (with 4 nodes setup only). |   | [INDY-1163](https://jira.hyperledger.org/browse/INDY-1163) |
| **Known Issue:** Ambiguous behavior after node demotion. |   | [INDY-1179](https://jira.hyperledger.org/browse/INDY-1179) |
| **Known Issue:** One of the nodes does not respond to libindy after several running load test. |   | [INDY-1180](https://jira.hyperledger.org/browse/INDY-1180) |
|**Known Issue:** Pool does not work after not simultaneous manual pool upgrades.   |   |[INDY-1197](https://jira.hyperledger.org/browse/INDY-1197)   |   
|**Known Issue:** Pool stops working if the primary node was not included to schedule in the upgrade transaction.   |   |[INDY-1198](https://jira.hyperledger.org/browse/INDY-1198)  |
|   |   |     |     |


### Additional Information:

Node promoting is not recommended for 1.3.52 version according to known issues because backup protocol instances may work incorrectly until next view change.

As mentioned above, upgrade to this version should be performed simultaneously for all nodes (with `force=True`).

## 1.2.50
### Release date: Dec 18th, 2017


### Component Version Information

| Components | Version Numbers |
| --- | --- |
| indy-plenum | 1.2.29 |
| indy-anoncreds | 1.0.11 |
| indy-node | 1.2.50 |
|   |   |   |

### Major Fixes

| Description | Additional Information | Ticket Number |
| --- | --- | --- |
| A node was maintaining a pace with the network exactly 12 transactions behind. |   | [INDY-759](https://jira.hyperledger.org/browse/INDY-759) |
| New nodes added to an existing pool were unable to sync ledgers with the pool. |   | [INDY-895](https://jira.hyperledger.org/browse/INDY-895) |
| Scheduled upgrades were happening at the current time on some of the nodes. |   | [INDY-231](https://jira.hyperledger.org/browse/INDY-231) |
| Some nodes were not restarting after a canceled pool upgrade. |   | [INDY-157](https://jira.hyperledger.org/browse/INDY-157) |
| A node was getting the wrong `upgrade_log` entries after restarting and was running the wrong upgrade. |   | [INDY-917](https://jira.hyperledger.org/browse/INDY-917) |
| An earlier `pool_upgrade` was not happening when there was an upgrade to schedule to happen in the future. |   | [INDY-701](https://jira.hyperledger.org/browse/INDY-701) |
| A validator was running instance change continually on the live pool. |   | [INDY-932](https://jira.hyperledger.org/browse/INDY-932) |
| New nodes added to an existing pool were unable to participate in consensus after the upgrade. |   | [INDY-909](https://jira.hyperledger.org/browse/INDY-909) |
| The node logs were repeating the message, &quot;NodeRequestSuspiciousSpike suspicious spike has been noticed.&quot; |   | [INDY-541](https://jira.hyperledger.org/browse/INDY-541) |
| Unable to catch up the agent if a validator was down. |   | [INDY-941](https://jira.hyperledger.org/browse/INDY-941) |
| The pool was unable to write nyms after BLS keys enabling. |   | [INDY-958](https://jira.hyperledger.org/browse/INDY-958) |
| The last pool node is `failed to upgrade`; during a pool upgrade. |   | [INDY-953](https://jira.hyperledger.org/browse/INDY-953) |
| State Proof creating is fixed. |   | [INDY-954](https://jira.hyperledger.org/browse/INDY-954) |
| State Proof verifying is fixed. |   | [INDY-949](https://jira.hyperledger.org/browse/INDY-949) |
|   |   |   |    |

### Changes - Additions - Known Issues

| Description | Workaround | Ticket |
| --- | --- | --- |
| Signed State implementation |   | [INDY-670](https://jira.hyperledger.org/browse/INDY-670) |
| State Proofs implementation |   | [INDY-790](https://jira.hyperledger.org/browse/INDY-790) |
| Removed all non-Indy branding from the indy-plenum repo. |   | [INDY-829](https://jira.hyperledger.org/browse/INDY-829) |
| Removed all non-Indy branding from the indy-anoncreds repo. |   | [INDY-855](https://jira.hyperledger.org/browse/INDY-855) |
| Removed all non-Indy branding from the indy-node repo. |   | [INDY-830](https://jira.hyperledger.org/browse/INDY-830) |
| Backward compatibility of nodes with state proofs support with old clients. |   | [INDY-877](https://jira.hyperledger.org/browse/INDY-877) |
| Support of multiple pool networks by Indy Node. |   | [INDY-831](https://jira.hyperledger.org/browse/INDY-831) |
| Support of multiple pool networks by Indy Client (CLI). |   | [INDY-832](https://jira.hyperledger.org/browse/INDY-832) |
| Created proper file folder paths for system service. |   | [INDY-833](https://jira.hyperledger.org/browse/INDY-833) |
| Client needs to be able to send read requests to one Node only. |   | [INDY-927](https://jira.hyperledger.org/browse/INDY-927) |
| Client needs to be able to make sure that we have the latest State Proof. |   | [INDY-928](https://jira.hyperledger.org/browse/INDY-928) |
| **Known Issue:** Node is broken after `load_test.py` run |   | [INDY-960](https://jira.hyperledger.org/browse/INDY-960) |
|    |    |    |    |

### Additional Information:

Mapping of all file/folder changes are located [here](https://docs.google.com/spreadsheets/d/1A84H8knCtn8rrTirzxta8XC1jpHBjvQiqrxquTv6bpc/edit#gid=0).

#### Upgrade Steps


1. Send Pool Upgrade command so all nodes upgrade.

2. Sometime later each Steward will need to do the following steps to add their BLS Keys:

##### Steps to Add BLS Keys

**_From the Validator Node:_**

1. Generate a new 32-byte seed for the bls key (we recommend pwgen):

``$ sudo apt install pwgen``

``$ pwgen -s -y -B 32 1``

If the output has a single-quote symbol ('), rerun until it doesn't.

**NOTE: This is not your Steward or Node seed.**

2. Record the seed **somewhere secure**.

3. Switch to the indy user.

``$ sudo su - indy``

4. Configure the BLS key.

``$ init_bls_keys --name <NODE_ALIAS> --seed '<SEED>'``

The ``--seed`` is the seed you generated above, and will be used to create the BLS key.

_Example with Seed:_

 ``$ init_bls_keys --name Node1 --seed 'xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx'``

Capture the stdout at the end of the output, which looks like the following, and record it.

`BLS Public key is 3AfkzUZVn2WT9mxW2zQXMgX39FXSY5qzohnMVpdvNS5KSath1YG5Ux4u9ubTFTaP6W55XX9Yx7xPWeYos489oyY53WzwNBG7X4o32ESnZ9xacLmNsQLBjqc6oqpWGTbEXv4edFTrZ88n93sEh4fjFhQMumaXxDfWJgd9aj7KCSpf38F`

5. Exit the indy user.

``$ exit ``

**_From the CLI Node:_**

1. Manually upgrade the CLI.

 ``$ sudo apt update``

 ``$ sudo apt upgrade``

2. Launch the CLI.

``$ indy ``

The first time running the upgraded CLI you will be prompted to migrate your previous settings. Answer "Yes."

3. Connect to the pool.

`indy> connect live`

4. Set your Steward as the signer in the CLI.

`indy@live> use DID <Steward DID>`

_Example:_

`indy@live> use DID Th7MpTaRZVRYnPiabds81Y`

**Note:** If your DID is not found in the wallet, you will need to use your steward seed:

`indy@live> new key with seed <steward_seed>`

5. Now you will send a node transaction like what you did when you added the node to the pool. You will add the BLS key as a new parameter to the transaction to update the pool ledger with this additional public key. For 'dest', use the same base58 value for this that was used when you initially onboarded your VM onto the provisional pool.

`indy@live> send NODE dest=<node_dest> data={'alias':'<node name>','blskey': '<key_generated_by_init_bls_keys>'}`

_Example:_

`indy@live> send NODE dest=Gw6pDLhcBcoQesN72qfotTgFa7cbuqZpkX3Xo6pLhPhv data={'alias':'Node1','blskey': '3AfkzUZVn2WT9mxW2zQXMgX39FXSY5qzohnMVpdvNS5KSath1YG5Ux4u9ubTFTaP6W55XX9Yx7xPWeYos489oyY53WzwNBG7X4o32ESnZ9xacLmNsQLBjqc6oqpWGTbEXv4edFTrZ88n93sEh4fjFhQMumaXxDfWJgd9aj7KCSpf38F'}`

**Note:** The 'node_dest' value can be found on the node with `sudo read_ledger --type pool`.


#### Questions and Answers

##### BLS Keys for State Proofs


**What does BLS stand for?**

Boneh-Lynn-Shacham - The BLS signature scheme is used to verify that a signer is authentic.

**How does the CLI use State Proof for confirmation?**

When the CLI requests information about a transaction it checks the BLS signatures to verify the transaction was written by nodes that are part of the validator pool. The CLI sends a request to one node (arbitrary one). If the Reply doesn't have a State Proof, or the reply is incorrect/invalid, then CLI falls back to sending requests to all Nodes and waiting for f+1 equal Replies.

**What if not all nodes in the pool have BLS signing keys for a transaction?**

Transactions only get signed if all nodes reaching consensus can sign it (>= n-f Nodes with correct BLS signatures).

**Can the bls_seed be any 32 character seed like the Steward seed?**

Yes.

**When adding a new node to an existing pool where do I find my BLS key?**

When initializing your node using `init_indy_node` the output will display the keys for the node including the BLS key. It can be found in /var/lib/indy/<network_name>/keys/<node_name>/bls_keys/bls_pk file (e.g.: /var/lib/indy/sandbox/keys/Node1/bls_keys/bls_pk)

When you send the transaction to add the new node to the pool it will also contain the BLS key in the transaction shown in this example.

*Example of send node command with BLS for 5th node in test pool:*

 ``send NODE dest=4Tn3wZMNCvhSTXPcLinQDnHyj56DTLQtL61ki4jo2Loc data=
{'client_port': 9702, 'client_ip': '10.0.0.105', 'alias': 'Node5', 'node_ip': '10.0.0.105', 'node_port': 9701, 'services': ['VALIDATOR'], 'blskey':'2RdajPq6rCidK5gQbMzSJo1NfBMYiS3e44GxjTqZUk3RhBdtF28qEABHRo4MgHS2hwekoLWRTza9XiGEMRCompeujWpX85MPt87WdbTMysXZfb7J1ZXUEMrtE5aZahfx6p2YdhZdrArFvTmFWdojaD2V5SuvuaQL4G92anZ1yteay3R'}``

**Can I use a seed when generating my BLS keys?**

For a new node when using `init_indy_node` if you specify a seed for this script that same seed is used to generate your BLS keys.

**For existing nodes** being upgraded to 1.2.50, which includes state proofs, you would use the script `init_bls_keys` where you can specify a 32-character seed on the command line.

 ``init_bls_keys --name <NODE_ALIAS> --seed '<SEED>'``

After running `init_bls_keys`, Stewards of existing nodes will be required use their CLI node to update their validator's information on the ledger to include the bls keys:

 ``send NODE dest=<node_dest> data={'alias':'<node name>', 'blskey': '<key_generated_by_init_bls_keys>'}``

##### Multi-network and indy_config.py

**Where do I find the configuration file settings?**

With file and folder changes the new location for `indy_config.py` is in the directory location /etc/indy/. The configuration file has a new setting called ``"NETWORK_NAME"`` which is used to identify which network and associated genesis transaction files to use, such as `sandbox` or `live`. If adding a new node to a live pool, change this setting before initializing the node.
The genesis files are now located in their own directory based off the network name "/var/lib/indy/NETWORK_NAME". The defaults are `live`, `local`, and `sandbox`. Setting the ``"NETWORK_NAME"`` in the `indy_config.py` file will determine which network is used. The default setting in the `indy_config.py` file is "``"NETWORK_NAME=sandbox"``.


## 1.1.43
### Release date: Oct 24th, 2017


### Component Version Information

| Components | Version Numbers |
| --- | --- |
| indy-plenum | 1.1.27 |
| indy-anoncreds | 1.0.10 |
| indy-node | 1.1.43 |
|   |   |   |

### Major Fixes

| Description | Additional Information | Ticket Number |
| --- | --- | --- |
| Added a migration script which eliminates redundant fields with `null` values from legacy transactions in the domain ledger. |   | [INDY-895](https://jira.hyperledger.org/browse/INDY-895) [INDY-869](https://jira.hyperledger.org/browse/INDY-869) |
| Added a constraint on `version` field of `POOL_UPGRADE` transaction that denies values lower than the current installed version. |   | [INDY-895](https://jira.hyperledger.org/browse/INDY-895) [INDY-869](https://jira.hyperledger.org/browse/INDY-869) |
| Added prevention of upgrade to a lower version to `Upgrader` class. |   | [INDY-895](https://jira.hyperledger.org/browse/INDY-895) [INDY-869](https://jira.hyperledger.org/browse/INDY-869) |
| Fixed a bug in `Upgrader` class in search for a `POOL_UPGRADE cancel` transaction for the last `POOL_UPGRADE start` transaction. |   | [INDY-895](https://jira.hyperledger.org/browse/INDY-895) [INDY-869](https://jira.hyperledger.org/browse/INDY-869) |
| Added a test verifying prevention of upgrade to a lower version. |   | [INDY-895](https://jira.hyperledger.org/browse/INDY-895) [INDY-869](https://jira.hyperledger.org/browse/INDY-869) |
| Corrected existing tests according to introduced prevention of upgrade to a lower version. |   | [INDY-895](https://jira.hyperledger.org/browse/INDY-895) [INDY-869](https://jira.hyperledger.org/browse/INDY-869) |
|   |   |   |   |

## 1.1.37
### Release date: Sep 26th, 2017


### Component Version Information

| Components | Version Numbers |
| --- | --- |
| indy-plenum | 1.1.27 |
| indy-anoncreds | 1.0.10 |
| indy-node | 1.1.37 |
|   |   | |

### Major Fixes

| Description | Additional Information | Ticket Number |
| --- | --- | --- |
| Stewards can now demote and promote their own nodes. |   | [INDY-410](https://jira.hyperledger.org/browse/INDY-410) |
| Fixed problem with timezones for timestamp in a transaction. |   | [INDY-466](https://jira.hyperledger.org/browse/INDY-466) |
| Limited incoming message size from 128k to 128MB (Temporary solution). |   | [INDY-25](https://jira.hyperledger.org/browse/INDY-25) |
| Fixed `send CLAIM_DEF` command. |   | [INDY-378](https://jira.hyperledger.org/browse/INDY-378) |
| Masked private information in the CLI logs/output. |   | [INDY-725](https://jira.hyperledger.org/browse/INDY-725) |
| Fixes crashes on ubuntu 17.04. |   | [INDY-8](https://jira.hyperledger.org/browse/INDY-8) |
| Python interpreter is executed in optimized mode. |   | [INDY-211](https://jira.hyperledger.org/browse/INDY-211) |
| Memory leak fixes. |   | [INDY-223](https://jira.hyperledger.org/browse/INDY-223) |
| Some minor stability fixes. |   |   |
| Fixed a problem with migration during manual upgrades. |   | [INDY-808](https://jira.hyperledger.org/browse/INDY-808) |
| Fixed a problem with the message length limitation. This was a permanent solution of [INDY-25](https://jira.hyperledger.org/browse/INDY-25). |   | [INDY-765](https://jira.hyperledger.org/browse/INDY-765) |
| Fixed a problem when the pool was writing transactions when more than F nodes were stopped. |   | [INDY -786](https://jira.hyperledger.org/browse/INDY-786) |
| Fixed a problem when the pool was broken after processing lots of transactions at once. |   | [INDY-760](https://jira.hyperledger.org/browse/INDY-760) |
| Fixed a problem when the pool doesn&#39;t come back to consensus in cases when less than n-f nodes are alive. |   | [INDY-804](https://jira.hyperledger.org/browse/INDY-804) |
| Partially fixed a problem when the pool responded with outdated data. |   | [INDY-761](https://jira.hyperledger.org/browse/INDY-761) |
|   |   |   | |

### Changes - Additions - Known Issues

| Description | Workaround | Ticket |
| --- | --- | --- |
| **New ledger serialization is supported and Leveldb is used as a storage for all ledgers** : msgpack is used for the ledger serialization (both transaction log and merkle tree). |   |   |
| **The new serialization change created changes to the directory structure for the nodes.** The directory name changes are located on a node under .sovrin/data/nodes/&lt;node name&gt;/&lt;directories&gt;. The change removes the ledger files as plain text files and creates them as binary files. A new tool was created to view the ledger entries called `read_ledger`. This tool also provides you with a count of the transactions. To learn more about this tool and to see a list of available commands, run this as the sovrin user: `read_ledger --h` | | |
| **Genesis transaction files are renamed adding a \_genesis to the end of each file name.** |   |   |
| **Added the commands to the POOL\_UPGRADE to support downgrade and re-installation.** However both have issues and should not be used at this time. |   | [INDY-735](https://jira.hyperledger.org/browse/INDY-735) [INDY-755](https://jira.hyperledger.org/browse/INDY-755) |
| **Fixes to upgrade procedure, in particular an issue which caused an infinite loop.** |   | [INDY-316](https://jira.hyperledger.org/browse/INDY-316) |
| **A new CLI command was added to ease the process of rotating a verification key (verkey).** The command is `change current key` or `change current key with seed xxxxx`. |   |   |
| **Improvements to log messages.** |   |   |
|  In your sources.list you only need the entry &quot;deb https://repo.evernym.com/deb xenial stable&quot;. |   |   |
| **Implemented a command line tool to provide validator status.** |   | [INDY-715](https://jira.hyperledger.org/browse/INDY-715) |
| **&quot;Debug&quot; mode for tests was moved to parameter.** |   | [INDY-716](https://jira.hyperledger.org/browse/INDY-716) |
| **Log levels were changed on some debug level messages to an info level.** |   | [INDY-800](https://jira.hyperledger.org/browse/INDY-800) |
| **If the pool loses enough nodes and cannot reach consensus when enough nodes become available, the pool will still not reach consensus.** | If you restart all the nodes in the pool, it will start reaching consensus again. | [INDY-849](https://jira.hyperledger.org/browse/INDY-849) |
