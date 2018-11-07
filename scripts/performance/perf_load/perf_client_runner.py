from perf_load.perf_client_msgs import ClientRun, ClientGetStat


class ClientRunner:
    ClientError = 0
    ClientCreated = 1
    ClientReady = 2
    ClientRun = 3
    ClientStopped = 4

    def __init__(self, name, conn, out_file):
        self.status = ClientRunner.ClientCreated
        self.name = name
        self.conn = conn
        self.total_sent = 0
        self.total_succ = 0
        self.total_failed = 0
        self.total_nack = 0
        self.total_reject = 0
        self._out_file = out_file

    def stop_client(self):
        self.status = ClientRunner.ClientStopped

    def is_finished(self):
        return self.status == ClientRunner.ClientStopped

    def refresh_stat(self, stat):
        if not isinstance(stat, dict):
            return
        self.total_sent = stat.get("total_sent", self.total_sent)
        self.total_succ = stat.get("total_succ", self.total_succ)
        self.total_failed = stat.get("total_fail", self.total_failed)
        self.total_nack = stat.get("total_nacked", self.total_nack)
        self.total_reject = stat.get("total_rejected", self.total_reject)

    def run_client(self):
        try:
            if self.conn and self.status == ClientRunner.ClientReady:
                self.conn.send(ClientRun())
                self.status = ClientRunner.ClientRun
        except Exception as e:
            print("Sent Run to client {} error {}".format(self.name, e), file=self._out_file)
            self.status = ClientRunner.ClientError

    def req_stats(self):
        try:
            if self.conn and self.status == ClientRunner.ClientRun:
                self.conn.send(ClientGetStat())
        except Exception as e:
            print("Sent ClientGetStat to client {} error {}".format(self.name, e), file=self._out_file)
            self.status = ClientRunner.ClientError
