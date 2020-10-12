from Doberman import LANSensor, utils
import re  # EVERYBODY STAND BACK xkcd.com/208


class pfeiffer_tpg(LANSensor):
    def set_parameters(self):
        self._msg_begin = ''
        self._msg_end = '\r\n\x05'
        self.commands = {
                'identify' : 'AYT',
                'read' : 'PR1',
                }
        self.reading_commands = {'iso_pressure' : self.commands['read']}
        self.reading_pattern = re.compile(('(?P<status>[0-9]),(?P<value>%s)' %
                                                    utils.number_regex).encode())

    def setup(self):
        self.SendRecv(self.commands['identify'])
        # stops the continuous flow of data

    def is_this_me(self, dev):
        ret = self.SendRecv(self.commands['identify'], dev)
        if ret['retcode'] or ret['data'] is None:
            return False
        if self.serialID in ret['data'].decode().split(','):
            return True
        return False
