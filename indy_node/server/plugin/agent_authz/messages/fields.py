from indy_common.config_util import getConfig
from indy_node.server.plugin.agent_authz.helper import is_prime
from plenum.common.messages.fields import NonNegativeNumberField, ChooseField


# This line causes config problems
# config = getConfig()


class CappedNumberField(NonNegativeNumberField):
    def __init__(self, max_val: int, **kwargs):
        super().__init__(**kwargs)
        self._max_val = max_val

    def _specific_validation(self, val):
        err = super()._specific_validation(val)
        if err:
            return err
        if val > self._max_val:
            return '{} should not be greater than {}'.format(val, self._max_val)


class AgentAuthzPolicyAddressField(CappedNumberField):
    _base_types = (int, str)

    def _specific_validation(self, val):
        if isinstance(val, str):
            try:
                val = int(val)
            except ValueError as ex:
                return str(ex)
        return super()._specific_validation(val)


class AgentAuthzAuthorisationField(CappedNumberField):
    _base_types = (int, )


class AgentAuthzCommitmentField(CappedNumberField):
    _base_types = (int, str)

    def _specific_validation(self, val):
        if isinstance(val, str):
            try:
                val = int(val)
            except ValueError as ex:
                return str(ex)
        err = super()._specific_validation(val)
        if err:
            return err
        if not is_prime(val):
            return 'should be prime, found {} instead'.format(val)


class AgentAuthzAccumIdField(ChooseField):
    base_types = (int,)

    def __init__(self, *accum_ids, **kwargs):
        self.accum_ids = accum_ids
        super().__init__(self.accum_ids, **kwargs)
