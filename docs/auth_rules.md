# Current implemented rules in auth_map
<style type="text/css">
.tg  {border-collapse:collapse;border-spacing:0;}
.tg td{font-family:Arial, sans-serif;font-size:14px;padding:10px 5px;border-style:solid;border-width:1px;overflow:hidden;word-break:normal;border-color:black;}
.tg th{font-family:Arial, sans-serif;font-size:14px;font-weight:normal;padding:10px 5px;border-style:solid;border-width:1px;overflow:hidden;word-break:normal;border-color:black;}
.tg .tg-0pky{font-size:12px;border-color:inherit;text-align:left;vertical-align:top}
</style>
<table class="tg">
  <tr>
    <th class="tg-0pky">Transaction type</td>
    <th class="tg-0pky">Field</td>
    <th class="tg-0pky">Previous value</td>
    <th class="tg-0pky">New value</td>
    <th class="tg-0pky">Who can</td>
    <th class="tg-0pky">Description</td>
  </tr>
  <tr>
    <td class="tg-0pky">NYM</td>
    <td class="tg-0pky">`role`</td>
    <td class="tg-0pky">`<empty>`</td>
    <td class="tg-0pky">TRUSTEE</td>
    <td class="tg-0pky">TRUSTEE</td>
    <td class="tg-0pky">Adding new TRUSTEE</td>
  </tr>
  <tr>
    <td class="tg-0pky">NYM</td>
    <td class="tg-0pky">`role`</td>
    <td class="tg-0pky">`<empty>`</td>
    <td class="tg-0pky">STEWARD</td>
    <td class="tg-0pky">TRUSTEE</td>
    <td class="tg-0pky">Adding new STEWARD</td>
  </tr>
  <tr>
    <td class="tg-0pky">NYM</td>
    <td class="tg-0pky">`role`</td>
    <td class="tg-0pky">`<empty>`</td>
    <td class="tg-0pky">TRUST_ANCHOR</td>
    <td class="tg-0pky">TRUSTEE, STEWARD</td>
    <td class="tg-0pky">Adding new TRUST_ANCHOR</td>
  </tr>
  <tr>
    <td class="tg-0pky">NYM</td>
    <td class="tg-0pky">`role`</td>
    <td class="tg-0pky">`<empty>`</td>
    <td class="tg-0pky">NETWORK_MONITOR</td>
    <td class="tg-0pky">TRUSTEE, STEWARD</td>
    <td class="tg-0pky">Adding new NETWORK_MONITOR</td>
  </tr>
  <tr>
    <td class="tg-0pky">NYM</td>
    <td class="tg-0pky">`role`</td>
    <td class="tg-0pky">`<empty>`</td>
    <td class="tg-0pky">`<empty>`</td>
    <td class="tg-0pky">TRUSTEE, STEWARD, TRUST_ANCHOR</td>
    <td class="tg-0pky">Adding new Identity Owner</td>
  </tr>
  <tr>
    <td class="tg-0pky">NYM</td>
    <td class="tg-0pky">`role`</td>
    <td class="tg-0pky">TRUSTEE</td>
    <td class="tg-0pky">`<empty>`</td>
    <td class="tg-0pky">TRUSTEE</td>
    <td class="tg-0pky">Blacklisting Trustee</td>
  </tr>
  <tr>
    <td class="tg-0pky">NYM</td>
    <td class="tg-0pky">`role`</td>
    <td class="tg-0pky">STEWARD</td>
    <td class="tg-0pky">`<empty>`</td>
    <td class="tg-0pky">TRUSTEE</td>
    <td class="tg-0pky">Blacklisting Steward</td>
  </tr>
  <tr>
    <td class="tg-0pky">NYM</td>
    <td class="tg-0pky">`role`</td>
    <td class="tg-0pky">TRUST_ANCHOR</td>
    <td class="tg-0pky">`<empty>`</td>
    <td class="tg-0pky">TRUSTEE</td>
    <td class="tg-0pky">Blacklisting Trust anchor</td>
  </tr>
  <tr>
    <td class="tg-0pky">NYM</td>
    <td class="tg-0pky">`role`</td>
    <td class="tg-0pky">NETWORK_MONITOR</td>
    <td class="tg-0pky">`<empty>`</td>
    <td class="tg-0pky">TRUSTEE, STEWARD</td>
    <td class="tg-0pky">Blacklisting user with NETWORK_MONITOR role</td>
  </tr>
  <tr>
    <td class="tg-0pky">NYM</td>
    <td class="tg-0pky">`verkey`</td>
    <td class="tg-0pky">`*`</td>
    <td class="tg-0pky">`*`</td>
    <td class="tg-0pky">Owner of this nym</td>
    <td class="tg-0pky">Key Rotation</td>
  </tr>
  <tr>
    <td class="tg-0pky">SCHEMA</td>
    <td class="tg-0pky">`*`</td>
    <td class="tg-0pky">`*`</td>
    <td class="tg-0pky">`*`</td>
    <td class="tg-0pky">TRUSTEE, STEWARD, TRUST_ANCHOR</td>
    <td class="tg-0pky">Adding new Schema</td>
  </tr>
  <tr>
    <td class="tg-0pky">SCHEMA</td>
    <td class="tg-0pky">`*`</td>
    <td class="tg-0pky">`*`</td>
    <td class="tg-0pky">`*`</td>
    <td class="tg-0pky">No one can edit existing Schema</td>
    <td class="tg-0pky">Editing Schema</td>
  </tr>
  <tr>
    <td class="tg-0pky">CLAIM_DEF</td>
    <td class="tg-0pky">`*`</td>
    <td class="tg-0pky">`*`</td>
    <td class="tg-0pky">`*`</td>
    <td class="tg-0pky">TRUSTEE, STEWARD, TRUST_ANCHOR</td>
    <td class="tg-0pky">Adding new CLAIM_DEF transaction</td>
  </tr>
  <tr>
    <td class="tg-0pky">CLAIM_DEF</td>
    <td class="tg-0pky">`*`</td>
    <td class="tg-0pky">`*`</td>
    <td class="tg-0pky">`*`</td>
    <td class="tg-0pky">Owner of claim_def txn</td>
    <td class="tg-0pky">Editing CLAIM_DEF transaction</td>
  </tr>
  <tr>
    <td class="tg-0pky">NODE</td>
    <td class="tg-0pky">`services`</td>
    <td class="tg-0pky">`<empty>`</td>
    <td class="tg-0pky">`[VALIDATOR]`</td>
    <td class="tg-0pky">STEWARD if it doesn't own NODE transaction yet</td>
    <td class="tg-0pky">Adding new node to pool</td>
  </tr>
  <tr>
    <td class="tg-0pky">NODE</td>
    <td class="tg-0pky">`services`</td>
    <td class="tg-0pky">`[VALIDATOR]`</td>
    <td class="tg-0pky">`[]`</td>
    <td class="tg-0pky">TRUSTEE, STEWARD if it is owner of this transaction</td>
    <td class="tg-0pky">Demotion of node</td>
  </tr>
  <tr>
    <td class="tg-0pky">NODE</td>
    <td class="tg-0pky">`services`</td>
    <td class="tg-0pky">`[]`</td>
    <td class="tg-0pky">`[VALIDATOR]`</td>
    <td class="tg-0pky">TRUSTEE, STEWARD if it is owner of this transaction</td>
    <td class="tg-0pky">Promotion of node</td>
  </tr>
  <tr>
    <td class="tg-0pky">NODE</td>
    <td class="tg-0pky">`node_ip`</td>
    <td class="tg-0pky">`*`</td>
    <td class="tg-0pky">`*`</td>
    <td class="tg-0pky">STEWARD if it is owner of this transaction</td>
    <td class="tg-0pky">Changing Node's ip address</td>
  </tr>
  <tr>
    <td class="tg-0pky">NODE</td>
    <td class="tg-0pky">`node_port`</td>
    <td class="tg-0pky">`*`</td>
    <td class="tg-0pky">`*`</td>
    <td class="tg-0pky">STEWARD if it is owner of this transaction</td>
    <td class="tg-0pky">Changing Node's port</td>
  </tr>
  <tr>
    <td class="tg-0pky">NODE</td>
    <td class="tg-0pky">`client_ip`</td>
    <td class="tg-0pky">`*`</td>
    <td class="tg-0pky">`*`</td>
    <td class="tg-0pky">STEWARD if it is owner of this transaction</td>
    <td class="tg-0pky">Changing Client's ip address</td>
  </tr>
  <tr>
    <td class="tg-0pky">NODE</td>
    <td class="tg-0pky">`client_port`</td>
    <td class="tg-0pky">`*`</td>
    <td class="tg-0pky">`*`</td>
    <td class="tg-0pky">STEWARD if it is owner of this transaction</td>
    <td class="tg-0pky">Changing Client's port</td>
  </tr>
  <tr>
    <td class="tg-0pky">NODE</td>
    <td class="tg-0pky">`blskey`</td>
    <td class="tg-0pky">`*`</td>
    <td class="tg-0pky">`*`</td>
    <td class="tg-0pky">STEWARD if it is owner of this transaction</td>
    <td class="tg-0pky">Changing Node's blskey</td>
  </tr>
  <tr>
    <td class="tg-0pky">POOL_UPGRADE</td>
    <td class="tg-0pky">`action`</td>
    <td class="tg-0pky">`<empty>`</td>
    <td class="tg-0pky">`start`</td>
    <td class="tg-0pky">TRUSTEE</td>
    <td class="tg-0pky">Starting upgrade procedure</td>
  </tr>
  <tr>
    <td class="tg-0pky">POOL_UPGRADE</td>
    <td class="tg-0pky">`action`</td>
    <td class="tg-0pky">`start`</td>
    <td class="tg-0pky">`cancel`</td>
    <td class="tg-0pky">TRUSTEE</td>
    <td class="tg-0pky">Canceling upgrade procedure</td>
  </tr>
  <tr>
    <td class="tg-0pky">POOL_RESTART</td>
    <td class="tg-0pky">`action`</td>
    <td class="tg-0pky">`*`</td>
    <td class="tg-0pky">`*`</td>
    <td class="tg-0pky">TRUSTEE</td>
    <td class="tg-0pky">Restarting pool command</td>
  </tr>
  <tr>
    <td class="tg-0pky">POOL_CONFIG</td>
    <td class="tg-0pky">`action`</td>
    <td class="tg-0pky">`*`</td>
    <td class="tg-0pky">`*`</td>
    <td class="tg-0pky">TRUSTEE</td>
    <td class="tg-0pky">Pool config command (like a `read only` option)</td>
  </tr>
  <tr>
    <td class="tg-0pky">VALIDATOR_INFO</td>
    <td class="tg-0pky">`*`</td>
    <td class="tg-0pky">`*`</td>
    <td class="tg-0pky">`*`</td>
    <td class="tg-0pky">TRUSTEE, STEWARD, NETWORK_MONITOR</td>
    <td class="tg-0pky">Getting validator_info from pool</td>
  </tr>
