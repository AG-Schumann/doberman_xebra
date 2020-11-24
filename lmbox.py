from Doberman import SerialSensor
import struct

class lmbox(SerialSensor):
    """
    Custom level meter box for pancake
    """

    def set_parameters(self):
        self._msg_start = ''
        self._msg_end = '\r\n'

    def process_one_reading(self, name, data):
        if len(data) != 55:
            self.logger.debug(f'length of data is not 55. Will ignore this reading')
            return
        decoded = struct.unpack('<'+6*(4*'h'+'c')+'c', data)
        c_meas = []
        for i in range(5):
            lm_values = decoded[5*i:5*i+4]
            offset_values = sorted(lm_values)[:2]
            n_off = sum(offset_values)
            index_min = lm_values.index(min(offset_values))
            index = (index_min+2)%4 if lm_values[(index_min+1)%4] in offset_values else (index_min+1)%4
            n_ref = lm_values[index]
            n_x = lm_values[(index+1)%4]
            c_meas.append(self.c_ref[i]*(n_x-n_off)/(n_ref-n_off))
        return c_meas


