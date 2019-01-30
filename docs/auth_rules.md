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
    <td><sub>role</sub></td>
    <td><sub>&lt;empty&gt;</sub></td>
    <td><sub>TRUSTEE</sub></td>
    <td><sub>TRUSTEE</sub></td>
    <td><sub>Adding new TRUSTEE</sub></td>
  </tr>
  <tr>
    <td><sub>NYM</sub></td>
    <td><sub>role</sub></td>
    <td><sub>&lt;empty&gt;</sub></td>
    <td><sub>STEWARD</sub></td>
    <td><sub>TRUSTEE</sub></td>
    <td><sub>Adding new STEWARD</sub></td>
  </tr>
  <tr>
    <td><sub>NYM</sub></td>
    <td><sub>role</sub></td>
    <td><sub>&lt;empty&gt;</sub></td>
    <td><sub>TRUST_ANCHOR</sub></td>
    <td><sub>TRUSTEE, STEWARD</sub></td>
    <td><sub>Adding new TRUST_ANCHOR</sub></td>
  </tr>
  <tr>
    <td><sub>NYM</sub></td>
    <td><sub>role</sub></td>
    <td><sub>&lt;empty&gt;</sub></td>
    <td><sub>NETWORK_MONITOR</sub></td>
    <td><sub>TRUSTEE, STEWARD</sub></td>
    <td><sub>Adding new NETWORK_MONITOR</sub></td>
  </tr>
  <tr>
    <td><sub>NYM</sub></td>
    <td><sub>role</sub></td>
    <td><sub>&lt;empty&gt;</sub></td>
    <td><sub>&lt;empty&gt;</sub></td>
    <td><sub>TRUSTEE, STEWARD, TRUST_ANCHOR</sub></td>
    <td><sub>Adding new Identity Owner</sub></td>
  </tr>
  <tr>
    <td><sub>NYM</sub></td>
    <td><sub>role</sub></td>
    <td><sub>TRUSTEE</sub></td>
    <td><sub>&lt;empty&gt;</sub></td>
    <td><sub>TRUSTEE</sub></td>
    <td><sub>Blacklisting Trustee</sub></td>
  </tr>
  <tr>
    <td><sub>NYM</sub></td>
    <td><sub>role</sub></td>
    <td><sub>STEWARD</sub></td>
    <td><sub>&lt;empty&gt;</sub></td>
    <td><sub>TRUSTEE</sub></td>
    <td><sub>Blacklisting Steward</sub></td>
  </tr>
  <tr>
    <td><sub>NYM</sub></td>
    <td><sub>role</sub></td>
    <td><sub>TRUST_ANCHOR</sub></td>
    <td><sub>&lt;empty&gt;</sub></td>
    <td><sub>TRUSTEE</sub></td>
    <td><sub>Blacklisting Trust anchor</sub></td>
  </tr>
  <tr>
    <td><sub>NYM</sub></td>
    <td><sub>role</sub></td>
    <td><sub>NETWORK_MONITOR</sub></td>
    <td><sub>&lt;empty&gt;</sub></td>
    <td><sub>TRUSTEE, STEWARD</sub></td>
    <td><sub>Blacklisting user with NETWORK_MONITOR role</sub></td>
  </tr>
  <tr>
    <td><sub>NYM</sub></td>
    <td><sub>verkey</sub></td>
    <td><sub>*</sub></td>
    <td><sub>*</sub></td>
    <td><sub>Owner of this nym</sub></td>
    <td><sub>Key Rotation</sub></td>
  </tr>
  <tr>
    <td><sub>SCHEMA</sub></td>
    <td><sub>*</sub></td>
    <td><sub>*</sub></td>
    <td><sub>*</sub></td>
    <td><sub>TRUSTEE, STEWARD, TRUST_ANCHOR</sub></td>
    <td><sub>Adding new Schema</sub></td>
  </tr>
  <tr>
    <td><sub>SCHEMA</sub></td>
    <td><sub>*</sub></td>
    <td><sub>*</sub></td>
    <td><sub>*</sub></td>
    <td><sub>No one can edit existing Schema</sub></td>
    <td><sub>Editing Schema</sub></td>
  </tr>
  <tr>
    <td><sub>CLAIM_DEF</sub></td>
    <td><sub>*</sub></td>
    <td><sub>*</sub></td>
    <td><sub>*</sub></td>
    <td><sub>TRUSTEE, STEWARD, TRUST_ANCHOR</sub></td>
    <td><sub>Adding new CLAIM_DEF transaction</sub></td>
  </tr>
  <tr>
    <td><sub>CLAIM_DEF</sub></td>
    <td><sub>*</sub></td>
    <td><sub>*</sub></td>
    <td><sub>*</sub></td>
    <td><sub>Owner of claim_def txn</sub></td>
    <td><sub>Editing CLAIM_DEF transaction</sub></td>
  </tr>
  <tr>
    <td><sub>NODE</sub></td>
    <td><sub>services</sub></td>
    <td><sub>&lt;empty&gt;</sub></td>
    <td><sub>[VALIDATOR]</sub></td>
    <td><sub>STEWARD if it doesn't own NODE transaction yet</sub></td>
    <td><sub>Adding new node to pool</sub></td>
  </tr>
  <tr>
    <td><sub>NODE</sub></td>
    <td><sub>services</sub></td>
    <td><sub>[VALIDATOR]</sub></td>
    <td><sub>[]</sub></td>
    <td><sub>TRUSTEE, STEWARD if it is owner of this transaction</sub></td>
    <td><sub>Demotion of node</sub></td>
  </tr>
  <tr>
    <td><sub>NODE</sub></td>
    <td><sub>services</sub></td>
    <td><sub>[]</sub></td>
    <td><sub>[VALIDATOR]</sub></td>
    <td><sub>TRUSTEE, STEWARD if it is owner of this transaction</sub></td>
    <td><sub>Promotion of node</sub></td>
  </tr>
  <tr>
    <td><sub>NODE</sub></td>
    <td><sub>node_ip</sub></td>
    <td><sub>*</sub></td>
    <td><sub>*</sub></td>
    <td><sub>STEWARD if it is owner of this transaction</sub></td>
    <td><sub>Changing Node's ip address</sub></td>
  </tr>
  <tr>
    <td><sub>NODE</sub></td>
    <td><sub>node_port</sub></td>
    <td><sub>*</sub></td>
    <td><sub>*</sub></td>
    <td><sub>STEWARD if it is owner of this transaction</sub></td>
    <td><sub>Changing Node's port</sub></td>
  </tr>
  <tr>
    <td><sub>NODE</sub></td>
    <td><sub>client_ip</sub></td>
    <td><sub>*</sub></td>
    <td><sub>*</sub></td>
    <td><sub>STEWARD if it is owner of this transaction</sub></td>
    <td><sub>Changing Client's ip address</sub></td>
  </tr>
  <tr>
    <td><sub>NODE</sub></td>
    <td><sub>client_port</sub></td>
    <td><sub>*</sub></td>
    <td><sub>*</sub></td>
    <td><sub>STEWARD if it is owner of this transaction</sub></td>
    <td><sub>Changing Client's port</sub></td>
  </tr>
  <tr>
    <td><sub>NODE</sub></td>
    <td><sub>blskey</sub></td>
    <td><sub>*</sub></td>
    <td><sub>*</sub></td>
    <td><sub>STEWARD if it is owner of this transaction</sub></td>
    <td><sub>Changing Node's blskey</sub></td>
  </tr>
  <tr>
    <td><sub>POOL_UPGRADE</sub></td>
    <td><sub>action</sub></td>
    <td><sub>&lt;empty&gt;</sub></td>
    <td><sub>start</sub></td>
    <td><sub>TRUSTEE</sub></td>
    <td><sub>Starting upgrade procedure</sub></td>
  </tr>
  <tr>
    <td><sub>POOL_UPGRADE</sub></td>
    <td><sub>action</sub></td>
    <td><sub>start</sub></td>
    <td><sub>cancel</sub></td>
    <td><sub>TRUSTEE</sub></td>
    <td><sub>Canceling upgrade procedure</sub></td>
  </tr>
  <tr>
    <td><sub>POOL_RESTART</sub></td>
    <td><sub>action</sub></td>
    <td><sub>*</sub></td>
    <td><sub>*</sub></td>
    <td><sub>TRUSTEE</sub></td>
    <td><sub>Restarting pool command</sub></td>
  </tr>
  <tr>
    <td><sub>POOL_CONFIG</sub></td>
    <td><sub>action</sub></td>
    <td><sub>*</sub></td>
    <td><sub>*</sub></td>
    <td><sub>TRUSTEE</sub></td>
    <td><sub>Pool config command (like a read only option)</sub></td>
  </tr>
  <tr>
    <td><sub>VALIDATOR_INFO</sub></td>
    <td><sub>*</sub></td>
    <td><sub>*</sub></td>
    <td><sub>*</sub></td>
    <td><sub>TRUSTEE, STEWARD, NETWORK_MONITOR</sub></td>
    <td><sub>Getting validator_info from pool</sub></td>
  </tr>
