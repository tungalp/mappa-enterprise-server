from abc import ABC


class BaseService(ABC):
    """Tüm servislerin atası olarak kullanılacak olan sınıftır."""
    
    def __init__(self) -> None:
        ...