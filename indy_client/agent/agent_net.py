from indy_client.agent.endpoint import ZEndpoint


class AgentNet:
    """
    Mixin for Agents to encapsulate the network interface to communicate with
    other agents.
    """

    def __init__(self, name, port, msgHandler, config, basedirpath=None,
                 endpoint_args=None):
        if port:
            endpoint_args = endpoint_args or {}
            seed = endpoint_args.get('seed')
            onlyListener = endpoint_args.get('onlyListener', False)
            self.endpoint = ZEndpoint(port=port,
                                      msgHandler=msgHandler,
                                      name=name,
                                      basedirpath=basedirpath,
                                      seed=seed,
                                      onlyListener=onlyListener)
        else:
            self.endpoint = None
