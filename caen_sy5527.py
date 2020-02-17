import Doberman
import re


class caen_sy5527(Doberman.LANSensor):
    """
    Driver for the CAEN high-voltage crate
    """
    def SetParameters(self):
        self.channel_status = [
                'on',
                'ramp_up',
                'ramp_down',
                'overcurrent',
                'overvoltage',
                'undervoltage',
                'external_trip',
                'max_v',
                'external_disable',
                'internal_error',
                'calibration_error',
                'unplugged',
                ]
        self.command_patterns = [(re.compile('set ch(?P<ch>[1-9]?[0-9]) sl3 (?P<task>rup|rdn|tripi|tript|setp|vset|pon|pdn|pw) (?P<value>%s)' % Doberman.utils.number_regex),
            lambda m : m.group(0))]

        self.reading_pattern = re.compile(('OK;(?P<value>(?:%s,)*%s)\r\n' % 
            (Doberman.utils.number_regex, Doberman.utils.number_regex)).encode())

    def ProcessOneReading(self, name, data):
        m = self.reading_pattern.search(data)
        return list(map(float, m.group('value').decode().split(',')))[0]