</table>

### Also, there is a some optional rules for case if in config option ANYONE_CAN_WRITE is set to True:
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
    <td><sub>role</sub></td>
    <td><sub>&lt;empty&gt;</sub></td>
    <td><sub>&lt;empty&gt;</sub></td>
    <td><sub>Anyone</sub></td>
    <td><sub>Adding new nym</sub></td>
  </tr>
  <tr>
    <td><sub>SCHEMA</sub></td>
    <td><sub>*</sub></td>
    <td><sub>*</sub></td>
    <td><sub>*</sub></td>
    <td><sub>Anyone</sub></td>
    <td><sub>Any operations with SCHEMA transaction</sub></td>
  </tr>
  <tr>
    <td><sub>CLAIM_DEF</sub></td>
    <td><sub>*</sub></td>
    <td><sub>*</sub></td>
    <td><sub>*</sub></td>
    <td><sub>Anyone</sub></td>
    <td><sub>Any operations with CLAIM_DEF transaction</sub></td>
  </tr>
</table>


### As of now it's not implemented yet, but the next rules for Revocation feature are needed:
#### If ANYONE_CAN_WRITE is set to False:
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
    <td><sub>REVOC_REG_DEF</sub></td>
    <td><sub>*</sub></td>
    <td><sub>*</sub></td>
    <td><sub>*</sub></td>
    <td><sub>TRUSTEE, STEWARD, TRUST_ANCHOR</sub></td>
    <td><sub>Adding new REVOC_REG_DEF</sub></td>
  </tr>
  <tr>
    <td><sub>REVOC_REG_DEF</sub></td>
    <td><sub>*</sub></td>
    <td><sub>*</sub></td>
    <td><sub>*</sub></td>
    <td><sub>Only owners can edit existing REVOC_REG_DEF</sub></td>
    <td><sub>Editing REVOC_REG_DEF</sub></td>
  </tr>
  <tr>
    <td><sub>REVOC_REG_ENTRY</sub></td>
    <td><sub>*</sub></td>
    <td><sub>*</sub></td>
    <td><sub>*</sub></td>
    <td><sub>Only the owner of the corresponding REVOC_REG_DEF can create new REVOC_REG_ENTRY</sub></td>
    <td><sub>Adding new REVOC_REG_ENTRY</sub></td>
  </tr>
  <tr>
    <td><sub>REVOC_REG_ENTRY</sub></td>
    <td><sub>*</sub></td>
    <td><sub>*</sub></td>
    <td><sub>*</sub></td>
    <td><sub>Only owners can edit existing REVOC_REG_ENTRY</sub></td>
    <td><sub>Editing REVOC_REG_ENTRY</sub></td>
  </tr>
