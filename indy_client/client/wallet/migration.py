from abc import ABCMeta

from jsonpickle import tags


class BaseWalletRawMigration(metaclass=ABCMeta):

    def _traverse_dict(self, d):
        for key in d:
            self._traverse_object(d[key])

    def _traverse_list(self, l):
        for item in l:
            self._traverse_object(item)

    def _traverse_object(self, v):
        if isinstance(v, dict):
            self._traverse_dict(v)
        elif isinstance(v, list):
            self._traverse_list(v)

    def try_apply(self, raw):
        self._traverse_object(raw)


class TerminologyWalletRawMigration(BaseWalletRawMigration):

    _LINK_FIELD_RENAMINGS = {
        'linkStatus': 'connection_status',
        'linkLastSynced': 'connection_last_synced',
        'linkLastSyncNo': 'connection_last_sync_no',
        'invitationNonce': 'request_nonce',

        # rule for the intermediate renaming state (MGL version)
        'connectionLastSynced': 'connection_last_synced'
    }

    def __process_wallet(self, wallet):
        if '_links' in wallet:
            wallet['_connections'] = wallet.pop('_links')

    def __process_link(self, link):
        link[tags.OBJECT] = \
            'sovrin_client.client.wallet.connection.Connection'
        for key in link:
            if key in self._LINK_FIELD_RENAMINGS:
                link[self._LINK_FIELD_RENAMINGS[key]] = link.pop(key)

    def _traverse_dict(self, d):
        if d.get(tags.OBJECT) == 'sovrin_client.client.wallet.wallet.Wallet':
            self.__process_wallet(d)
        if d.get(tags.OBJECT) == 'sovrin_client.client.wallet.link.Link':
            self.__process_link(d)
        super()._traverse_dict(d)


class RebrandingWalletRawMigration(BaseWalletRawMigration):

    def __process_did_methods(self, didMethods):
        if 'd' in didMethods:
            d = didMethods['d']
            if isinstance(d, dict) and 'sovrin' in d:
                d['indy'] = d.pop('sovrin')

    def __process_did_method(self, didMethod):
        if 'name' in didMethod and isinstance(didMethod['name'], str):
            didMethod['name'] = \
                didMethod['name'].replace('sovrin', 'indy')
        if 'pattern' in didMethod and isinstance(didMethod['pattern'], str):
            didMethod['pattern'] = \
                didMethod['pattern'].replace('sovrin', 'indy')

    def _traverse_dict(self, d):
        if tags.OBJECT in d:
            if d[tags.OBJECT] == 'plenum.common.did_method.DidMethods':
                self.__process_did_methods(d)
            if d[tags.OBJECT] == 'plenum.common.did_method.DidMethod':
                self.__process_did_method(d)

            if isinstance(d[tags.OBJECT], str):
                d[tags.OBJECT] = \
                    d[tags.OBJECT].replace('sovrin', 'indy')
                d[tags.OBJECT] = \
                    d[tags.OBJECT].replace('Sovrin', 'Indy')

        super()._traverse_dict(d)


class MultiNetworkWalletRawMigration(BaseWalletRawMigration):

    def __process_wallet(self, wallet):
        if wallet.get('env') == 'test':
            wallet['env'] = 'sandbox'

    def _traverse_dict(self, d):
        if d.get(tags.OBJECT) == 'indy_client.client.wallet.wallet.Wallet':
            self.__process_wallet(d)
        super()._traverse_dict(d)


def migrate_indy_wallet_raw(raw):
    TerminologyWalletRawMigration().try_apply(raw)
    RebrandingWalletRawMigration().try_apply(raw)
    MultiNetworkWalletRawMigration().try_apply(raw)
