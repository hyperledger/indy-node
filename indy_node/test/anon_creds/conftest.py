import pytest
import time
import json
from contextlib import ExitStack
from plenum.common.util import randomString
from indy_common.constants import REVOC_REG_ENTRY, REVOC_REG_DEF_ID, ISSUED, \
    REVOKED, PREV_ACCUM, ACCUM, REVOC_REG_DEF, ISSUANCE_BY_DEFAULT, \
    CRED_DEF_ID, VALUE, TAG, ISSUANCE_ON_DEMAND, CLAIM_DEF, ID, GET_REVOC_REG_DEF, \
    TXN_TYPE, REVOC_TYPE, ISSUANCE_TYPE, MAX_CRED_NUM, TAILS_HASH, TAILS_LOCATION, PUBLIC_KEYS, \
    GET_REVOC_REG_DELTA, GET_REVOC_REG, TIMESTAMP, FROM, TO
from indy_common.types import Request
from indy_common.state import domain
from plenum.test.helper import sdk_sign_request_from_dict, sdk_send_and_check
from plenum.common.txn_util import reqToTxn
from plenum.common.types import f
from plenum.common.constants import TXN_TIME
from plenum.test.helper import create_new_test_node


@pytest.fixture(scope="module")
def create_node_and_not_start(testNodeClass,
                              node_config_helper_class,
                              tconf,
                              tdir,
                              allPluginsPath,
                              looper,
                              tdirWithPoolTxns,
                              tdirWithDomainTxns,
                              tdirWithNodeKeepInited):
    with ExitStack() as exitStack:
        node = exitStack.enter_context(create_new_test_node(testNodeClass,
                                node_config_helper_class,
                                "Alpha",
                                tconf,
                                tdir,
                                allPluginsPath))
        yield node
        node.stop()


@pytest.fixture(scope="module")
def add_revoc_def_by_default(create_node_and_not_start,
                  looper,
                  sdk_wallet_steward):
    node = create_node_and_not_start
    data = {
        ID: randomString(50),
        TXN_TYPE: REVOC_REG_DEF,
        REVOC_TYPE: "CL_ACCUM",
        TAG: randomString(5),
        CRED_DEF_ID: randomString(50),
        VALUE:{
            ISSUANCE_TYPE: ISSUANCE_BY_DEFAULT,
            MAX_CRED_NUM: 1000000,
            TAILS_HASH: randomString(50),
            TAILS_LOCATION: 'http://tails.location.com',
            PUBLIC_KEYS: {},
        }
    }
    req = sdk_sign_request_from_dict(looper, sdk_wallet_steward, data)

    req_handler = node.getDomainReqHandler()
    txn = reqToTxn(Request(**req))
    txn[f.SEQ_NO.nm] = node.domainLedger.seqNo + 1
    txn[TXN_TIME] = int(time.time())
    req_handler._addRevocDef(txn)
    return req

def build_revoc_reg_entry_for_given_revoc_reg_def(
        revoc_def_txn):
    revoc_def_txn = reqToTxn(revoc_def_txn)
    path = ":".join([revoc_def_txn[f.IDENTIFIER.nm],
                     domain.MARKER_REVOC_DEF,
                     revoc_def_txn[CRED_DEF_ID],
                     revoc_def_txn[REVOC_TYPE],
                     revoc_def_txn[TAG]])
    data = {
        REVOC_REG_DEF_ID: path,
        TXN_TYPE: REVOC_REG_ENTRY,
        REVOC_TYPE: revoc_def_txn[REVOC_TYPE],
        VALUE: {
            PREV_ACCUM: randomString(10),
            ACCUM: randomString(10),
            ISSUED: [],
            REVOKED: [],
        }
    }
    return data


@pytest.fixture(scope="module")
def build_txn_for_revoc_def_entry_by_default(looper,
                                  sdk_wallet_steward,
                                  add_revoc_def_by_default):
    revoc_def_txn = add_revoc_def_by_default
    data = build_revoc_reg_entry_for_given_revoc_reg_def(revoc_def_txn)
    req = sdk_sign_request_from_dict(looper, sdk_wallet_steward, data)
    return req

