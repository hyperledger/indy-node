from plenum.cli.command import Command
from sovrin_common.roles import Roles
from sovrin_common.transactions import SovrinTransactions

nymName = SovrinTransactions.NYM.name
getNymName = SovrinTransactions.GET_NYM.name
attribName = SovrinTransactions.ATTRIB.name
getAttrName = SovrinTransactions.GET_ATTR.name
nodeName = SovrinTransactions.NODE.name
schemaName = SovrinTransactions.SCHEMA.name
getSchemaName = SovrinTransactions.GET_SCHEMA.name
poolUpgradeName = SovrinTransactions.POOL_UPGRADE.name
claimDefName = SovrinTransactions.CLAIM_DEF.name
getClaimDefName = SovrinTransactions.GET_CLAIM_DEF.name

sendNymCmd = Command(
    id="send {nym}".format(nym=nymName),
    title="Adds given identifier to sovrin",
    usage="send {nym} dest=<target identifier> role=<role> [verkey=<ver-key>]".format(nym=nymName),
    examples=[
        "send {nym} dest=BiCMHDqC5EjheFHumZX9nuAoVEp8xyuBgiRi5JcY5whi role={role}".format(nym=nymName,
                                                                                          role=Roles.TRUST_ANCHOR.name),
        "send {nym} dest=33A18XMqWqTzDpLHXLR5nT verkey=~Fem61Q5SnYhGVVHByQNxHj".format(nym=nymName)])

sendGetNymCmd = Command(
    id="send {getNym}".format(getNym=getNymName),
    title="Get NYM from sovrin",
    usage="send {getNym} dest=<target identifier>".format(getNym=getNymName),
    examples="send {getNym} dest=33A18XMqWqTzDpLHXLR5nT".format(getNym=getNymName))

sendAttribCmd = Command(
    id="send {attrib}".format(attrib=attribName),
    title="Adds attributes to existing identifier",
    usage="send {attrib} dest=<target identifier> [raw={{<json-data>}}] [hash=<hashed-data>] [enc: <encrypted-data>]".format(
        attrib=attribName),
    examples='send {attrib} dest=33A18XMqWqTzDpLHXLR5nT raw={{"endpoint": "127.0.0.1:5555"}}'.format(attrib=attribName))

sendGetAttrCmd = Command(
    id="send {getAttr}".format(getAttr=getAttrName),
    title="Get ATTR from sovrin",
    usage="send {getAttr} dest=<target identifier>".format(getAttr=getAttrName),
    examples="send {getAttr} dest=33A18XMqWqTzDpLHXLR5nT".format(getAttr=getAttrName))

sendNodeCmd = Command(
    id="send {node}".format(node=nodeName),
    title="Adds a node to the pool",
    usage="send {node} dest=<target node identifier> data={{<json-data>}}".format(node=nodeName),
    note="Only Steward (must be already added on sovrin) can execute this command to add new node to the pool",
    examples='send {node} dest=87Ys5T2eZfau4AATsBZAYvqwvD8XL5xYCHgg2o1ffjqg data={{"services":["VALIDATOR"], "node_ip": "127.0.0.1", "node_port": 9711, "client_ip": "127.0.0.1", "client_port": 9712, "alias": "Node101"}}'.format(
        node=nodeName))

sendPoolUpgCmd = Command(
    id="send {poolUpgrade}".format(poolUpgrade=poolUpgradeName),
    title="Sends instructions to nodes to update themselves",
    usage="send {poolUpgrade} name=<name> version=<version> sha256=<sha256> action=<action> schedule=<schedule> timeout=<timeout> force=<force>".format(poolUpgrade=poolUpgradeName),
    examples="send {poolUpgrade} name=upgrade-01 "
             "version=0.0.1 sha256=aad1242 action=start "
             "schedule={{'AtDfpKFe1RPgcr5nnYBw1Wxkgyn8Zjyh5MzFoEUTeoV3': "
             "'2017-01-25T12:49:05.258870+00:00', "
             "'4yC546FFzorLPgTNTc6V43DnpFrR8uHvtunBxb2Suaa2': "
             "'2017-01-25T12:33:53.258870+00:00', "
             "'JpYerf4CssDrH76z7jyQPJLnZ1vwYgvKbvcp16AB5RQ': "
             "'2017-01-25T12:44:01.258870+00:00', "
             "'DG5M4zFm33Shrhjj6JB7nmx9BoNJUq219UXDfvwBDPe2': "
             "'2017-01-25T12:38:57.258870+00:00'}} "
             "timeout=10 "
             "force=False".format(poolUpgrade=poolUpgradeName))

