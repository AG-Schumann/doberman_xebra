from Doberman import LANDevice, utils
import re  # EVERYBODY STAND BACK xkcd.com/208


class cryocon_22c(LANDevice):
    """
    Cryogenic controller
    """
    accepted_commands = [
        'set setpoint <value>: change the setpoint',
    ]

    def set_parameters(self):
        self._msg_end = ';\n'
        self.commands = {  # these are not case sensitive
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
        self.value_pattern = re.compile(('(?P<value>%s)' % utils.number_regex).encode())
        self.command_patterns = [
            (re.compile(r'setpoint (?P<ch>1|2) (?P<value>%s)' % utils.number_regex),
             lambda x: self.commands['setSP'].format(**x.groupdict())),

        ]