@pytest.fixture(scope="module")
def add_revoc_def_by_demand(create_node_and_not_start,
                  looper,
                  sdk_wallet_steward):
    node = create_node_and_not_start
    data = {
        ID: randomString(50),
        TXN_TYPE: REVOC_REG_DEF,
        REVOC_TYPE: "CL_ACCUM",
        TAG: randomString(5),
        CRED_DEF_ID: randomString(50),
        VALUE:{
            ISSUANCE_TYPE: ISSUANCE_ON_DEMAND,
            MAX_CRED_NUM: 1000000,
            TAILS_HASH: randomString(50),
            TAILS_LOCATION: 'http://tails.location.com',
            PUBLIC_KEYS: {},
        }
    }
    req = sdk_sign_request_from_dict(looper, sdk_wallet_steward, data)

    req_handler = node.getDomainReqHandler()
    txn = reqToTxn(Request(**req))
    txn[f.SEQ_NO.nm] = node.domainLedger.seqNo + 1
    txn[TXN_TIME] = int(time.time())
    req_handler._addRevocDef(txn)
    return req

@pytest.fixture(scope="module")
def build_txn_for_revoc_def_entry_by_demand(looper,
                                  sdk_wallet_steward,
                                  add_revoc_def_by_demand):
    revoc_def_txn = add_revoc_def_by_demand
    revoc_def_txn = reqToTxn(revoc_def_txn)
    path = ":".join([revoc_def_txn[f.IDENTIFIER.nm],
                     domain.MARKER_REVOC_DEF,
                     revoc_def_txn[CRED_DEF_ID],
                     revoc_def_txn[REVOC_TYPE],
                     revoc_def_txn[TAG]])
    data = {
        REVOC_REG_DEF_ID: path,
        TXN_TYPE: REVOC_REG_ENTRY,
        VALUE: {
            PREV_ACCUM: randomString(10),
            ACCUM: randomString(10),
            ISSUED: [],
            REVOKED: [],
        }
    }

    req = sdk_sign_request_from_dict(looper, sdk_wallet_steward, data)
    return req

@pytest.fixture(scope="module")
def claim_def():
    return {
        "type": CLAIM_DEF,
        "ref": 1,
        "signature_type": "CL",
        "data": {
            "primary": {
                "n": "94759924268422840873493186881483285628376767714620627055233230078254863658476446487556117977593248501523199451418346650764648601684276437772084327637083000213497377603495837360299641742248892290843802071224822481683143989223918276185323177379400413928352871249494885563503003839960930062341074783742062464846448855510814252519824733234277681749977392772900212293652238651538092092030867161752390937372967233462027620699196724949212432236376627703446877808405786247217818975482797381180714523093913559060716447170497587855871901716892114835713057965087473682457896508094049813280368069805661739141591558517233009123957",
                "s": "3589207374161609293256840431433442367968556468254553005135697551692970564853243905310862234226531556373974144223993822323573625466428920716249949819187529684239371465431718456502388533731367046146704547241076626874082510133130124364613881638153345624380195335138152993132904167470515345775215584510356780117368593105284564368954871044494967246738070895990267205643985529060025311535539534155086912661927003271053443110788963970349858709526217650537936123121324492871282397691771309596632805099306241616501610166028401599243350835158479028294769235556557248339060399322556412171888114265194198405765574333538019124846",
                "rms": "57150374376895616256492932008792437185713712934712117819417607831438470701645904776986426606717466732609284990796923331049549544903261623636958698296956103821068569714644825742048584174696465882627177060166162341112552851798863535031243458188976013190131935905789786836375734914391914349188643340535242562896244661798678234667651641013894284156416773868299435641426810968290584996112925365638881750944407842890875840705650290814965768221299488400872767679122749231050406680432079499973527780212310700022178178822528199576164498116369689770884051691678056831493476045361227274839673581033532995523269047577973637307053",
                "r": {
                    "age": "94304485801056920773231824603827244147437820123357994068540328541540143488826838939836897544389872126768239056314698953816072289663428273075648246498659039419931054256171488371404693243192741923382499918184822032756852725234903892700640856294525441486319095181804549558538523888770076173572615957495813339649470619615099181648313548341951673407624414494737018574238782648822189142664108450534642272145962844003886059737965854042074083374478426875684184904488545593139633653407062308621502392373426120986761417580127895634822264744063122368296502161439648408926687989964483291459079738447940651025900007635890755686910",
                    "sex": "29253365609829921413347591854991689007250272038394995372767401325848195298844802462252851926995846503104090589196060683329875231216529049681648909174047403783834364995363938741001507091534282239210301727771803410513303526378812888571225762557471133950393342500638551458868147905023198508660460641434022020257614450354085808398293279060446966692082427506909617283562394303716193372887306176319841941848888379308208426966697446699225783646634631703732019477632822374479322570142967559738439193417309205283438893083349863592921249218168590490390313109776446516881569691499831380592661740653935515397472059631417493981532",
                    "name": "25134437486609445980011967476486104706321061312022352268621323694861467756181853100693555519614894168921947814126694858839278103549577703105305116890325322098078409416441750313062396467567140699008203113519528887729951138845002409659317083029073793314514377377412805387401717457417895322600145580639449003584446356048213839274172751441145076183734269045919984853749007476629365146654240675320041155618450449041510280560040162429566008590065069477149918088087715269037925211599101597422023202484497946662159070023999719865939258557778022770035320019440597702090334486792710436579355608406897769514395306079855023848170",
                    "height": "59326960517737425423547279838932030505937927873589489863081026714907925093402287263487670945897247474465655528290016645774365383046524346223348261262488616342337864633104758662753452450299389775751012589698563659277683974188553993694220606310980581680471280640591973543996299789038056921309016983827578247477799948667666717056420270448516049047961099547588510086600581628091290215485826514170097211360599793229701811672966818089371089216189744274422526431130783428589346341196561742409198605034972210917502326180305735092988639850309253190875578501020679137562856724998821945605494355779034135306337094344532980411836"
                },
                "rctxt": "9641986614889199796257508700106896585587271615330980339636468819377346498767697681332046156705231986464570206666984343024200482683981302064613556104594051003956610353281701880542337665385482309134369756144345334575765116656633321636736946947493150642615481313285221467998414924865943067790561494301461899025374692884841352282256044388512875752628313052128404892424405230961678931620525106856624692942373538946467902799339061714326383378018581568876147181355325663707572429090278505823900491548970098691127791086305310899642155499128171811034581730190877600697624903963241473287185133286356124371104261592694271730029",
                "z": "77594127026421654059198621152153180600664927707984020918609426112642522289621323453889995053400171879296098965678384769043918218957929606187082395048777546641833348694470081024386996548890150355901703252426977094536933434556202865213941384425538749866521536494046548509344678288447175898173634381514948562261015286492185924659638474376885655055568341574638453213864956407243206035973349529545863886325462867413885904072942842465859476940638839087894582648849969332663627779378998245133055807038199937421971988505911494931665143822588532097754480882750243126847177560978100527491344463525107644125030963904001009159559"
            },
        }
    }

