from Doberman import SerialDevice
import struct

class lmbox(SerialDevice):
    """
    Custom level meter box for XeBRA
    """

    def set_parameters(self):
        self.eol = 13
        self.split = b'\x06'

    def process_one_value(self, name, data):

        """
               Data structure: 6 times 4 integers divided by the split character plus the EOL-character.
               """
        if data[-1] == self.eol:
            data = data[:-1]
            if len(data) != 54:
                self.logger.debug(f'data legth is {len(data)} not 54. Trying to salvage...')
                data = self.salvage_input(data)
                if len(data) != 54:
                    self.logger.debug(f'salvaging unsuccessful, length is {len(data)} not 54')
                    return
        else:
            self.logger.debug('data does not end with EOL')
            return
        decoded = struct.unpack('<' + 6 * (4 * 'h' + 'c'), data)
        c_meas = []
        for i in range(6):
            lm_values = decoded[5 * i:5 * i + 4]
            offset_values = sorted(lm_values)[:2]
            n_off = sum(offset_values)
            index_min = lm_values.index(min(offset_values))
            index = (index_min + 2) % 4 if lm_values[(index_min + 1) % 4] in offset_values else (index_min + 1) % 4
            n_ref = lm_values[index]
            n_x = lm_values[(index + 1) % 4]
            c_meas.append(self.c_ref[i] * (n_x - n_off) / (n_ref - n_off))
        return c_meas


def salvage_input(self, data):
    """
    This may or may not salvage some reading if the length of the data doesn't fit the normal
    structure.
    """
    place_holder = b'\x02\x00\x02\x00\x05\x00\x03\x00'
    data_temp = data.split(self.split)[:-1]
    data_list = [p if len(p) == 8 else place_holder for p in data_temp]
    data = self.split.join(data_list) + self.split
    return data