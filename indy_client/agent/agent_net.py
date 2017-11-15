#   Copyright 2017 Sovrin Foundation
#
#   Licensed under the Apache License, Version 2.0 (the "License");
#   you may not use this file except in compliance with the License.
#   You may obtain a copy of the License at
#
#       http://www.apache.org/licenses/LICENSE-2.0
#
#   Unless required by applicable law or agreed to in writing, software
#   distributed under the License is distributed on an "AS IS" BASIS,
#   WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#   See the License for the specific language governing permissions and
#   limitations under the License.
#

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
