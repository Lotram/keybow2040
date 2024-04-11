import math


def xy_to_number(x, y, row_size):
    return y + (x * row_size)


def number_to_xy(idx, row_size):
    # Convert a idx to an x/y coordinate.
    y = idx % row_size
    x = idx // row_size
    return (x, y)


class Matrix:
    def __init__(self, *iterable):
        # cannot inherit from tuple, as it does not have a __getitem__ method in circuitpython
        self._tuple = tuple(iterable)
        self.row_size = int(math.sqrt(len(self._tuple)))

    def xy_to_number(self, x, y):
        # Convert an x/y coordinate to key idx.
        return xy_to_number(x, y, self.row_size)

    def number_to_xy(self, idx):
        return number_to_xy(idx, self.row_size)

    def __getitem__(self, item):
        if isinstance(item, tuple) and len(item) == 2:
            return self.__getitem__(self.xy_to_number(*item))

        return self._tuple[item]

    def __str__(self) -> str:
        return str(self._tuple)

    def __len__(self) -> str:
        return len(self._tuple)

    def __repr__(self) -> str:
        return repr(self._tuple)


def partial(func, *args, **kwargs):
    """Creates a partial of the function"""

    def _partial(*more_args, **more_kwargs):
        local_kwargs = kwargs.copy()
        local_kwargs.update(more_kwargs)
        return func(*(args + more_args), **local_kwargs)

    return _partial
