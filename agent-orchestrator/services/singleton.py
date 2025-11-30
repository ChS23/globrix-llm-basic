class SingletonMeta(type):
    _instances = {}

    def __call__(cls, *args, **kwargs):
        if cls not in cls._instances:
            instance = super().__call__(*args, **kwargs)
            cls._instances[cls] = instance
        return cls._instances[cls]

    @classmethod
    def reset_instance(cls, target_class):
        """Сброс инстанса для тестирования"""
        if target_class in cls._instances:
            del cls._instances[target_class]
