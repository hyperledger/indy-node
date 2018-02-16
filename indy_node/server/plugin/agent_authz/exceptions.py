class NoAgentFound(Exception):
    reason = 'No agent found with address {} and verkey {}'

    def __init__(self, policy_address, agent_verkey):
        self.reason = self.reason.format(policy_address, agent_verkey)
