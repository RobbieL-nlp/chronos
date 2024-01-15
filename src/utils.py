from abc import ABCMeta


class Meta(ABCMeta):
    def __new__(cls, name, base, dict, **kwargs):
        cls_ = super().__new__(cls, name, base, dict)
        for k, v in kwargs.items():
            setattr(cls_, cls.field_name(k), v)
        return cls_

    @staticmethod
    def field_name(name: str):
        return f"__meta_{name}__"


def shift_0(num: int):
    """convert the num from 1 to 0 base, 0 always means first number"""
    return num - 1 if num > 0 else num


def reload_1(num: int):
    """convert the positive num from 0 base to  1"""
    return num + 1
