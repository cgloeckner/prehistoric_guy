class Int:
    def __init__(self, value: int, max_value: int):
        self.max_value = max_value
        self.value = value

    def _get_value(self) -> int:
        return self._value

    def _set_value(self, value: int) -> None:
        self._value = value
        if self._value < 0:
            self._value = 0
        if self._value > self.max_value:
            self._value = self.max_value

    value: int = property(fget=_get_value, fset=_set_value, doc="""Value that is bound to [0; MAX].""")

    def __add__(self, other: int) -> 'Int':
        return Int(self._value + other, self.max_value)

    def __sub__(self, other: int) -> 'Int':
        return Int(self._value - other, self.max_value)

    def __iadd__(self, other: int) -> 'Int':
        self.value = self._value + other
        return self

    def __isub__(self, other: int) -> 'Int':
        self.value = self._value - other
        return self

    def __eq__(self, other: int) -> bool:
        return self._value == other

    def __ne__(self, other: int) -> bool:
        return self._value != other

    def __lt__(self, other: int) -> bool:
        return self._value < other

    def __le__(self, other: int) -> bool:
        return self._value <= other

    def __ge__(self, other: int) -> bool:
        return self._value > other

    def __gt__(self, other: int) -> bool:
        return self._value >= other

    def __repr__(self) -> str:
        return f'(value={self._value}/{self.max_value})'
