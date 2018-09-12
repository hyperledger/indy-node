from plenum.cli.command import Command
from indy_common.roles import Roles
from indy_common.transactions import IndyTransactions

nymName = IndyTransactions.NYM.name
getNymName = IndyTransactions.GET_NYM.name
attribName = IndyTransactions.ATTRIB.name
getAttrName = IndyTransactions.GET_ATTR.name
nodeName = IndyTransactions.NODE.name
schemaName = IndyTransactions.SCHEMA.name
getSchemaName = IndyTransactions.GET_SCHEMA.name
poolUpgradeName = IndyTransactions.POOL_UPGRADE.name
claimDefName = IndyTransactions.CLAIM_DEF.name
getClaimDefName = IndyTransactions.GET_CLAIM_DEF.name
poolConfigName = IndyTransactions.POOL_CONFIG.name
changeKeyName = IndyTransactions.CHANGE_KEY.name

sendNymCmd = Command(
    id="send {nym}".format(
        nym=nymName),
    title="Adds given DID to indy",
    usage="send {nym} dest=<target DID> role=<role> [verkey=<ver-key>]".format(
        nym=nymName),
    examples=[
        "send {nym} dest=BiCMHDqC5EjheFHumZX9nuAoVEp8xyuBgiRi5JcY5whi role={role}".format(
            nym=nymName,
            role=Roles.TRUST_ANCHOR.name),
        "send {nym} dest=33A18XMqWqTzDpLHXLR5nT verkey=~Fem61Q5SnYhGVVHByQNxHj".format(
            nym=nymName)])

sendGetNymCmd = Command(
    id="send {getNym}".format(
        getNym=getNymName),
    title="Get NYM from indy",
    usage="send {getNym} dest=<target DID>".format(
        getNym=getNymName),
    examples="send {getNym} dest=33A18XMqWqTzDpLHXLR5nT".format(
        getNym=getNymName))

sendAttribCmd = Command(
    id="send {attrib}".format(attrib=attribName),
    title="Adds attributes to existing DID",
    usage="send {attrib} dest=<target DID> [raw={{<json-data>}}] [hash=<hashed-data>] [enc=<encrypted-data>]".format(
        attrib=attribName),
    examples='send {attrib} dest=33A18XMqWqTzDpLHXLR5nT raw={{"endpoint": "127.0.0.1:5555"}}'.format(attrib=attribName))

sendGetAttrCmd = Command(
    id="send {getAttr}".format(
        getAttr=getAttrName),
    title="Get ATTR from indy",
    usage="send {getAttr} dest=<target DID> [raw=<name>] [hash=<hashed-data>] [enc=<encrypted-data>]".format(
        getAttr=getAttrName),
    examples="send {getAttr} dest=33A18XMqWqTzDpLHXLR5nT raw=endpoint".format(
        getAttr=getAttrName))


sendNodeCmd = Command(
    id="send {node}".format(node=nodeName),
    title="Adds a node to the pool",
    usage="send {node} dest=<target node DID> data={{<json-data>}}".format(
        node=nodeName),
    note="Only Steward (must be already added on indy) can execute this command to add new node to the pool",
    examples='send {node} dest=87Ys5T2eZfau4AATsBZAYvqwvD8XL5xYCHgg2o1ffjqg data={{"services":["VALIDATOR"], '
             '"node_ip": "127.0.0.1", "node_port": 9711, "client_ip": "127.0.0.1", "client_port": 9712, '
             '"alias": "Node101", "blskey": "00000000000000000000000000000000"}}'.format(node=nodeName))

