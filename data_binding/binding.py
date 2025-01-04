from enum import Enum
from typing import Union


class BindingException(Exception):
    def __init__(self, msg):
        super().__init__(msg)


class BindType(Enum):
    ONE_WAY = 0
    TWO_WAY = 1


class BindInfo:
    """
    bind info
    """

    def __init__(self, data_provider, src_prop: Union[str, callable], data_receiver, dst_prop: Union[str, callable],
                 converter: callable = None):
        """
        bind info

        :param data_provider: data provider
        :param src_prop: bind property in data provider
        :param data_receiver: data receiver
        :param dst_prop: bind property in data receiver
        :param converter: converter function
        """
        self.data_provider = data_provider
        self.src_prop = src_prop
        self.data_receiver = data_receiver
        self.dst_prop = dst_prop
        self.converter = converter

    def _get_src_prop(self):
        if isinstance(self.src_prop, str):
            return getattr(self.data_provider, self.src_prop)
        elif callable(self.src_prop):
            return self.src_prop()
        raise BindingException(f"property {self.src_prop} type invalid, must be str or callable")

    def _set_dst_prop(self, value):
        if isinstance(self.dst_prop, str):
            setattr(self.data_receiver, self.dst_prop, value)
        elif callable(self.dst_prop):
            self.dst_prop(value)
        else:
            raise BindingException(f"property {self.dst_prop} type invalid, must be str or callable")

    def _get_dst_prop(self):
        if isinstance(self.dst_prop, str):
            return getattr(self.data_receiver, self.dst_prop)
        raise BindingException(f"property {self.dst_prop} type invalid, must be str or callable")

    def _do_converter(self, value):
        if self.converter is None:
            return value
        return self.converter(value)

    def update(self):
        if callable(self.dst_prop) or not (self._get_dst_prop() == self._do_converter(self._get_src_prop())):
            self._set_dst_prop(self._do_converter(self._get_src_prop()))

    def is_equal(self, other, is_compare_converter: bool = True):
        is_equal = self.src_prop == other.src_prop and self.data_receiver == other.data_receiver and self.dst_prop == other.dst_prop
        if not is_equal:
            return False
        if is_compare_converter:
            return self.converter == other.converter
        return True


class BindManager:
    @staticmethod
    def bind(data_provider, src_prop: Union[str, callable], data_receiver, dst_prop: Union[str, callable],
             bind_type: BindType,
             converter: tuple[callable, callable] = None):
        """
        bind two property

        :param data_provider: data provider
        :param src_prop: bind property in data provider
        :param data_receiver: data receiver
        :param dst_prop: bind property in data receiver
        :param bind_type: bind type ONE_WAY or TWO_WAY, if any of src_prop or dst_prop is callable, bind_type must be ONE_WAY
        :param converter: converter tuple (to src, to dst)
        :return: None
        """
        # valid check
        if not isinstance(data_provider, Bindable) or not isinstance(data_receiver, Bindable):
            raise BindingException("data_provider and data_consumer must be Bindable")
        if not hasattr(data_provider, src_prop if isinstance(src_prop, str) else src_prop.__name__):
            raise BindingException(f"property {src_prop} not exists in data_provider")
        if not hasattr(data_receiver, dst_prop if isinstance(dst_prop, str) else dst_prop.__name__):
            raise BindingException(f"property {dst_prop} not exists in data_receiver")
        if (callable(src_prop) or callable(dst_prop)) and bind_type == BindType.TWO_WAY:
            raise BindingException("two way bind must use property name")
        # bind
        data_provider.register_subscription(BindInfo(data_provider, src_prop, data_receiver, dst_prop, converter[0]))
        if bind_type == BindType.TWO_WAY:
            data_receiver.register_subscription(
                BindInfo(data_receiver, dst_prop, data_provider, src_prop, converter[1]))

    @staticmethod
    def unbind(data_provider, src_prop, data_receiver, dst_prop):
        """
        unbind two property

        :param data_provider: data provider
        :param src_prop: bind property in data provider
        :param data_receiver: data receiver
        :param dst_prop: bind property in data receiver
        :return: None
        """
        data_provider.unregister_subscription(BindInfo(data_provider, src_prop, data_receiver, dst_prop))
        data_receiver.unregister_subscription(BindInfo(data_receiver, dst_prop, data_provider, src_prop))

    @staticmethod
    def change_converter(data_provider, src_prop: Union[str, callable], data_receiver, dst_prop: Union[str, callable], bind_type: BindType,
                         converter: tuple[callable, callable]):
        data_provider.unregister_subscription(BindInfo(data_provider, src_prop, data_receiver, dst_prop))
        data_provider.register_subscription(BindInfo(data_provider, src_prop, data_receiver, dst_prop, converter[0]))
        if bind_type == BindType.TWO_WAY:
            data_receiver.unregister_subscription(BindInfo(data_receiver, dst_prop, data_provider, src_prop))
            data_receiver.register_subscription(BindInfo(data_receiver, dst_prop, data_provider, src_prop, converter[1]))


class Bindable:
    def __init__(self):
        self.subscriptions: list[BindInfo] = []

    def register_subscription(self, subscription):
        for sub in self.subscriptions:
            if sub.is_equal(subscription):
                return
        self.subscriptions.append(subscription)

    def unregister_subscription(self, subscription):
        for sub in self.subscriptions:
            if sub.is_equal(subscription, False):
                self.subscriptions.remove(sub)

    def notify(self, prop: Union[str, callable]):
        for sub in self.subscriptions:
            if sub.src_prop == prop:
                sub.update()