</table>

### Also, there is a some optional rules for case if in config option ANYONE_CAN_WRITE is set to True:
<style type="text/css">
.tg  {border-collapse:collapse;border-spacing:0;}
.tg td{font-family:Arial, sans-serif;font-size:14px;padding:10px 5px;border-style:solid;border-width:1px;overflow:hidden;word-break:normal;border-color:black;}
.tg th{font-family:Arial, sans-serif;font-size:14px;font-weight:normal;padding:10px 5px;border-style:solid;border-width:1px;overflow:hidden;word-break:normal;border-color:black;}
.tg .tg-0pky{font-size:12px;border-color:inherit;text-align:left;vertical-align:top}
</style>
<table class="tg">
  <tr>
    <th class="tg-0pky">Transaction type</td>
    <th class="tg-0pky">Field</td>
    <th class="tg-0pky">Previous value</td>
    <th class="tg-0pky">New value</td>
    <th class="tg-0pky">Who can</td>
    <th class="tg-0pky">Description</td>
  <\/tr>
  <tr>
    <td class="tg-0pky">NYM</td>
    <td class="tg-0pky">`role`</td>
    <td class="tg-0pky">`<empty>`</td>
    <td class="tg-0pky">`<empty>`</td>
    <td class="tg-0pky">Anyone</td>
    <td class="tg-0pky">Adding new nym</td>
  <\/tr>
  <tr>
    <td class="tg-0pky">SCHEMA</td>
    <td class="tg-0pky">`*`</td>
    <td class="tg-0pky">`*`</td>
    <td class="tg-0pky">`*`</td>
    <td class="tg-0pky">Anyone</td>
    <td class="tg-0pky">Any operations with SCHEMA transaction</td>
  <\/tr>
  <tr>
    <td class="tg-0pky">CLAIM_DEF</td>
    <td class="tg-0pky">`*`</td>
    <td class="tg-0pky">`*`</td>
    <td class="tg-0pky">`*`</td>
    <td class="tg-0pky">Anyone</td>
    <td class="tg-0pky">Any operations with CLAIM_DEF transaction</td>
  <\/tr>