sendPoolUpgCmd = Command(
    id="send {poolUpgrade}".format(poolUpgrade=poolUpgradeName),
    title="Sends instructions to nodes to update themselves",
    usage="send {poolUpgrade} name=<name> version=<version> sha256=<sha256> action=<action> schedule=<schedule> timeout=<timeout> force=<force> reinstall=<reinstall> package=<pkg-name>".format(
        poolUpgrade=poolUpgradeName),
    examples="send {poolUpgrade} name=upgrade-01 "
             "version=0.0.1 sha256=e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855 action=start "
             "schedule={{'AtDfpKFe1RPgcr5nnYBw1Wxkgyn8Zjyh5MzFoEUTeoV3': "
             "'2017-01-25T12:49:05.258870+00:00', "
             "'4yC546FFzorLPgTNTc6V43DnpFrR8uHvtunBxb2Suaa2': "
             "'2017-01-25T12:33:53.258870+00:00', "
             "'JpYerf4CssDrH76z7jyQPJLnZ1vwYgvKbvcp16AB5RQ': "
             "'2017-01-25T12:44:01.258870+00:00', "
             "'DG5M4zFm33Shrhjj6JB7nmx9BoNJUq219UXDfvwBDPe2': "
             "'2017-01-25T12:38:57.258870+00:00'}} "
             "timeout=10 "
             "force=False "
             "reinstall=False "
             "package=indy-node".format(poolUpgrade=poolUpgradeName))

sendSchemaCmd = Command(
    id="send {schema}".format(
        schema=schemaName),
    title="Adds schema to indy",
    usage="send {schema} name=<schema-name> version=<version> keys=<comma separated attributes>".format(
        schema=schemaName),
    examples="send {schema} name=Degree version=1.0 keys=undergrad,last_name,first_name,birth_date,postgrad,expiry_date".format(
        schema=schemaName))

sendGetSchemaCmd = Command(
    id="send {getSchema}".format(
        getSchema=getSchemaName),
    title="Gets schema from indy",
    usage="send {getSchema} dest=<target DID> name=<schema-name> version=<version>".format(
        getSchema=getSchemaName),
    examples="send {getSchema} dest=33A18XMqWqTzDpLHXLR5nT name=Degree version=1.0".format(
        getSchema=getSchemaName))


sendClaimDefCmd = Command(
    id="send {claimDef}".format(claimDef=claimDefName),
    title="Adds claim definition for given schema",
    usage="send {claimDef} ref=<ref-no-of-SCHEMA-txn> signature_type=<type>".format(
        claimDef=claimDefName),
    examples="send {claimDef} ref=10 signature_type=CL".format(claimDef=claimDefName))

sendGetClaimDefCmd = Command(
    id="send {getClaimDef}".format(
        getClaimDef=getClaimDefName),
    title="Gets claim definition from indy",
    usage="send {getClaimDef} ref=<ref-no-of-SCHEMA-txn> signature_type=<type>".format(
        getClaimDef=getClaimDefName),
    examples="send {getClaimDef} ref=10 signature_type=CL".format(
        getClaimDef=getClaimDefName))

sendProofRequestCmd = Command(
    id="send proof request",
    title="Send a proof request",
    usage="send proofreq <proof-name> to <remote>",
    examples="send proofreq Over-21 to JaneDo")

showFileCmd = Command(
    id="show",
    title="Shows content of given file",
    usage="show <file-path>",
    examples="show sample/faber-request.indy")

loadFileCmd = Command(
    id="load",
    title="Creates the connection",
    usage="load <file-path>",
    examples="load sample/faber-request.indy")

showConnectionCmd = Command(
    id="show connection",
    title="Shows connection info in case of one matching connection, otherwise shows all the matching connection names",
    usage="show connection <connection-name>",
    examples="show connection faber")

connectToCmd = Command(
    id="connect",
    title="Lets you connect to the respective environment",
    usage="connect sandbox|live",
    examples=["connect sandbox", "connect live"])

disconnectCmd = Command(
    id="disconnect",
    title="Disconnects from currently connected environment",
    usage="disconnect")

syncConnectionCmd = Command(
    id="sync",
    title="Synchronizes the connection between the endpoints",
    usage="sync connection <connection-name>",
    examples="sync connection faber")

