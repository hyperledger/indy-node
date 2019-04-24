# Current implemented rules in auth_map
<table class="tg">
  <tr>
    <th>Transaction type</th>
    <th>Field</th>
    <th>Previous value</th>
    <th>New value</th>
    <th>Who can</th>
    <th>Description</th>
  </tr>

  <tr>
    <td><sub>NYM</sub></td>
    <td><sub><code>role</code></sub></td>
    <td><sub><code>&lt;empty&gt;</code></sub></td>
    <td><sub>TRUSTEE</sub></td>
    <td><sub>TRUSTEE</sub></td>
    <td><sub>Adding new TRUSTEE</sub></td>
  </tr>
  <tr>
    <td><sub>NYM</sub></td>
    <td><sub><code>role</code></sub></td>
    <td><sub><code>&lt;empty&gt;</code></sub></td>
    <td><sub>STEWARD</sub></td>
    <td><sub>TRUSTEE</sub></td>
    <td><sub>Adding new STEWARD</sub></td>
  </tr>
  <tr>
    <td><sub>NYM</sub></td>
    <td><sub><code>role</code></sub></td>
    <td><sub><code>&lt;empty&gt;</code></sub></td>
    <td><sub>TRUST_ANCHOR</sub></td>
    <td><sub>TRUSTEE, STEWARD</sub></td>
    <td><sub>Adding new TRUST_ANCHOR</sub></td>
  </tr>
  <tr>
    <td><sub>NYM</sub></td>
    <td><sub><code>role</code></sub></td>
    <td><sub><code>&lt;empty&gt;</code></sub></td>
    <td><sub>NETWORK_MONITOR</sub></td>
    <td><sub>TRUSTEE, STEWARD</sub></td>
    <td><sub>Adding new NETWORK_MONITOR</sub></td>
  </tr>
  <tr>
    <td><sub>NYM</sub></td>
    <td><sub><code>role</code></sub></td>
    <td><sub><code>&lt;empty&gt;</code></sub></td>
    <td><sub><code>&lt;None&gt;</code></sub></td>
    <td><sub>TRUSTEE, STEWARD, TRUST_ANCHOR</sub></td>
    <td><sub>Adding new Identity Owner</sub></td>
  </tr>

  <tr>
    <td><sub>NYM</sub></td>
    <td><sub><code>role</code></sub></td>
    <td><sub>TRUSTEE</sub></td>
    <td><sub>STEWARD</sub></td>
    <td><sub>TRUSTEE</sub></td>
    <td><sub>Change Trustee to Steward</sub></td>
  </tr>
  <tr>
    <td><sub>NYM</sub></td>
    <td><sub><code>role</code></sub></td>
    <td><sub>TRUSTEE</sub></td>
    <td><sub>TRUST_ANCHOR</sub></td>
    <td><sub>TRUSTEE</sub></td>
    <td><sub>Change Trustee to Trust Anchor</sub></td>
  </tr>
  <tr>
    <td><sub>NYM</sub></td>
    <td><sub><code>role</code></sub></td>
    <td><sub>TRUSTEE</sub></td>
    <td><sub>NETWORK_MONITOR</sub></td>
    <td><sub>TRUSTEE</sub></td>
    <td><sub>Change Trustee to Network Monitor</sub></td>
  </tr>
  <tr>
    <td><sub>NYM</sub></td>
    <td><sub><code>role</code></sub></td>
    <td><sub>TRUSTEE</sub></td>
    <td><sub><code>&lt;None&gt;</code></sub></td>
    <td><sub>TRUSTEE</sub></td>
    <td><sub>Demote Trustee</sub></td>
  </tr>

  <tr>
    <td><sub>NYM</sub></td>
    <td><sub><code>role</code></sub></td>
    <td><sub>STEWARD</sub></td>
    <td><sub>TRUSTEE</sub></td>
    <td><sub>TRUSTEE</sub></td>
    <td><sub>Change Steward to Trustee</sub></td>
  </tr>
  <tr>
    <td><sub>NYM</sub></td>
    <td><sub><code>role</code></sub></td>
    <td><sub>STEWARD</sub></td>
    <td><sub>TRUST_ANCHOR</sub></td>
    <td><sub>TRUSTEE</sub></td>
    <td><sub>Change Steward to Trust Anchor</sub></td>
  </tr>
  <tr>
    <td><sub>NYM</sub></td>
    <td><sub><code>role</code></sub></td>
    <td><sub>STEWARD</sub></td>
    <td><sub>NETWORK_MONITOR</sub></td>
    <td><sub>TRUSTEE</sub></td>
    <td><sub>Change Steward to Network Monitor</sub></td>
  </tr>
  <tr>
    <td><sub>NYM</sub></td>
    <td><sub><code>role</code></sub></td>
    <td><sub>STEWARD</sub></td>
    <td><sub><code>&lt;None&gt;</code></sub></td>
    <td><sub>TRUSTEE</sub></td>
    <td><sub>Demote Steward</sub></td>
  </tr>

  <tr>
    <td><sub>NYM</sub></td>
    <td><sub><code>role</code></sub></td>
    <td><sub>TRUST_ANCHOR</sub></td>
    <td><sub>TRUSTEE</sub></td>
    <td><sub>TRUSTEE</sub></td>
    <td><sub>Change Trust Anchor to Trustee</sub></td>
  </tr>
  <tr>
    <td><sub>NYM</sub></td>
    <td><sub><code>role</code></sub></td>
    <td><sub>TRUST_ANCHOR</sub></td>
    <td><sub>STEWARD</sub></td>
    <td><sub>TRUSTEE</sub></td>
    <td><sub>Change Trust Anchor to Steward</sub></td>
  </tr>
  <tr>
    <td><sub>NYM</sub></td>
    <td><sub><code>role</code></sub></td>
    <td><sub>TRUST_ANCHOR</sub></td>
    <td><sub>NETWORK_MONITOR</sub></td>
    <td><sub>TRUSTEE</sub></td>
    <td><sub>Change Trust Anchor to Network Monitor</sub></td>
  </tr>
  <tr>
    <td><sub>NYM</sub></td>
    <td><sub><code>role</code></sub></td>
    <td><sub>TRUST_ANCHOR</sub></td>
    <td><sub><code>&lt;None&gt;</code></sub></td>
    <td><sub>TRUSTEE</sub></td>
    <td><sub>Demote Trust Anchor</sub></td>
  </tr>

  <tr>
    <td><sub>NYM</sub></td>
    <td><sub><code>role</code></sub></td>
    <td><sub>NETWORK_MONITOR</sub></td>
    <td><sub>TRUSTEE</sub></td>
    <td><sub>TRUSTEE</sub></td>
    <td><sub>Change Network Monitor to Trustee</sub></td>
  </tr>
  <tr>
    <td><sub>NYM</sub></td>
    <td><sub><code>role</code></sub></td>
    <td><sub>NETWORK_MONITOR</sub></td>
    <td><sub>STEWARD</sub></td>
    <td><sub>TRUSTEE</sub></td>
    <td><sub>Change Network Monitor to Steward</sub></td>
  </tr>
  <tr>
    <td><sub>NYM</sub></td>
    <td><sub><code>role</code></sub></td>
    <td><sub>NETWORK_MONITOR</sub></td>
    <td><sub>TRUST_ANCHOR</sub></td>
    <td><sub>TRUSTEE, STEWARD</sub></td>
    <td><sub>Change Network Monitor to Trust Anchor</sub></td>
  </tr>
  <tr>
    <td><sub>NYM</sub></td>
    <td><sub><code>role</code></sub></td>
    <td><sub>NETWORK_MONITOR</sub></td>
    <td><sub><code>&lt;None&gt;</code></sub></td>
    <td><sub>TRUSTEE, STEWARD</sub></td>
    <td><sub>Demote Network Monitor</sub></td>
  </tr>

  <tr>
    <td><sub>NYM</sub></td>
    <td><sub><code>role</code></sub></td>
    <td><sub><code>&lt;None&gt;</code></sub></td>
    <td><sub>TRUSTEE</sub></td>
    <td><sub>TRUSTEE</sub></td>
    <td><sub>Promote roleless user to Trustee</sub></td>
  </tr>
  <tr>
    <td><sub>NYM</sub></td>
    <td><sub><code>role</code></sub></td>
    <td><sub><code>&lt;None&gt;</code></sub></td>
    <td><sub>STEWARD</sub></td>
    <td><sub>TRUSTEE</sub></td>
    <td><sub>Promote roleless user to Steward</sub></td>
  </tr>
  <tr>
    <td><sub>NYM</sub></td>
    <td><sub><code>role</code></sub></td>
    <td><sub><code>&lt;None&gt;</code></sub></td>
    <td><sub>TRUST_ANCHOR</sub></td>
    <td><sub>TRUSTEE, STEWARD</sub></td>
    <td><sub>Promote roleless user to Trust Anchor</sub></td>
  </tr>
  <tr>
    <td><sub>NYM</sub></td>
    <td><sub><code>role</code></sub></td>
    <td><sub><code>&lt;None&gt;</code></sub></td>
    <td><sub>NETWORK_MONITOR</sub></td>
    <td><sub>TRUSTEE, STEWARD</sub></td>
    <td><sub>Promote roleless user to Network Monitor</sub></td>
  </tr>
  <tr>
    <td><sub>NYM</sub></td>
    <td><sub><code>verkey</code></sub></td>
    <td><sub><code>&lt;None&gt;</code></sub></td>
    <td><sub><code>*</code></sub></td>
    <td><sub>Guardian of this nym (who published it to the ledger)</sub></td>
    <td><sub>Assign Key to new DID</sub></td>
  </tr>
  <tr>
    <td><sub>NYM</sub></td>
    <td><sub><code>verkey</code></sub></td>
    <td><sub><code>*</code></sub></td>
    <td><sub><code>*</code></sub></td>
    <td><sub>Owner of this nym</sub></td>
    <td><sub>Key Rotation</sub></td>
  </tr>
  <tr>
    <td><sub>SCHEMA</sub></td>
    <td><sub><code>*</code></sub></td>
    <td><sub><code>*</code></sub></td>
    <td><sub><code>*</code></sub></td>
    <td><sub>TRUSTEE, STEWARD, TRUST_ANCHOR</sub></td>
    <td><sub>Adding new Schema</sub></td>
  </tr>
  <tr>
    <td><sub>SCHEMA</sub></td>
    <td><sub><code>*</code></sub></td>
    <td><sub><code>*</code></sub></td>
    <td><sub><code>*</code></sub></td>
    <td><sub>No one can edit existing Schema</sub></td>
    <td><sub>Editing Schema</sub></td>
  </tr>
  <tr>
    <td><sub>CLAIM_DEF</sub></td>
    <td><sub><code>*</code></sub></td>
    <td><sub><code>*</code></sub></td>
    <td><sub><code>*</code></sub></td>
    <td><sub>TRUSTEE, STEWARD, TRUST_ANCHOR</sub></td>
    <td><sub>Adding new CLAIM_DEF transaction</sub></td>
  </tr>
  <tr>
    <td><sub>CLAIM_DEF</sub></td>
    <td><sub><code>*</code></sub></td>
    <td><sub><code>*</code></sub></td>
    <td><sub><code>*</code></sub></td>
    <td><sub>Owner of claim_def txn</sub></td>
    <td><sub>Editing CLAIM_DEF transaction</sub></td>
  </tr>
  <tr>
    <td><sub>NODE</sub></td>
    <td><sub><code>services</code></sub></td>
    <td><sub><code>&lt;empty&gt;</code></sub></td>
    <td><sub><code>['VALIDATOR']</code></sub></td>
    <td><sub>STEWARD if it doesn't own NODE transaction yet</sub></td>
    <td><sub>Adding new node to pool</sub></td>
  </tr>
  <tr>
    <td><sub>NODE</sub></td>
    <td><sub><code>services</code></sub></td>
    <td><sub><code>&lt;empty&gt;</code></sub></td>
    <td><sub><code>[]</code></sub></td>
    <td><sub>STEWARD if it doesn't own NODE transaction yet</sub></td>
    <td><sub>Adding new node to pool with empty services</sub></td>
  </tr>
  <tr>
    <td><sub>NODE</sub></td>
    <td><sub><code>services</code></sub></td>
    <td><sub><code>['VALIDATOR']</code></sub></td>
    <td><sub><code>[]</code></sub></td>
    <td><sub>TRUSTEE, STEWARD if it is owner of this transaction</sub></td>
    <td><sub>Demotion of node</sub></td>
  </tr>
  <tr>
    <td><sub>NODE</sub></td>
    <td><sub><code>services</code></sub></td>
    <td><sub><code>[]</code></sub></td>
    <td><sub><code>['VALIDATOR']</code></sub></td>
    <td><sub>TRUSTEE, STEWARD if it is owner of this transaction</sub></td>
    <td><sub>Promotion of node</sub></td>
  </tr>
  <tr>
    <td><sub>NODE</sub></td>
    <td><sub><code>node_ip</code></sub></td>
    <td><sub><code>*</code></sub></td>
    <td><sub><code>*</code></sub></td>
    <td><sub>STEWARD if it is owner of this transaction</sub></td>
    <td><sub>Changing Node's ip address</sub></td>
  </tr>
  <tr>
    <td><sub>NODE</sub></td>
    <td><sub><code>node_port</code></sub></td>
    <td><sub><code>*</code></sub></td>
    <td><sub><code>*</code></sub></td>
    <td><sub>STEWARD if it is owner of this transaction</sub></td>
    <td><sub>Changing Node's port</sub></td>
  </tr>
  <tr>
    <td><sub>NODE</sub></td>
    <td><sub><code>client_ip</code></sub></td>
    <td><sub><code>*</code></sub></td>
    <td><sub><code>*</code></sub></td>
    <td><sub>STEWARD if it is owner of this transaction</sub></td>
    <td><sub>Changing Client's ip address</sub></td>
  </tr>
  <tr>
    <td><sub>NODE</sub></td>
    <td><sub><code>client_port</code></sub></td>
    <td><sub><code>*</code></sub></td>
    <td><sub><code>*</code></sub></td>
    <td><sub>STEWARD if it is owner of this transaction</sub></td>
    <td><sub>Changing Client's port</sub></td>
  </tr>
  <tr>
    <td><sub>NODE</sub></td>
    <td><sub><code>blskey</code></sub></td>
    <td><sub><code>*</code></sub></td>
    <td><sub><code>*</code></sub></td>
    <td><sub>STEWARD if it is owner of this transaction</sub></td>
    <td><sub>Changing Node's blskey</sub></td>
  </tr>
  <tr>
    <td><sub>POOL_UPGRADE</sub></td>
    <td><sub><code>action</code></sub></td>
    <td><sub><code>&lt;empty&gt;</code></sub></td>
    <td><sub><code>start</code></sub></td>
    <td><sub>TRUSTEE</sub></td>
    <td><sub>Starting upgrade procedure</sub></td>
  </tr>
  <tr>
    <td><sub>POOL_UPGRADE</sub></td>
    <td><sub><code>action</code></sub></td>
    <td><sub><code>start</code></sub></td>
    <td><sub><code>cancel</code></sub></td>
    <td><sub>TRUSTEE</sub></td>
    <td><sub>Canceling upgrade procedure</sub></td>
  </tr>
  <tr>
    <td><sub>POOL_RESTART</sub></td>
    <td><sub><code>action</code></sub></td>
    <td><sub><code>*</code></sub></td>
    <td><sub><code>*</code></sub></td>
    <td><sub>TRUSTEE</sub></td>
    <td><sub>Restarting pool command</sub></td>
  </tr>
  <tr>
    <td><sub>POOL_CONFIG</sub></td>
    <td><sub><code>action</code></sub></td>
    <td><sub><code>*</code></sub></td>
    <td><sub><code>*</code></sub></td>
    <td><sub>TRUSTEE</sub></td>
    <td><sub>Pool config command (like a <code>read only</code> option)</sub></td>
  </tr>
  <tr>
    <td><sub>AUTH_RULE</sub></td>
    <td><sub><code>*</code></sub></td>
    <td><sub><code>*</code></sub></td>
    <td><sub><code>*</code></sub></td>
    <td><sub>TRUSTEE</sub></td>
    <td><sub>Change authentification rules</sub></td>
  </tr>
  <tr>
    <td><sub>VALIDATOR_INFO</sub></td>
    <td><sub><code>*</code></sub></td>
    <td><sub><code>*</code></sub></td>
    <td><sub><code>*</code></sub></td>
    <td><sub>TRUSTEE, STEWARD, NETWORK_MONITOR</sub></td>
    <td><sub>Getting validator_info from pool</sub></td>
  </tr>
    <tr>
    <td><sub>REVOC_REG_DEF</sub></td>
    <td><sub><code>*</code></sub></td>
    <td><sub><code>*</code></sub></td>
    <td><sub><code>*</code></sub></td>
    <td><sub>TRUSTEE, STEWARD, TRUST_ANCHOR</sub></td>
    <td><sub>Adding new REVOC_REG_DEF</sub></td>
  </tr>
  <tr>
    <td><sub>REVOC_REG_DEF</sub></td>
    <td><sub><code>*</code></sub></td>
    <td><sub><code>*</code></sub></td>
    <td><sub><code>*</code></sub></td>
    <td><sub>Only owners can edit existing REVOC_REG_DEF</sub></td>
    <td><sub>Editing REVOC_REG_DEF</sub></td>
  </tr>
  <tr>
    <td><sub>REVOC_REG_ENTRY</sub></td>
    <td><sub><code>*</code></sub></td>
    <td><sub><code>*</code></sub></td>
    <td><sub><code>*</code></sub></td>
    <td><sub>Only the owner of the corresponding REVOC_REG_DEF can create new REVOC_REG_ENTRY</sub></td>
    <td><sub>Adding new REVOC_REG_ENTRY</sub></td>
  </tr>
  <tr>
    <td><sub>REVOC_REG_ENTRY</sub></td>
    <td><sub><code>*</code></sub></td>
    <td><sub><code>*</code></sub></td>
    <td><sub><code>*</code></sub></td>
    <td><sub>Only owners can edit existing REVOC_REG_ENTRY</sub></td>
    <td><sub>Editing REVOC_REG_ENTRY</sub></td>
  </tr>
