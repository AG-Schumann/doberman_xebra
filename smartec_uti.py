from Doberman import SerialSensor
from subprocess import Popen, PIPE, TimeoutExpired
import re  # EVERYBODY STAND BACK
from itertools import repeat


class smartec_uti(SerialSensor):
    """
    Level meter sensors
    """

    def set_parameters(self):
        self.commands = {
                'greet' : '@',
                'help' : '?',
                'setSlow' : 's',
                'setFast' : 'f',
                'setMode0' : '0',
                'setMode1' : '1',
                'setMode2' : '2',
                'setMode4' : '4',
                'measure' : 'm',
                }
        self._msg_start = ''
        self._msg_end = '\r\n'

    def setup(self):
        self.send_recv(self.commands['greet'])
        self.send_recv(self.commands['setSlow'])
        self.send_recv(self.commands['setMode%s' % int(self.mode)])

    def is_this_me(self, dev):
        """
        The smartec serial protocol is very poorly designed, so we have to use
        dmesg to see if we found the right sensor
        """
        ttyUSB = int(dev.port.split('USB')[-1])
        proc = Popen('dmesg | grep ttyUSB%i | tail -n 1' % ttyUSB,
                shell=True, stdout=PIPE, stderr=PIPE)
        try:
            out, err = proc.communicate(timeout=5)
        except TimeoutExpired:
            proc.kill()
            out, err = proc.communicate()
        if not len(out) or len(err):
            self.logger.error('Could not check sensor! stdout: %s, stderr: %s' % (
                out.decode(), err.decode()))
            return False
        pattern = r'usb (?P<which>[^:]+):'
        match = re.search(pattern, out.decode())
        if not match:
            #self.logger.error('Could not find sensor')
            return False
        proc = Popen('dmesg | grep \'%s: SerialNumber\' | tail -n 1' % match.group('which'),
                shell=True, stdout=PIPE, stderr=PIPE)
        try:
            out, err = proc.communicate(timeout=5)
        except TimeoutExpired:
            proc.kill()
            out, err = proc.communicate()
        if not len(out) or len(err):
            #self.logger.error('Could not check sensor! stdout: %s, stderr: %s' % (
            #    out.decode(), err.decode()))
            pass
        if self.serialID in out.decode():
            return True
        return False

    def process_one_reading(self, name, data):
        """
        """
        values = data.decode().rstrip().split()
        values = list(map(lambda x : int(x,16), values))

        c_off = values[0]
        div = values[1] - values[0]
        self.logger.debug('UTI measured %s' % values)
        if div: # evals to (value[cde] - valuea)/(valueb - valuea)
            resp = [(v-c_off)/div*self.c_ref for v in values[2:]]
            self.logger.debug(f'Calculated response: {resp}')
            if len(resp) > 1:
                return resp
            return resp[0]
        return None

