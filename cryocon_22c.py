from Doberman import LANDevice, utils
import re  # EVERYBODY STAND BACK xkcd.com/208


class cryocon_22c(LANDevice):
    """
    Cryogenic controller
    """
    accepted_commands = [
        'set setpoint <value>: change the setpoint',
    ]

    eol = b'\n'
    _msg_end = ';\n'
    commands = {  # these are not case sensitive
        'identify': '*idn?',
        'getTempA': 'input? a:units k',
        'getTempB': 'input? b:units k',
        'getSP1': 'loop 1:setpt?',
        'getSP2': 'loop 2:setpt?',
        'getLp1Pwr': 'loop 1:htrread?',
        'getLp2Pwr': 'loop 2:htrread?',
        'setTempAUnits': 'input a:units k',
        'settempBUnits': 'input b:units k',
        'setSP': 'loop {ch}:setpt {value}',
    }
    value_pattern = re.compile(('(?P<value>%s)' % utils.number_regex).encode())
    
    def execute_command(self, quantity, value):
        if quantity == 'setpoint':
            return self.commands['setSP'].format(ch=1, value=value)
