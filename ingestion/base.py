from abc import ABC, abstractmethod
from typing import Dict, Iterable


class BaseIngestor(ABC):

    @abstractmethod
    def load(self) -> Iterable[Dict]:
        """
        Must yield normalized documents with the canonical schema.
        """
        pass
