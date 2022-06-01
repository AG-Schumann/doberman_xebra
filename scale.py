from Doberman import SerialDevice, utils
import re

class scale(SerialDevice):
    """
    Large scale for XeBRA LN2 dewar
    """

    def set_parameters(self):
        self.value_pattern = re.compile((f'(?P<value>{utils.number_regex})kg').encode())