sendSchemaCmd = Command(
    id="send {schema}".format(schema=schemaName),
    title="Adds schema to sovrin",
    usage="send {schema} name=<schema-name> version=<version> keys=<comma separated attributes>".format(schema=schemaName),
    examples="send {schema} name=Degree version=1.0 keys=undergrad,last_name,first_name,birth_date,postgrad,expiry_date".format(schema=schemaName))

sendGetSchemaCmd = Command(
    id="send {getSchema}".format(getSchema=getSchemaName),
    title="Gets schema from sovrin",
    usage="send {getSchema} dest=<target identifier> name=<schema-name> version=<version>".format(getSchema=getSchemaName),
    examples="send {getSchema} name=Degree version=1.0".format(getSchema=getSchemaName))

sendClaimDefCmd = Command(
    id="send {claimDef}".format(claimDef=claimDefName),
    title="Adds claim definition for given schema",
    usage="send {claimDef} ref=<ref-no-of-SCHEMA-txn> signature_type=<type>".format(claimDef=claimDefName),
    examples="send {claimDef} ref=10 signature_type=CL".format(claimDef=claimDefName))

sendGetClaimDefCmd = Command(
    id="send {getClaimDef}".format(getClaimDef=getClaimDefName),
    title="Gets claim definition from sovrin",
    usage="send {getClaimDef} ref=<ref-no-of-SCHEMA-txn> signature_type=<type>".format(getClaimDef=getClaimDefName),
    examples="send {getClaimDef} ref=10 signature_type=CL".format(getClaimDef=getClaimDefName))

sendProofRequestCmd = Command(
    id="send proofreq",
    title="Send a proof request",
    usage="send proofreq <proof-name> to <remote>",
    examples="send proofreq Over-21 to JaneDo")

showFileCmd = Command(
    id="show",
    title="Shows content of given file",
    usage="show <file-path>",
    examples="show sample/faber-invitation.sovrin")

loadFileCmd = Command(
    id="load",
    title="Creates the link",
    usage="load <file-path>",
    examples="load sample/faber-invitation.sovrin")

showLinkCmd = Command(
    id="show link",
    title="Shows link info in case of one matching link, otherwise shows all the matching link names",
    usage="show link <link-name>",
    examples="show link faber")

connectToCmd = Command(
    id="connect",
    title="Lets you connect to the respective environment (test/live)",
    usage="connect test|live",
    examples=["connect test", "connect live"])

disconnectCmd = Command(
    id="disconnect",
    title="Disconnects from currently connected environment",
    usage="disconnect")

syncLinkCmd = Command(
    id="sync",
    title="Synchronizes the link between the endpoints",
    usage="sync link <link-name>",
    examples="sync link faber")

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

listLinksCmd = Command(
    id='list links',
    title='List available links in active wallet',
    usage='list links',
    examples='list links'
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

acceptLinkCmd = Command(
    id="accept invitation from",
    title="Accept invitation from given remote",
    usage="accept invitation from <remote>",
    examples="accept invitation from Faber")

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
    usage="add genesis transaction {nym} dest=<dest-identifier> [role=<role>]".format(nym=nymName),
    examples=[
        'add genesis transaction {nym} dest=2ru5PcgeQzxF7QZYwQgDkG2K13PRqyigVw99zMYg8eML'.format(nym=nymName),
        'add genesis transaction {nym} dest=2ru5PcgeQzxF7QZYwQgDkG2K13PRqyigVw99zMYg8eML role={role}'.format(
            nym=nymName, role=Roles.STEWARD.name),
        'add genesis transaction {node} for 2ru5PcgeQzxF7QZYwQgDkG2K13PRqyigVw99zMYg8eML by FvDi9xQZd1CZitbK15BNKFbA7izCdXZjvxf91u3rQVzW with data '
        '{{"node_ip": "localhost", "node_port": "9701", "client_ip": "localhost", "client_port": "9702", "alias": "AliceNode"}}'.format(node=nodeName)])

newIdentifierCmd = Command(
    id="new identifier",
    title="Creates new Identifier",
    usage="new identifier [<identifier>|abbr|crypto] [with seed <seed>] [as <alias>]",
    note="crypto = cryptographic identifier, abbr = abbreviated verkey",
    examples=[
        "new identifier",
        "new identifier abbr",
        "new identifier 4QxzWk3ajdnEA37NdNU5Kt",
        "new identifier with seed aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa",
        "new identifier abbr with seed aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa",
        "new identifier 4QxzWk3ajdnEA37NdNU5Kt with seed aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa"])

reqAvailClaimsCmd = Command(
    id="request available claims from",
    title="Requests all available claims from given connection",
    usage="request available claims from <connection-name>",
    examples="request available claims from Faber"
)