</table>


### As of now it's not implemented yet, but the next rules for Revocation feature are needed:
#### If ANYONE_CAN_WRITE is set to False:
<style type="text/css">
.tg  {border-collapse:collapse;border-spacing:0;}
.tg td{font-family:Arial, sans-serif;font-size:14px;padding:10px 5px;border-style:solid;border-width:1px;overflow:hidden;word-break:normal;border-color:black;}
.tg th{font-family:Arial, sans-serif;font-size:14px;font-weight:normal;padding:10px 5px;border-style:solid;border-width:1px;overflow:hidden;word-break:normal;border-color:black;}
.tg .tg-0pky{font-size:12px;border-color:inherit;text-align:left;vertical-align:top}
</style>
<table class="tg">
  <tr>
    <th class="tg-0pky">Transaction type</td>
    <th class="tg-0pky">Field</td>
    <th class="tg-0pky">Previous value</td>
    <th class="tg-0pky">New value</td>
    <th class="tg-0pky">Who can</td>
    <th class="tg-0pky">Description</td>
  <\/tr>
  <tr>
    <td class="tg-0pky">REVOC_REG_DEF</td>
    <td class="tg-0pky">`*`</td>
    <td class="tg-0pky">`*`</td>
    <td class="tg-0pky">`*`</td>
    <td class="tg-0pky">TRUSTEE, STEWARD, TRUST_ANCHOR</td>
    <td class="tg-0pky">Adding new REVOC_REG_DEF</td>
  <\/tr>
  <tr>
    <td class="tg-0pky">REVOC_REG_DEF</td>
    <td class="tg-0pky">`*`</td>
    <td class="tg-0pky">`*`</td>
    <td class="tg-0pky">`*`</td>
    <td class="tg-0pky">Only owners can edit existing REVOC_REG_DEF</td>
    <td class="tg-0pky">Editing REVOC_REG_DEF</td>
  <\/tr>
  <tr>
    <td class="tg-0pky">REVOC_REG_ENTRY</td>
    <td class="tg-0pky">`*`</td>
    <td class="tg-0pky">`*`</td>
    <td class="tg-0pky">`*`</td>
    <td class="tg-0pky">Only the owner of the corresponding REVOC_REG_DEF can create new REVOC_REG_ENTRY</td>
    <td class="tg-0pky">Adding new REVOC_REG_ENTRY</td>
  <\/tr>
  <tr>
    <td class="tg-0pky">REVOC_REG_ENTRY</td>
    <td class="tg-0pky">`*`</td>
    <td class="tg-0pky">`*`</td>
    <td class="tg-0pky">`*`</td>
    <td class="tg-0pky">Only owners can edit existing REVOC_REG_ENTRY</td>
    <td class="tg-0pky">Editing REVOC_REG_ENTRY</td>
  <\/tr>
