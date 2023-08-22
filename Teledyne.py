from Doberman import LANDevice, utils
import re  # EVERYBODY STAND BACK xkcd.com/208


class Teledyne(LANDevice):
    """
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