pingTargetCmd = Command(
    id="ping",
    title="Pings given remote's endpoint",
    usage="ping <remote>",
    examples="ping faber")

showClaimCmd = Command(
    id="show claim",
    title="Shows given claim information",
    usage="show claim <claim-name>",
    examples="show claim Transcript")

listClaimsCmd = Command(
    id="list claims",
    title="Refresh the list of claims",
    usage="list claims <link-name>",
    examples="list claims faber")

listConnectionsCmd = Command(
    id='list connections',
    title='List available connections in active wallet',
    usage='list connections',
    examples='list connections'
)

reqClaimCmd = Command(
    id="request claim",
    title="Request given claim",
    usage="request claim <claim-name>",
    examples="request claim Transcript")

showProofRequestCmd = Command(
    id="show proof request",
    title="Shows given proof request",
    usage="show proof request <proof-req-name>",
    examples="show proof request Transcription")

acceptConnectionCmd = Command(
    id="accept request from",
    title="Accept request from given remote",
    usage="accept request from <remote>",
    examples="accept request from Faber")

setAttrCmd = Command(
    id="set",
    title="Sets given value to given attribute name",
    usage="set <attr-name> to <attr-value>",
    examples="set first_name to Alice")

sendProofCmd = Command(
    id="send proof",
    title="Sends given proof to given remote",
    usage="send proof <claim-name> to <remote>",
    examples="send proof Job-Application to Acme Corp")

addGenesisTxnCmd = Command(
    id="add genesis transaction",
    title="Adds given genesis transaction",
    usage="add genesis transaction {nym} dest=<dest-DID> [role=<role>]".format(
        nym=nymName),
    examples=[
        'add genesis transaction {nym} dest=2ru5PcgeQzxF7QZYwQgDkG2K13PRqyigVw99zMYg8eML'.format(
            nym=nymName),
        'add genesis transaction {nym} dest=2ru5PcgeQzxF7QZYwQgDkG2K13PRqyigVw99zMYg8eML role={role}'.format(
            nym=nymName, role=Roles.STEWARD.name),
        'add genesis transaction {node} for 2ru5PcgeQzxF7QZYwQgDkG2K13PRqyigVw99zMYg8eML by FvDi9xQZd1CZitbK15BNKFbA7izCdXZjvxf91u3rQVzW with data '
        '{{"node_ip": "localhost", "node_port": "9701", "client_ip": "localhost", "client_port": "9702", "alias": "AliceNode"}}'.format(node=nodeName)])

newDIDCmd = Command(
    id="new DID",
    title="Creates new DID",
    usage="new DID [<DID>|abbr|crypto] [with seed <seed>] [as <alias>]",
    note="crypto = cryptographic DID, abbr = abbreviated verkey",
    examples=[
        "new DID",
        "new DID abbr",
        "new DID 4QxzWk3ajdnEA37NdNU5Kt",
        "new DID with seed aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa",
        "new DID abbr with seed aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa",
        "new DID 4QxzWk3ajdnEA37NdNU5Kt with seed aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa"])

reqAvailClaimsCmd = Command(
    id="request available claims from",
    title="Requests all available claims from given connection",
    usage="request available claims from <connection-name>",
    examples="request available claims from Faber"
)

sendPoolConfigCmd = Command(
    id="send {poolConfig}".format(poolConfig=poolConfigName),
    title="Sends write configuration to pool",
    usage="send {poolConfig} writes=<writes> force=<force>".format(
        poolConfig=poolConfigName),
    examples="send {poolConfig} writes=True force=False".format(
        poolConfig=poolConfigName)
)

changeKeyCmd = Command(
    id="change current key",
    title="Changes key for the current identifier",
    usage="change current key [with seed <seed>]",
    examples=[
        "change current key",
        "change current key with seed aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa"]
)