</table>


#### If ANYONE_CAN_WRITE is set to True:
<style type="text/css">
.tg  {border-collapse:collapse;border-spacing:0;}
.tg td{font-family:Arial, sans-serif;font-size:14px;padding:10px 5px;border-style:solid;border-width:1px;overflow:hidden;word-break:normal;border-color:black;}
.tg th{font-family:Arial, sans-serif;font-size:14px;font-weight:normal;padding:10px 5px;border-style:solid;border-width:1px;overflow:hidden;word-break:normal;border-color:black;}
.tg .tg-0pky{font-size:12px;border-color:inherit;text-align:left;vertical-align:top}
</style>
<table class="tg">
  <tr>
    <th class="tg-0pky">Transaction type</td>
    <th class="tg-0pky">Field</td>
    <th class="tg-0pky">Previous value</td>
    <th class="tg-0pky">New value</td>
    <th class="tg-0pky">Who can</td>
    <th class="tg-0pky">Description</td>
  <\/tr>
  <tr>
    <td class="tg-0pky">REVOC_REG_DEF</td>
    <td class="tg-0pky">`*`</td>
    <td class="tg-0pky">`*`</td>
    <td class="tg-0pky">`*`</td>
    <td class="tg-0pky">Anyone can create new REVOC_REG_DEF</td>
    <td class="tg-0pky">Adding new REVOC_REG_DEF</td>
  <\/tr>
  <tr>
    <td class="tg-0pky">REVOC_REG_DEF</td>
    <td class="tg-0pky">`*`</td>
    <td class="tg-0pky">`*`</td>
    <td class="tg-0pky">`*`</td>
    <td class="tg-0pky">Only owners can edit existing REVOC_REG_DEF</td>
    <td class="tg-0pky">Editing REVOC_REG_DEF</td>
  <\/tr>
  <tr>
    <td class="tg-0pky">REVOC_REG_ENTRY</td>
    <td class="tg-0pky">`*`</td>
    <td class="tg-0pky">`*`</td>
    <td class="tg-0pky">`*`</td>
    <td class="tg-0pky">Only the owner of the corresponding REVOC_REG_DEF can create new REVOC_REG_ENTRY</td>
    <td class="tg-0pky">Adding new REVOC_REG_ENTRY</td>
  <\/tr>
  <tr>
    <td class="tg-0pky">REVOC_REG_ENTRY</td>
    <td class="tg-0pky">`*`</td>
    <td class="tg-0pky">`*`</td>
    <td class="tg-0pky">`*`</td>
    <td class="tg-0pky">Only owners can edit existing REVOC_REG_ENTRY</td>
    <td class="tg-0pky">Adding new REVOC_REG_ENTRY</td>
  <\/tr>
</table>
