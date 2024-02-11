class NotFoundCryptoToken(Exception):
    """
    Кастомное исключение.
    Вызывается, если в системе нет такой крипто-сети
    """
    def __init__(self, *args: str | None) -> None:
        self.message = args[0] if args else None

    def __str__(self) -> str:
        return f'{self.message}'
