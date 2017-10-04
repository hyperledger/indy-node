from indy_client.agent.endpoint import REndpoint, ZEndpoint


class AgentNet:
    """
    Mixin for Agents to encapsulate the network interface to communicate with
    other agents.
    """

    def __init__(self, name, port, msgHandler, config, basedirpath=None,
                 endpoint_args=None):
        if port:
            if config.UseZStack:
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
                self.endpoint = REndpoint(port=port,
                                          msgHandler=msgHandler,
                                          name=name,
                                          basedirpath=basedirpath)
        else:
            self.endpoint = None
