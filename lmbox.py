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
            data = self.sanify_input(data)
        if len(data) != 55:
            return None
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

    def sanify_input(self, data):
        """
        Sometimes the lmbox returns more bytes than expected. The data is still intact, though,
        and can be decoded.
        """
        self.logger.debug(f'sanify input: {data}')
        place_holder=b'\x02\x00\x02\x00\x05\x00\x03\x00'
        data_tmp = data.split(b'\x06')
        self.logger.debug(f'data_temp: {data_tmp}')
        data_list = [p if len(p)==8 or p==b'\r' else place_holder for p in data_tmp]
        self.logger.debug(f'data_list: {data_list}')
        data=b'\x06'.join(data_list)
        self.logger.debug(f'decoded: {data}, length: {len(data)}')
        return data
