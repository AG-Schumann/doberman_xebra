from Doberman import SerialSensor, utils
import re  # EVERYBODY STAND BACK xkcd.com/208


class Teledyne(SerialSensor):
    """
    NOT ADJUSTED FOR DOBERMAN 6 since the device isn't working anymore
    Teledyne flow controller
    THCD-100
    """
    accepted_commands = [
            'setpoint <value>: change setpoint',
            'valve <auto|open|close>: change valve status',
        ]
    def set_parameters(self):
        self._msg_end = '\r\n'
        self.commands = {
                'Address' : 'add',
                'read' : 'r',
                'SetpointMode' : 'spm',
                'Unit' : 'uiu',
                'SetpointValue' : 'spv'
                }
        self.basecommand = f'{self.device_address}' + '{cmd}'
        self.setcommand = self.basecommand + ' {params}'
        self.getcommand = self.basecommand + '?'

        self.reading_pattern = re.compile(('READ: *(?P<value>%s)' %
                                            utils.number_regex).encode())
        self.get_addr = re.compile(b'ADDR: *(?P<addr>[a-z])')
        self.command_echo = f'\\*{self.device_address}\\*:' + '{cmd} *;'
        self.retcode = f'!{self.device_address}!(?P<retcode>[beow])!'

        self.setpoint_map = {'auto' : 0, 'open' : 1, 'close' : 2}
        self.reading_commands = {'flow' : self.basecommand.format(
                                    cmd=self.commands['read'])}
        self.command_patterns = [
                (re.compile(r'setpoint (?P<params>%s)' % utils.number_regex),
                    lambda x : self.setcommand.format(cmd=self.commands['SetpointValue'],
                        **x.groupdict())),
                (re.compile(r'valve (?P<params>auto|open|close)'),
                    lambda x : self.setcommand.format(cmd=self.commands['SetpointMode'],
                        params=self.setpoint_map[x.group('params')])),
                ]

    def is_this_me(self, dev):
        command = self.getcommand.format(cmd=self.commands['Address'])
        resp = self.SendRecv(command, dev)
        if resp['retcode'] or not resp['data']:
            return False
        m = self.get_addr.search(resp['data'])
        if not m:
            return False
        return self.device_address == m.group('addr').decode():
