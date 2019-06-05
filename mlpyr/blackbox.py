import inspect
import types
import typing

import pygtrie


class _Blackbox:
    blackbox: pygtrie.StringTrie

    def __init__(self):
        self.blackbox = pygtrie.StringTrie(separator=".")

    @staticmethod
    def get_path(value: typing.Any) -> str:
        path = inspect.getmodule(value).__name__
        if callable(value):
            if hasattr(value, "__name__"):
                path += "." + value.__name__
        return path

    def register_blackbox(self, value: typing.Union[str, typing.Any], flag=True) -> None:
        """
        :param value: string or object for get_path
        :param flag: Whether or not to blackbox; allows for selective un-black-boxing.
        :return: None
        """
        if isinstance(value, str):
            self.blackbox[value] = flag
        else:
            self.blackbox[_Blackbox.get_path(value)] = flag

    def is_blackboxed(self, value: typing.Union[str, typing.Any]) -> bool:
        path = value if isinstance(value, str) else _Blackbox.get_path(value)
        result = self.blackbox.longest_prefix(path)
        if result:
            return result.value
        return False


Blackbox = _Blackbox()
