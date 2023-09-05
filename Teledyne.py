from Doberman import LANDevice, utils
import re  # EVERYBODY STAND BACK xkcd.com/208


class Teledyne(LANDevice):
    """
    Teledyne flow controller
    THCD-100
    """
    accepted_commands = [
            'set setpoint <value>: change setpoint',
            'set valvemode <auto|open|close>: change valve status',
        ]

    def execute_command(self, quantity, value):
        if quantity == 'setpoint':
            return self.setcommand.format(cmd=self.commands['SetpointValue'], params=value)
        elif quantity == 'valvemode':
            value = int(value)
            return self.setcommand.format(cmd=self.commands['SetpointMode'], params=value)

    def do_one_measurement(self):
        """
        Asks the device for data, unpacks it, and sends it to the database
        """
        pkg = {}
        self.schedule(self.readout_command, ret=(pkg, self.cv))
        with self.cv:
            if self.cv.wait_for(lambda: (len(pkg) > 0 or self.event.is_set()), self.readout_interval):
                failed = False
            else:
                # timeout expired
                failed = len(pkg) == 0
        if len(pkg) == 0 or failed:
            #self.logger.debug(f'Didn\'t get anything from the device!')
            return
        try:
            value = self.device_process(name=self.name, data=pkg['data'])
        except (ValueError, TypeError, ZeroDivisionError, UnicodeDecodeError, AttributeError) as e:
            self.logger.debug(f'Got a {type(e)} while processing \'{pkg["data"]}\': {e}')
            value = None
        if value is not None:
            value = self.more_processing(value)
            self.send_downstream(value, pkg['time'])
        else:
            self.logger.debug(f'Got None')
        return


    def set_parameters(self):
        self._msg_end = '\r\n'
        self.commands = {
                'Address' : 'add',
                'read' : 'r',
                'SetpointMode' : 'spm',
                'Unit' : 'uiu',
                'SetpointValue' : 'spv'
                }
        self.basecommand = f'{self.params["device_address"]}' + '{cmd}'
        self.setcommand = self.basecommand + ' {params}'
        self.getcommand = self.basecommand + '?'

        self.value_pattern = re.compile(('(?P<value>%s)' %
                                            utils.number_regex).encode())
        self.get_addr = re.compile(b'ADDR: *(?P<addr>[a-z])')
        self.command_echo = f'\\*{self.params["device_address"]}\\*:' + '{cmd} *;'
        self.retcode = f'!{self.params["device_address"]}!(?P<retcode>[beow])!'

        self.setpoint_map = {'auto' : 0, 'open' : 1, 'close' : 2}
        self.reading_commands = {'flow' : self.basecommand.format(
                                    cmd=self.commands['read'])}


    def execute_command(self, quantity, value):
        if quantity == 'setpoint':
            return self.setcommand.format(cmd=self.commands['SetpointValue'], params=value)
        elif quantity == 'valvemode':
            value = int(value)
            return self.setcommand.format(cmd=self.commands['SetpointMode'], params=value)
