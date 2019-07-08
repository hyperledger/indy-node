from indy_common.constants import ENDORSER, NETWORK_MONITOR
from plenum.common.constants import TRUSTEE, STEWARD


OTHER_ROLE = "OtherRole"
OTHER_IDENTIFIER = "some_other_identifier"


IDENTIFIERS = {TRUSTEE: ["trustee_identifier", "trustee_identifier2", "trustee_identifier3", "trustee_identifier4"],
               STEWARD: ["steward_identifier", "steward_identifier2", "steward_identifier3", "steward_identifier4"],
               ENDORSER: ["endorser_identifier", "endorser_identifier2", "endorser_identifier3",
                          "endorser_identifier4"],
               NETWORK_MONITOR: ["network_monitor_identifier"],
               None: ["identity_owner_identifier", "identity_owner_identifier2", "identity_owner_identifier3",
                      "identity_owner_identifier4"],
               OTHER_ROLE: [OTHER_IDENTIFIER, "some_other_identifier2", "some_other_identifier3",
                            "some_other_identifier4"]}
