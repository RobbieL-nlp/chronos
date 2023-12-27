class Meta(type):
    def __new__(cls, name, base, dict, **kwargs):
        cls_ = super().__new__(cls, name, base, dict)
        for k, v in kwargs:
            setattr(cls_, cls.field_name(k), v)
        return cls_

    @staticmethod
    def field_name(name: str):
        return f"__meta_{name}__"
