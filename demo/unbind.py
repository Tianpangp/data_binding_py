import re

from data_binding import Bindable, BindManager, BindType


class ModA(Bindable):
    def __init__(self):
        super().__init__()
        self._data: str = ''

    @property
    def data(self):
        return self._data

    @data.setter
    def data(self, value):
        self._data = value
        self.notify('data')


class ModB(Bindable):
    def __init__(self):
        super().__init__()
        self._data: bytes = b''

    @property
    def data(self):
        return self._data

    @data.setter
    def data(self, value):
        self._data = value
        self.notify('data')


def bytes_to_hex_styled(bytes):
    return ' '.join('%02x' % b for b in bytes)


def hex_to_bytes(hex_str):
    hex_str = hex_str.replace(' ', '')
    pattern = r'^[0-9a-fA-F]+$'
    if not re.match(pattern, hex_str):
        raise ValueError
    return bytes.fromhex(hex_str)


if __name__ == '__main__':
    mod_a = ModA()
    mod_b = ModB()
    BindManager.bind(mod_a, 'data', mod_b, 'data', BindType.ONE_WAY, (hex_to_bytes, None))

    mod_a.data = 'aa ff'
    print(f'mod_b.data: {mod_b.data}')

    BindManager.unbind(mod_a, 'data', mod_b, 'data')

    mod_a.data = 'bb ff'
    print(f'mod_b.data: {mod_b.data}')