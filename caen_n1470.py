from Doberman import SerialDevice, utils
import re  # EVERYBODY STAND BACK xkcd.com/208
from itertools import product
import serial
import time

class caen_n1470(SerialDevice):
    """
    Connects to the CAEN N1470. Command syntax:
    '$BD:<board number>,CMD:<MON,SET>,CH<channel>,PAR:<parameter>[,VAL:<%.2f>]\\r\\n'
    Return syntax:
    error:
    '#BD:<board number>,<error type>:ERR'
    correct:
    '#BD:<board number>,CMD:OK[,VAL:<value>[,<value>...]]'
    """
    accepted_commands = [
        '<anode|cathode|screen> <on|off>',
        '<anode|cathode|screen> <value>',
    ]
    msg_wait = 0.1  # Seconds to wait for response
    recv_interval = 0.01  # Socket polling interval
    eol = b'\r\n'

    def set_parameters(self):
        self._msg_start = '$'
        self._msg_end = '\r\n'
        self.setcommand = f'BD:{self.params["board"]},CMD:SET,' + 'CH:{ch},PAR:{par},VAL:{val}'
        self.powercommand = f'BD:{self.params["board"]},CMD:SET,' + 'CH:{ch},PAR:{par}'
        self.value_pattern = re.compile(f'OK,VAL:(?P<value>{utils.number_regex})'.encode())

    def setup(self):
        self._device = serial.Serial()
        self._device.baudrate = 9600 if not hasattr(self, 'baud') else self.baud
        self._device.parity = serial.PARITY_NONE
        self._device.stopbits = serial.STOPBITS_ONE
        self._device.timeout = self.msg_wait 
        self._device.write_timeout = 0
        if hasattr(self, 'id'):
            self._device.port = f'/dev/serial/by-id/{self.id}'
        elif self.tty == '0':
            raise ValueError('No id nor tty port specified!')
        elif self.tty.startswith('/'):  # Full path to device TTY specified
            self._device.port = self.tty
        else:
            self._device.port = f'/dev/tty{self.tty}'
        try:
            self._device.open()
            self._device.reset_output_buffer()
        except serial.SerialException as e:
            raise ValueError(f'Problem opening {self._device.port}: {e}')
        if not self._device.is_open:
            raise ValueError('Error while connecting to device')

    def execute_command(self, quantity, value):
        ch, q = quantity.split('_')  # split anode_status, anode_setpoint, etc.
        if ch in self.params['channel_map']:
            if q == 'status':
                if value in ['0', 'off', 'OFF']:
                    return self.powercommand.format(ch=self.params['channel_map'][ch], par='OFF')
                elif value in ['1', 'on', 'ON']:
                    return self.powercommand.format(ch=self.params['channel_map'][ch], par='ON')
            elif q == 'setpoint':
                return self.setcommand.format(ch=self.params['channel_map'][ch], par='VSET', val=value)

    
    def send_recv(self, message, dev=None):
        device = dev if dev else self._device
        ret = {'retcode': 0, 'data': None}
        message = f'{self._msg_start}{message}{self._msg_end}'
        try:
            device.write(message.encode())
        except Exception as e:
            self.logger.error(f'Could not send message: {message}. Got an {type(e)}: {e}')
            ret['retcode'] = -2
            return ret
        try:
            data = self._receive_data(device)
            ret['data'] = data
        except Exception as e:
            self.logger.error(f'Could not receive data from device. {e}')
            ret['retcode'] = -2
        if not data:
            self.logger.info('Didn\'t get anything from device. Reestablishing connection')
            device.close()
            time.sleep(0.1)
            device.open()
            device.read(1024)
        return ret

    def _receive_data(self, device):
        data = b''
        end_time = time.time() + self.msg_wait

        while time.time() < end_time:
            if device.in_waiting:
                data += device.read(device.in_waiting)
              
            if data.endswith(self.eol):
                break
            time.sleep(self.recv_interval)
        if not data.endswith(self.eol):
            data = None
        self.logger.debug(f'Got {data}, ({(time.time()-end_time+self.msg_wait)*1000:.1f} ms)')
        return data