</table>


#### If ANYONE_CAN_WRITE is set to True:
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
    <td><sub>REVOC_REG_DEF</sub></td>
    <td><sub>*</sub></td>
    <td><sub>*</sub></td>
    <td><sub>*</sub></td>
    <td><sub>Anyone can create new REVOC_REG_DEF</sub></td>
    <td><sub>Adding new REVOC_REG_DEF</sub></td>
  </tr>
  <tr>
    <td><sub>REVOC_REG_DEF</sub></td>
    <td><sub>*</sub></td>
    <td><sub>*</sub></td>
    <td><sub>*</sub></td>
    <td><sub>Only owners can edit existing REVOC_REG_DEF</sub></td>
    <td><sub>Editing REVOC_REG_DEF</sub></td>
  </tr>
  <tr>
    <td><sub>REVOC_REG_ENTRY</sub></td>
    <td><sub>*</sub></td>
    <td><sub>*</sub></td>
    <td><sub>*</sub></td>
    <td><sub>Only the owner of the corresponding REVOC_REG_DEF can create new REVOC_REG_ENTRY</sub></td>
    <td><sub>Adding new REVOC_REG_ENTRY</sub></td>
  </tr>
  <tr>
    <td><sub>REVOC_REG_ENTRY</sub></td>
    <td><sub>*</sub></td>
    <td><sub>*</sub></td>
    <td><sub>*</sub></td>
    <td><sub>Only owners can edit existing REVOC_REG_ENTRY</sub></td>
    <td><sub>Adding new REVOC_REG_ENTRY</sub></td>
  </tr>
</table>