@pytest.fixture(scope="module")
def send_claim_def(looper,
                   txnPoolNodeSet,
                   sdk_wallet_steward,
                   sdk_pool_handle,
                   claim_def):
    req = sdk_sign_request_from_dict(looper, sdk_wallet_steward, claim_def)
    sdk_send_and_check([json.dumps(req)], looper, txnPoolNodeSet, sdk_pool_handle)
    return req

@pytest.fixture(scope="module")
def build_revoc_def_by_default(looper, sdk_wallet_steward):
    data = {
        ID: randomString(50),
        TXN_TYPE: REVOC_REG_DEF,
        REVOC_TYPE: "CL_ACCUM",
        TAG: randomString(5),
        CRED_DEF_ID: randomString(50),
        VALUE:{
            ISSUANCE_TYPE: ISSUANCE_BY_DEFAULT,
            MAX_CRED_NUM: 1000000,
            TAILS_HASH: randomString(50),
            TAILS_LOCATION: 'http://tails.location.com',
            PUBLIC_KEYS: {},
        }
    }
    req = sdk_sign_request_from_dict(looper, sdk_wallet_steward, data)
    return req

@pytest.fixture(scope="module")
def build_revoc_def_by_demand(looper, sdk_wallet_steward):
    data = {
        ID: randomString(50),
        TXN_TYPE: REVOC_REG_DEF,
        REVOC_TYPE: "CL_ACCUM",
        TAG: randomString(5),
        CRED_DEF_ID: randomString(50),
        VALUE:{
            ISSUANCE_TYPE: ISSUANCE_ON_DEMAND,
            MAX_CRED_NUM: 1000000,
            TAILS_HASH: randomString(50),
            TAILS_LOCATION: 'http://tails.location.com',
            PUBLIC_KEYS: {},
        }
    }
    req = sdk_sign_request_from_dict(looper, sdk_wallet_steward, data)
    return req

