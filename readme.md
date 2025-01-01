# 数据绑定 data binding

这个module用来绑定两个对象中的两个属性，或者2个函数，实现自动更新，更新过程中自动进行数据转换

This module is used to bind two properties between two objects or two functions, enabling automatic updates and data transformation during the update process.

示例：

Sample: 

```python
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
```

如上面示例，有`mod_a`和`mod_b`两个`Bindable`对象，绑定了其中的属性data，并指定类型和转换函数

As in the example above, there are two `Bindable` objects, `mod_a` and `mod_b`, where their data properties are bound together with specified types and transformation functions.

使用方法非常简单，可以看demo源码

The usage is very straightforward; you can check out the demo source code.