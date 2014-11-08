from hwmonitors import MonitorWorker
from notifiers import Event
from network import NetworkInfo
import subprocess

CHECK_DRIVES = [
    '/dev/sda',
    '/dev/sdb',
    '/dev/sdc',
    '/dev/sdd',
    '/dev/sde'
]

class SMARTMonitor(MonitorWorker):

    def run(self):
        foundProblem = False
        problemDrive = "Problem in "
        for d in CHECK_DRIVES:
            result = self._call_smartctl(d)
            if (not result):
                foundProblem = True
                problemDrive = problemDrive + d + ', '

        if (foundProblem):
            net = NetworkInfo()
            event = Event("Smart Alert", problemDrive, net.fqdn)
            self.callback(event)

    def _call_smartctl(self, drive):
        try:
            smartctl_out = subprocess.check_output(['smartctl', '--health', drive])
            return ('PASSED' in str(smartctl_out))
        except:
            return False
