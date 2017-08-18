from abc import abstractmethod


class GeneratesRequest:
    @abstractmethod
    def _op(self):
        pass

    @abstractmethod
    def ledgerRequest(self):
        """
        Generates a Request object to be submitted to the ledger.
        :return: a Request to be submitted, or None if it shouldn't be written
        """
