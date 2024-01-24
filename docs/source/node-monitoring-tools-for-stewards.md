# Node Monitoring Tools for Stewards

- [Node Monitoring Tools for Stewards](#node-monitoring-tools-for-stewards)
  - [Plugin Manager](#plugin-manager)
    - [Events Emitted](#events-emitted)
  - [Plugins](#plugins)

## Plugin Manager

Currently, indy-node emits different events via the Plugin Manager when certain criteria are met. The Plugin Manager tries to import all pip packages which names start with "indynotifier*". Each of these packages is required to expose `send_message`; interface which is used to pass the event with the associated message to the package for further handling.

The Plugin Manager code is located at [here](https://github.com/hyperledger/indy-plenum/blob/master/plenum/server/notifier_plugin_manager.py#L23).

### Events Emitted

- .nodeRequestSpike : NodeRequestSuspiciousSpike
- .clusterThroughputSpike : ClusterThroughputSuspiciousSpike
- .clusterLatencyTooHigh : ClusterLatencyTooHigh
- .nodeUpgradeScheduled : NodeUpgradeScheduled
- .nodeUpgradeComplete : NodeUpgradeComplete
- .nodeUpgradeFail :  NodeUpgradeFail
- .poolUpgradeCancel :  PoolUpgradeCancel

## Plugins

No official plugins exist, however you are free to create your own plugins to suit our needs.