@pytest.fixture(scope="module")
def send_revoc_reg_def_by_default(looper,
                                  txnPoolNodeSet,
                                  sdk_wallet_steward,
                                  sdk_pool_handle,
                                  send_claim_def,
                                  build_revoc_def_by_default):
    _, author_did = sdk_wallet_steward
    claim_def_req = send_claim_def
    revoc_reg = build_revoc_def_by_default
    revoc_reg['operation'][CRED_DEF_ID] = ":".join([author_did,
                                                    domain.MARKER_CLAIM_DEF,
                                                    claim_def_req['operation']["signature_type"],
                                                    str(claim_def_req['operation']["ref"])])
    revoc_req = sdk_sign_request_from_dict(looper, sdk_wallet_steward, revoc_reg['operation'])
    sdk_send_and_check([json.dumps(revoc_req)], looper, txnPoolNodeSet, sdk_pool_handle)
    return revoc_req

@pytest.fixture(scope="module")
def send_revoc_reg_def_by_demand(looper,
                                  txnPoolNodeSet,
                                  sdk_wallet_steward,
                                  sdk_pool_handle,
                                  send_claim_def,
                                 build_revoc_def_by_demand):
    _, author_did = sdk_wallet_steward
    claim_def_req = send_claim_def
    revoc_reg = build_revoc_def_by_demand
    revoc_reg['operation'][CRED_DEF_ID] = ":".join([author_did,
                                                    domain.MARKER_CLAIM_DEF,
                                                    claim_def_req['operation']["signature_type"],
                                                    str(claim_def_req['operation']["ref"])])
    revoc_req = sdk_sign_request_from_dict(looper, sdk_wallet_steward, revoc_reg['operation'])
    sdk_send_and_check([json.dumps(revoc_req)], looper, txnPoolNodeSet, sdk_pool_handle)
    return revoc_req


@pytest.fixture(scope="module")
def send_revoc_reg_entry_by_default(looper,
                         txnPoolNodeSet,
                         sdk_wallet_steward,
                         sdk_pool_handle,
                         send_revoc_reg_def_by_default):
    revoc_def_req = send_revoc_reg_def_by_default
    rev_reg_entry = build_revoc_reg_entry_for_given_revoc_reg_def(revoc_def_req)
    rev_reg_entry[VALUE][REVOKED] = [1, 2, 3, 4, 5]
    rev_entry_req = sdk_sign_request_from_dict(looper, sdk_wallet_steward, rev_reg_entry)
    reg_entry_replies = sdk_send_and_check([json.dumps(rev_entry_req)],
                       looper,
                       txnPoolNodeSet,
                       sdk_pool_handle)
    return reg_entry_replies[0]


@pytest.fixture(scope="module")
def send_revoc_reg_entry_by_demand(looper,
                         txnPoolNodeSet,
                         sdk_wallet_steward,
                         sdk_pool_handle,
                         send_revoc_reg_def_by_demand):
    revoc_def_req = send_revoc_reg_def_by_demand
    rev_reg_entry = build_revoc_reg_entry_for_given_revoc_reg_def(revoc_def_req)
    rev_reg_entry[VALUE][ISSUED] = [1, 2, 3, 4, 5]
    rev_entry_req = sdk_sign_request_from_dict(looper, sdk_wallet_steward, rev_reg_entry)
    reg_entry_replies = sdk_send_and_check([json.dumps(rev_entry_req)],
                       looper,
                       txnPoolNodeSet,
                       sdk_pool_handle)
    return reg_entry_replies[0]


@pytest.fixture(scope="module")
def build_get_revoc_reg_entry(looper,
                              sdk_wallet_steward):

    data = {
        REVOC_REG_DEF_ID: randomString(10),
        TXN_TYPE: GET_REVOC_REG,
        TIMESTAMP: int(time.time())
    }
    revoc_reg_req = sdk_sign_request_from_dict(looper, sdk_wallet_steward, data)
    return revoc_reg_req


@pytest.fixture(scope="module")
def build_get_revoc_reg_delta(looper,
                              sdk_wallet_steward):
    data = {
        REVOC_REG_DEF_ID: randomString(10),
        TXN_TYPE: GET_REVOC_REG_DELTA,
        FROM: 10,
        TO: 20,
    }
    revoc_reg_delta_req = sdk_sign_request_from_dict(looper, sdk_wallet_steward, data)
    return revoc_reg_delta_req