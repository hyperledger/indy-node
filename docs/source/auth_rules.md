# Default AUTH_MAP Rules
<table class="tg">
  <tr>
    <th>Transaction type</th>
    <th>Action</th>
    <th>Field</th>
    <th>Previous value</th>
    <th>New value</th>
    <th>Who can</th>
    <th>Description</th>
  </tr>

  <tr>
    <td><sub>NYM</sub></td>
    <td><sub>ADD</sub></td>
    <td><sub><code>role</code></sub></td>
    <td><sub><code>*</code></sub></td>
    <td><sub>TRUSTEE</sub></td>
    <td><sub>1 TRUSTEE</sub></td>
    <td><sub>Adding a new TRUSTEE</sub></td>
  </tr>
  <tr>
    <td><sub>NYM</sub></td>
    <td><sub>ADD</sub></td>
    <td><sub><code>role</code></sub></td>
    <td><sub><code>*</code></sub></td>
    <td><sub>STEWARD</sub></td>
    <td><sub>1 TRUSTEE</sub></td>
    <td><sub>Adding a new STEWARD</sub></td>
  </tr>
  <tr>
    <td><sub>NYM</sub></td>
    <td><sub>ADD</sub></td>
    <td><sub><code>role</code></sub></td>
    <td><sub><code>*</code></sub></td>
    <td><sub>ENDORSER</sub></td>
    <td><sub>1 TRUSTEE OR 1 STEWARD</sub></td>
    <td><sub>Adding a new ENDORSER</sub></td>
  </tr>
  <tr>
    <td><sub>NYM</sub></td>
    <td><sub>ADD</sub></td>
    <td><sub><code>role</code></sub></td>
    <td><sub><code>*</code></sub></td>
    <td><sub>NETWORK_MONITOR</sub></td>
    <td><sub>1 TRUSTEE OR 1 STEWARD</sub></td>
    <td><sub>Adding a new NETWORK_MONITOR</sub></td>
  </tr>
  <tr>
    <td><sub>NYM</sub></td>
    <td><sub>ADD</sub></td>
    <td><sub><code>role</code></sub></td>
    <td><sub><code>*</code></sub></td>
    <td><sub><code>&lt;None&gt;</code></sub></td>
    <td><sub>1 TRUSTEE OR 1 STEWARD OR 1 ENDORSER</sub></td>
    <td><sub>Adding a new Identity Owner</sub></td>
  </tr>

  <tr>
    <td><sub>NYM</sub></td>
    <td><sub>EDIT</sub></td>
    <td><sub><code>role</code></sub></td>
    <td><sub>TRUSTEE</sub></td>
    <td><sub>STEWARD</sub></td>
    <td><sub>1 TRUSTEE</sub></td>
    <td><sub>Changing Trustee to Steward</sub></td>
  </tr>
  <tr>
    <td><sub>NYM</sub></td>
    <td><sub>EDIT</sub></td>
    <td><sub><code>role</code></sub></td>
    <td><sub>TRUSTEE</sub></td>
    <td><sub>ENDORSER</sub></td>
    <td><sub>1 TRUSTEE</sub></td>
    <td><sub>Changing Trustee to Endorser</sub></td>
  </tr>
  <tr>
    <td><sub>NYM</sub></td>
    <td><sub>EDIT</sub></td>
    <td><sub><code>role</code></sub></td>
    <td><sub>TRUSTEE</sub></td>
    <td><sub>NETWORK_MONITOR</sub></td>
    <td><sub>1 TRUSTEE</sub></td>
    <td><sub>Changing Trustee to Network Monitor</sub></td>
  </tr>
  <tr>
    <td><sub>NYM</sub></td>
    <td><sub>EDIT</sub></td>
    <td><sub><code>role</code></sub></td>
    <td><sub>TRUSTEE</sub></td>
    <td><sub><code>&lt;None&gt;</code></sub></td>
    <td><sub>1 TRUSTEE</sub></td>
    <td><sub>Demoting a Trustee</sub></td>
  </tr>

  <tr>
    <td><sub>NYM</sub></td>
    <td><sub>EDIT</sub></td>
    <td><sub><code>role</code></sub></td>
    <td><sub>STEWARD</sub></td>
    <td><sub>TRUSTEE</sub></td>
    <td><sub>1 TRUSTEE</sub></td>
    <td><sub>Changing Steward to Trustee</sub></td>
  </tr>
  <tr>
    <td><sub>NYM</sub></td>
    <td><sub>EDIT</sub></td>
    <td><sub><code>role</code></sub></td>
    <td><sub>STEWARD</sub></td>
    <td><sub>ENDORSER</sub></td>
    <td><sub>1 TRUSTEE</sub></td>
    <td><sub>Changing Steward to Endorser</sub></td>
  </tr>
  <tr>
    <td><sub>NYM</sub></td>
    <td><sub>EDIT</sub></td>
    <td><sub><code>role</code></sub></td>
    <td><sub>STEWARD</sub></td>
    <td><sub>NETWORK_MONITOR</sub></td>
    <td><sub>1 TRUSTEE</sub></td>
    <td><sub>Changing Steward to Network Monitor</sub></td>
  </tr>
  <tr>
    <td><sub>NYM</sub></td>
    <td><sub>EDIT</sub></td>
    <td><sub><code>role</code></sub></td>
    <td><sub>STEWARD</sub></td>
    <td><sub><code>&lt;None&gt;</code></sub></td>
    <td><sub>1 TRUSTEE</sub></td>
    <td><sub>Demoting a Steward</sub></td>
  </tr>

  <tr>
    <td><sub>NYM</sub></td>
    <td><sub>EDIT</sub></td>
    <td><sub><code>role</code></sub></td>
    <td><sub>ENDORSER</sub></td>
    <td><sub>TRUSTEE</sub></td>
    <td><sub>1 TRUSTEE</sub></td>
    <td><sub>Changing Endorser to Trustee</sub></td>
  </tr>
  <tr>
    <td><sub>NYM</sub></td>
    <td><sub>EDIT</sub></td>
    <td><sub><code>role</code></sub></td>
    <td><sub>ENDORSER</sub></td>
    <td><sub>STEWARD</sub></td>
    <td><sub>1 TRUSTEE</sub></td>
    <td><sub>Changing Endorser to Steward</sub></td>
  </tr>
  <tr>
    <td><sub>NYM</sub></td>
    <td><sub>EDIT</sub></td>
    <td><sub><code>role</code></sub></td>
    <td><sub>ENDORSER</sub></td>
    <td><sub>NETWORK_MONITOR</sub></td>
    <td><sub>1 TRUSTEE</sub></td>
    <td><sub>Changing Endorser to Network Monitor</sub></td>
  </tr>
  <tr>
    <td><sub>NYM</sub></td>
    <td><sub>EDIT</sub></td>
    <td><sub><code>role</code></sub></td>
    <td><sub>ENDORSER</sub></td>
    <td><sub><code>&lt;None&gt;</code></sub></td>
    <td><sub>1 TRUSTEE</sub></td>
    <td><sub>Demoting a Endorser</sub></td>
  </tr>

  <tr>
    <td><sub>NYM</sub></td>
    <td><sub>EDIT</sub></td>
    <td><sub><code>role</code></sub></td>
    <td><sub>NETWORK_MONITOR</sub></td>
    <td><sub>TRUSTEE</sub></td>
    <td><sub>1 TRUSTEE</sub></td>
    <td><sub>Changing Network Monitor to Trustee</sub></td>
  </tr>
  <tr>
    <td><sub>NYM</sub></td>
    <td><sub>EDIT</sub></td>
    <td><sub><code>role</code></sub></td>
    <td><sub>NETWORK_MONITOR</sub></td>
    <td><sub>STEWARD</sub></td>
    <td><sub>1 TRUSTEE</sub></td>
    <td><sub>Changing Network Monitor to Steward</sub></td>
  </tr>
  <tr>
    <td><sub>NYM</sub></td>
    <td><sub>EDIT</sub></td>
    <td><sub><code>role</code></sub></td>
    <td><sub>NETWORK_MONITOR</sub></td>
    <td><sub>ENDORSER</sub></td>
    <td><sub>1 TRUSTEE OR 1 STEWARD</sub></td>
    <td><sub>Changing Network Monitor to Endorser</sub></td>
  </tr>
  <tr>
    <td><sub>NYM</sub></td>
    <td><sub>EDIT</sub></td>
    <td><sub><code>role</code></sub></td>
    <td><sub>NETWORK_MONITOR</sub></td>
    <td><sub><code>&lt;None&gt;</code></sub></td>
    <td><sub>1 TRUSTEE OR 1 STEWARD</sub></td>
    <td><sub>Demoting a Network Monitor</sub></td>
  </tr>

  <tr>
    <td><sub>NYM</sub></td>
    <td><sub>EDIT</sub></td>
    <td><sub><code>role</code></sub></td>
    <td><sub><code>&lt;None&gt;</code></sub></td>
    <td><sub>TRUSTEE</sub></td>
    <td><sub>1 TRUSTEE</sub></td>
    <td><sub>Promoting Identity Owner to Trustee</sub></td>
  </tr>
  <tr>
    <td><sub>NYM</sub></td>
    <td><sub>EDIT</sub></td>
    <td><sub><code>role</code></sub></td>
    <td><sub><code>&lt;None&gt;</code></sub></td>
    <td><sub>STEWARD</sub></td>
    <td><sub>1 TRUSTEE</sub></td>
    <td><sub>Promoting Identity Owner to Steward</sub></td>
  </tr>
  <tr>
    <td><sub>NYM</sub></td>
    <td><sub>EDIT</sub></td>
    <td><sub><code>role</code></sub></td>
    <td><sub><code>&lt;None&gt;</code></sub></td>
    <td><sub>ENDORSER</sub></td>
    <td><sub>1 TRUSTEE OR 1 STEWARD</sub></td>
    <td><sub>Promoting Identity Owner to Endorser</sub></td>
  </tr>
  <tr>
    <td><sub>NYM</sub></td>
    <td><sub>EDIT</sub></td>
    <td><sub><code>role</code></sub></td>
    <td><sub><code>&lt;None&gt;</code></sub></td>
    <td><sub>NETWORK_MONITOR</sub></td>
    <td><sub>1 TRUSTEE OR 1 STEWARD</sub></td>
    <td><sub>Promoting Identity Owner to Network Monitor</sub></td>
  </tr>
  <tr>
    <td><sub>NYM</sub></td>
    <td><sub>EDIT</sub></td>
    <td><sub><code>verkey</code></sub></td>
    <td><sub><code>*</code></sub></td>
    <td><sub><code>*</code></sub></td>
    <td><sub>1 any (*) role owner</sub></td>
    <td><sub>Rotation the key or assigning a key to a DID under guardianship</sub></td>
  </tr>
  <tr>
    <td><sub>ATTRIB</sub></td>
    <td><sub>ADD</sub></td>
    <td><sub><code>*</code></sub></td>
    <td><sub><code>*</code></sub></td>
    <td><sub><code>*</code></sub></td>
    <td><sub>1 any (*) role owner of the corresponding NYM</sub></td>
    <td><sub>Adding a new ATTRIB for the NYM</sub></td>
  </tr>
  <tr>
    <td><sub>ATTRIB</sub></td>
    <td><sub>EDIT</sub></td>
    <td><sub><code>*</code></sub></td>
    <td><sub><code>*</code></sub></td>
    <td><sub><code>*</code></sub></td>
    <td><sub>1 any (*) role owner of the corresponding NYM</sub></td>
    <td><sub>Editing an ATTRIB for the NYM</sub></td>
  </tr>
  <tr>
    <td><sub>SCHEMA</sub></td>
    <td><sub>ADD</sub></td>
    <td><sub><code>*</code></sub></td>
    <td><sub><code>*</code></sub></td>
    <td><sub><code>*</code></sub></td>
    <td><sub>1 TRUSTEE OR 1 STEWARD OR 1 ENDORSER</sub></td>
    <td><sub>Adding a new Schema</sub></td>
  </tr>
  <tr>
    <td><sub>SCHEMA</sub></td>
    <td><sub>EDIT</sub></td>
    <td><sub><code>*</code></sub></td>
    <td><sub><code>*</code></sub></td>
    <td><sub><code>*</code></sub></td>
    <td><sub>No one can edit existing Schema</sub></td>
    <td><sub>Editing a Schema</sub></td>
  </tr>
  <tr>
    <td><sub>SET_CONTEXT</sub></td>
    <td><sub>ADD</sub></td>
    <td><sub><code>*</code></sub></td>
    <td><sub><code>*</code></sub></td>
    <td><sub><code>*</code></sub></td>
    <td><sub>1 TRUSTEE OR 1 STEWARD OR 1 ENDORSER</sub></td>
    <td><sub>Adding a new Context</sub></td>
  </tr>
  <tr>
    <td><sub>SET_CONTEXT</sub></td>
    <td><sub>EDIT</sub></td>
    <td><sub><code>*</code></sub></td>
    <td><sub><code>*</code></sub></td>
    <td><sub><code>*</code></sub></td>
    <td><sub>No one can edit existing Context</sub></td>
    <td><sub>Editing a Context</sub></td>
  </tr>
  <tr>
    <td><sub>CLAIM_DEF</sub></td>
    <td><sub>ADD</sub></td>
    <td><sub><code>*</code></sub></td>
    <td><sub><code>*</code></sub></td>
    <td><sub><code>*</code></sub></td>
    <td><sub>1 TRUSTEE OR 1 STEWARD OR 1 ENDORSER</sub></td>
    <td><sub>Adding a new CLAIM_DEF</sub></td>
  </tr>
  <tr>
    <td><sub>CLAIM_DEF</sub></td>
    <td><sub>EDIT</sub></td>
    <td><sub><code>*</code></sub></td>
    <td><sub><code>*</code></sub></td>
    <td><sub><code>*</code></sub></td>
    <td><sub>1 owner TRUSTEE OR 1 owner STEWARD OR 1 owner ENDORSER</sub></td>
    <td><sub>Editing a CLAIM_DEF: INDY-2078 - can not be configured by auth rule; ADD CLAIM_DEF rule is currently used for editing where owner is always true as it's part of the primary key</sub></td>
  </tr>
    <tr>
    <td><sub>REVOC_REG_DEF</sub></td>
    <td><sub>ADD</sub></td>
    <td><sub><code>*</code></sub></td>
    <td><sub><code>*</code></sub></td>
    <td><sub><code>*</code></sub></td>
    <td><sub>1 TRUSTEE OR 1 STEWARD OR 1 ENDORSER</sub></td>
    <td><sub>Adding a new REVOC_REG_DEF</sub></td>
  </tr>
  <tr>
    <td><sub>REVOC_REG_DEF</sub></td>
    <td><sub>EDIT</sub></td>
    <td><sub><code>*</code></sub></td>
    <td><sub><code>*</code></sub></td>
    <td><sub><code>*</code></sub></td>
    <td><sub>1 any (*) role owner</sub></td>
    <td><sub>Editing a REVOC_REG_DEF</sub></td>
  </tr>
  <tr>
    <td><sub>REVOC_REG_ENTRY</sub></td>
    <td><sub>ADD</sub></td>
    <td><sub><code>*</code></sub></td>
    <td><sub><code>*</code></sub></td>
    <td><sub><code>*</code></sub></td>
    <td><sub>1 any (*) role owner of the corresponding REVOC_REG_DEF</sub></td>
    <td><sub>Adding a new REVOC_REG_ENTRY</sub></td>
  </tr>
  <tr>
    <td><sub>REVOC_REG_ENTRY</sub></td>
    <td><sub>EDIT</sub></td>
    <td><sub><code>*</code></sub></td>
    <td><sub><code>*</code></sub></td>
    <td><sub><code>*</code></sub></td>
    <td><sub>1 any (*) role owner</sub></td>
    <td><sub>Editing a REVOC_REG_ENTRY</sub></td>
  </tr>  
  <tr>
    <td><sub>NODE</sub></td>
    <td><sub>ADD</sub></td>
    <td><sub><code>services</code></sub></td>
    <td><sub><code>*</code></sub></td>
    <td><sub><code>['VALIDATOR']</code></sub></td>
    <td><sub>1 STEWARD (if it doesn't own NODE transaction yet)</sub></td>
    <td><sub>Adding a new node to the pool in the active (Validator) state</sub></td>
  </tr>
  <tr>
    <td><sub>NODE</sub></td>
    <td><sub>ADD</sub></td>
    <td><sub><code>services</code></sub></td>
    <td><sub><code>*</code></sub></td>
    <td><sub><code>[]</code></sub></td>
    <td><sub>1 STEWARD if it doesn't own NODE transaction yet</sub></td>
    <td><sub>Adding a new node to the pool in inactive state</sub></td>
  </tr>
  <tr>
    <td><sub>NODE</sub></td>
    <td><sub>EDIT</sub></td>
    <td><sub><code>services</code></sub></td>
    <td><sub><code>['VALIDATOR']</code></sub></td>
    <td><sub><code>[]</code></sub></td>
    <td><sub>1 TRUSTEE OR 1 owner STEWARD</sub></td>
    <td><sub>Demoting a node</sub></td>
  </tr>
  <tr>
    <td><sub>NODE</sub></td>
    <td><sub>EDIT</sub></td>
    <td><sub><code>services</code></sub></td>
    <td><sub><code>[]</code></sub></td>
    <td><sub><code>['VALIDATOR']</code></sub></td>
    <td><sub>1 TRUSTEE or 1 owner STEWARD</sub></td>
    <td><sub>Promoting a node</sub></td>
  </tr>
  <tr>
    <td><sub>NODE</sub></td>
    <td><sub>EDIT</sub></td>
    <td><sub><code>node_ip</code></sub></td>
    <td><sub><code>*</code></sub></td>
    <td><sub><code>*</code></sub></td>
    <td><sub>1 owner STEWARD</sub></td>
    <td><sub>Changing Node's ip address</sub></td>
  </tr>
  <tr>
    <td><sub>NODE</sub></td>
    <td><sub>EDIT</sub></td>
    <td><sub><code>node_port</code></sub></td>
    <td><sub><code>*</code></sub></td>
    <td><sub><code>*</code></sub></td>
    <td><sub>1 owner STEWARD</sub></td>
    <td><sub>Changing Node's port</sub></td>
  </tr>
  <tr>
    <td><sub>NODE</sub></td>
    <td><sub>EDIT</sub></td>
    <td><sub><code>client_ip</code></sub></td>
    <td><sub><code>*</code></sub></td>
    <td><sub><code>*</code></sub></td>
    <td><sub>1 owner STEWARD</sub></td>
    <td><sub>Changing Client's ip address</sub></td>
  </tr>
  <tr>
    <td><sub>NODE</sub></td>
    <td><sub>EDIT</sub></td>
    <td><sub><code>client_port</code></sub></td>
    <td><sub><code>*</code></sub></td>
    <td><sub><code>*</code></sub></td>
    <td><sub>1 owner STEWARD</sub></td>
    <td><sub>Changing Client's port</sub></td>
  </tr>
  <tr>
    <td><sub>NODE</sub></td>
    <td><sub>EDIT</sub></td>
    <td><sub><code>blskey</code></sub></td>
    <td><sub><code>*</code></sub></td>
    <td><sub><code>*</code></sub></td>
    <td><sub>1 owner STEWARD</sub></td>
    <td><sub>Changing Node's blskey</sub></td>
  </tr>
  <tr>
    <td><sub>POOL_UPGRADE</sub></td>
    <td><sub>ADD</sub></td>
    <td><sub><code>action</code></sub></td>
    <td><sub><code>*</code></sub></td>
    <td><sub><code>start</code></sub></td>
    <td><sub>1 TRUSTEE</sub></td>
    <td><sub>Starting upgrade procedure</sub></td>
  </tr>
  <tr>
    <td><sub>POOL_UPGRADE</sub></td>
    <td><sub>EDIT</sub></td>
    <td><sub><code>action</code></sub></td>
    <td><sub><code>start</code></sub></td>
    <td><sub><code>cancel</code></sub></td>
    <td><sub>1 TRUSTEE</sub></td>
    <td><sub>Canceling upgrade procedure</sub></td>
  </tr>
  <tr>
    <td><sub>POOL_RESTART</sub></td>
    <td><sub>ADD</sub></td>
    <td><sub><code>action</code></sub></td>
    <td><sub><code>*</code></sub></td>
    <td><sub><code>*</code></sub></td>
    <td><sub>1 TRUSTEE</sub></td>
    <td><sub>Restarting the whole pool</sub></td>
  </tr>
  <tr>
    <td><sub>POOL_CONFIG</sub></td>
    <td><sub>EDIT</sub></td>
    <td><sub><code>action</code></sub></td>
    <td><sub><code>*</code></sub></td>
    <td><sub><code>*</code></sub></td>
    <td><sub>1 TRUSTEE</sub></td>
    <td><sub>Changing Pool config (for example, putting the pool into <code>read only</code> state)</sub></td>
  </tr>
  <tr>
    <td><sub>AUTH_RULE</sub></td>
    <td><sub>EDIT</sub></td>
    <td><sub><code>*</code></sub></td>
    <td><sub><code>*</code></sub></td>
    <td><sub><code>*</code></sub></td>
    <td><sub>1 TRUSTEE</sub></td>
    <td><sub>Changing an authentification rule</sub></td>
  </tr>
  <tr>
    <td><sub>AUTH_RULES</sub></td>
    <td><sub>EDIT</sub></td>
    <td><sub><code>*</code></sub></td>
    <td><sub><code>*</code></sub></td>
    <td><sub><code>*</code></sub></td>
    <td><sub>1 TRUSTEE</sub></td>
    <td><sub>Changing a number of authentification rules</sub></td>
  </tr>
  <tr>
    <td><sub>TRANSACTION_AUTHOR_AGREEMENT</sub></td>
    <td><sub>ADD</sub></td>
    <td><sub><code>*</code></sub></td>
    <td><sub><code>*</code></sub></td>
    <td><sub><code>*</code></sub></td>
    <td><sub>1 TRUSTEE</sub></td>
    <td><sub>Adding a new Transaction Author Agreement</sub></td>
  </tr>    
  <tr>
    <td><sub>TRANSACTION_AUTHOR_AGREEMENT_AML</sub></td>
    <td><sub>ADD</sub></td>
    <td><sub><code>*</code></sub></td>
    <td><sub><code>*</code></sub></td>
    <td><sub><code>*</code></sub></td>
    <td><sub>1 TRUSTEE</sub></td>
    <td><sub>Adding a new Transaction Author Agreement Mechanism List</sub></td>
  </tr>      
  <tr>
    <td><sub>VALIDATOR_INFO</sub></td>
    <td><sub>ADD</sub></td>
    <td><sub><code>*</code></sub></td>
    <td><sub><code>*</code></sub></td>
    <td><sub><code>*</code></sub></td>
    <td><sub>1 TRUSTEE OR 1 STEWARD OR 1 NETWORK_MONITOR</sub></td>
    <td><sub>Getting validator_info from pool</sub></td>
  </tr>
</table>


### Who Is Owner

<table class="tg">
  <tr>
    <th>Transaction Type</th>
    <th>Action</th>
    <th>Who is Owner</th>
  </tr>
  
  <tr>
    <td><sub>NYM</sub></td>
    <td><sub>ADD</sub></td>
    <td><sub>N/A</sub></td>
  </tr>

  <tr>
    <td><sub>NYM</sub></td>
    <td><sub>EDIT</sub></td>
    <td><sub>The DID defined by the NYM txn (`dest` field) if `verkey` is set; otherwise the submitter of the NYM txn (`identifier` field)</sub></td>
  </tr>
  
  <tr>
    <td><sub>ATTRIB</sub></td>
    <td><sub>ADD</sub></td>
    <td><sub>The owner of the DID (`dest` field) the ATTRIB is created for (see NYM's owner description)</sub></td>
  </tr>  

  <tr>
    <td><sub>ATTRIB</sub></td>
    <td><sub>EDIT</sub></td>
    <td><sub>The owner of the DID (`dest` field) the ATTRIB is created for (see NYM's owner description)</sub></td>
  </tr>
  
  <tr>
    <td><sub>SCHEMA</sub></td>
    <td><sub>ADD</sub></td>
    <td><sub>N/A</sub></td>
  </tr>    

  <tr>
    <td><sub>SCHEMA</sub></td>
    <td><sub>EDIT</sub></td>
    <td><sub>The DID used to create the SCHEMA</sub></td>
  </tr>    
  
  <tr>
    <td><sub>SET_CONTEXT</sub></td>
    <td><sub>ADD</sub></td>
    <td><sub>N/A</sub></td>
  </tr>    

  <tr>
    <td><sub>SET_CONTEXT</sub></td>
    <td><sub>EDIT</sub></td>
    <td><sub>The DID used to create the CONTEXT</sub></td>
  </tr>  

  <tr>
    <td><sub>CLAIM_DEF</sub></td>
    <td><sub>ADD</sub></td>
    <td><sub>N/A</sub></td>
  </tr>    

  <tr>
    <td><sub>CLAIM_DEF</sub></td>
    <td><sub>EDIT</sub></td>
    <td><sub>The DID used to create the CLAIM_DEF</sub></td>
  </tr>  
  
  <tr>
    <td><sub>REVOC_REG_DEF</sub></td>
    <td><sub>ADD</sub></td>
    <td><sub>N/A</sub></td>
  </tr>    

  <tr>
    <td><sub>REVOC_REG_DEF</sub></td>
    <td><sub>EDIT</sub></td>
    <td><sub>The DID used to create the REVOC_REG_DEF</sub></td>
  </tr>    
  
  <tr>
    <td><sub>REVOC_REG_ENTRY</sub></td>
    <td><sub>ADD</sub></td>
    <td><sub>The DID used to create the corresponding REVOC_REG_DEF</sub></td>
  </tr>    

  <tr>
    <td><sub>REVOC_REG_ENTRY</sub></td>
    <td><sub>EDIT</sub></td>
    <td><sub>The DID used to create the REVOC_REG_ENTRY</sub></td>
  </tr>     
  
  <tr>
    <td><sub>NODE</sub></td>
    <td><sub>ADD</sub></td>
    <td><sub>N/A</sub></td>
  </tr>    

  <tr>
    <td><sub>NODE</sub></td>
    <td><sub>EDIT</sub></td>
    <td><sub>The Steward's DID used to create the NODE</sub></td>
  </tr>      
  
  <tr>
    <td><sub>POOL_UPGRADE</sub></td>
    <td><sub>ADD</sub></td>
    <td><sub>N/A</sub></td>
  </tr>    

  <tr>
    <td><sub>POOL_UPGRADE</sub></td>
    <td><sub>EDIT</sub></td>
    <td><sub>N/A</sub></td>
  </tr>     
  
  <tr>
    <td><sub>POOL_RESTART</sub></td>
    <td><sub>ADD</sub></td>
    <td><sub>N/A</sub></td>
  </tr>    

  <tr>
    <td><sub>POOL_RESTART</sub></td>
    <td><sub>EDIT</sub></td>
    <td><sub>N/A</sub></td>
  </tr>     
  
  <tr>
    <td><sub>POOL_CONFIG</sub></td>
    <td><sub>ADD</sub></td>
    <td><sub>N/A</sub></td>
  </tr>    

  <tr>
    <td><sub>POOL_CONFIG</sub></td>
    <td><sub>EDIT</sub></td>
    <td><sub>N/A</sub></td>
  </tr>      
  
  <tr>
    <td><sub>GET_VALIDATOR_INFO</sub></td>
    <td><sub>ADD</sub></td>
    <td><sub>N/A</sub></td>
  </tr>    

  <tr>
    <td><sub>GET_VALIDATOR_INFO</sub></td>
    <td><sub>EDIT</sub></td>
    <td><sub>N/A</sub></td>
  </tr>    
  
  <tr>
    <td><sub>AUTH_RULE</sub></td>
    <td><sub>ADD</sub></td>
    <td><sub>N/A</sub></td>
  </tr>    

  <tr>
    <td><sub>AUTH_RULE</sub></td>
    <td><sub>EDIT</sub></td>
    <td><sub>N/A</sub></td>
  </tr>      
  
  <tr>
    <td><sub>TRANSACTION_AUTHOR_AGREEMENT</sub></td>
    <td><sub>ADD</sub></td>
    <td><sub>N/A</sub></td>
  </tr>    

  <tr>
    <td><sub>TRANSACTION_AUTHOR_AGREEMENT_AML</sub></td>
    <td><sub>ADD</sub></td>
    <td><sub>N/A</sub></td>
  </tr>    

        
</table>

### Endorser using

- Endorser is required only when the transaction is endorsed, that is signed by someone else besides the author.
- If transaction is endorsed, Endorser must sign the transaction.
- If author of txn has role `ENDORSER`, then no multi-sig is required, since he's already signed the txn.
- Endorser is required for unprivileged roles only.
- Unprivileged users cannot submit any transaction (including administrative transactions like pool upgrade or restart) without a signature from a DID with the endorser role that is specified in the endorser field.