</table>

### Also, there are optional rules for case of ANYONE_CAN_WRITE set to True in config file:
<table class="tg">
  <tr>
    <th>Transaction type</th>
    <th>Field</th>
    <th>Previous value</th>
    <th>New value</th>
    <th>Who can</th>
    <th>Description</th>
  </tr>
  <tr>
    <td><sub>NYM</sub></td>
    <td><sub><code>role</code></sub></td>
    <td><sub><code>&lt;empty&gt;</code></sub></td>
    <td><sub><code>&lt;empty&gt;</code></sub></td>
    <td><sub>Anyone</sub></td>
    <td><sub>Adding new nym</sub></td>
  </tr>
  <tr>
    <td><sub>SCHEMA</sub></td>
    <td><sub><code>*</code></sub></td>
    <td><sub><code>*</code></sub></td>
    <td><sub><code>*</code></sub></td>
    <td><sub>Anyone</sub></td>
    <td><sub>Any operations with SCHEMA transaction</sub></td>
  </tr>
  <tr>
    <td><sub>CLAIM_DEF</sub></td>
    <td><sub><code>*</code></sub></td>
    <td><sub><code>*</code></sub></td>
    <td><sub><code>*</code></sub></td>
    <td><sub>Anyone</sub></td>
    <td><sub>Any operations with CLAIM_DEF transaction</sub></td>
  </tr>
    <tr>
    <td><sub>REVOC_REG_DEF</sub></td>
    <td><sub><code>*</code></sub></td>
    <td><sub><code>*</code></sub></td>
    <td><sub><code>*</code></sub></td>
    <td><sub>Anyone can create new REVOC_REG_DEF</sub></td>
    <td><sub>Adding new REVOC_REG_DEF</sub></td>
  </tr>
  <tr>
    <td><sub>REVOC_REG_DEF</sub></td>
    <td><sub><code>*</code></sub></td>
    <td><sub><code>*</code></sub></td>
    <td><sub><code>*</code></sub></td>
    <td><sub>Only owners can edit existing REVOC_REG_DEF</sub></td>
    <td><sub>Editing REVOC_REG_DEF</sub></td>
  </tr>
  <tr>
    <td><sub>REVOC_REG_ENTRY</sub></td>
    <td><sub><code>*</code></sub></td>
    <td><sub><code>*</code></sub></td>
    <td><sub><code>*</code></sub></td>
    <td><sub>Only the owner of the corresponding REVOC_REG_DEF can create new REVOC_REG_ENTRY</sub></td>
    <td><sub>Adding new REVOC_REG_ENTRY</sub></td>
  </tr>
  <tr>
    <td><sub>REVOC_REG_ENTRY</sub></td>
    <td><sub><code>*</code></sub></td>
    <td><sub><code>*</code></sub></td>
    <td><sub><code>*</code></sub></td>
    <td><sub>Only owners can edit existing REVOC_REG_ENTRY</sub></td>
    <td><sub>Adding new REVOC_REG_ENTRY</sub></td>
  </tr>
</table>

