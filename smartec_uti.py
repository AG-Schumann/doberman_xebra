from Doberman import SerialDevice
from subprocess import Popen, PIPE, TimeoutExpired
import re  # EVERYBODY STAND BACK
from itertools import repeat


class smartec_uti(SerialDevice):
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
        self.send_recv(self.commands[f'setMode{int(self.params["mode"])}'])

    def process_one_value(self, name, data):
        """
        """
        values = data.decode().rstrip().split()
        values = list(map(lambda x : int(x,16), values))

        c_off = values[0]
        div = values[1] - values[0]
        #self.logger.debug(f'UTI measured {values}')
        if div: # evals to (value[cde] - valuea)/(valueb - valuea)
            resp = [(v-c_off)/div*self.params['c_ref'] for v in values[2:]]
            #self.logger.debug(f'Calculated response: {resp}')
            if len(resp) > 1:
                return resp
            return resp[0]
        return None

