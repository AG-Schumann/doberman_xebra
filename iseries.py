from Doberman import SerialDevice, utils
import re  # EVERYBODY STAND BACK xkcd.com/208


class iseries(SerialDevice):
    """
    iseries sensor
    """

    def set_parameters(self):
        self._msg_start = '*'
        self._msg_end = '\r\n'
        self.commands = {
                'hardReset' : 'Z02',  # give the device a minute after this
                'getID' : 'R05',
                'getAddress' : 'R21',
                'getDataString' : 'V01',
                'getDisplayedValue' : 'X01',
                'getCommunicationParameters' : 'R10',
                }
        self.value_pattern = re.compile(f'{self.commands["getDisplayedValue"]}(?P<value>{utils.number_regex})'.encode())
