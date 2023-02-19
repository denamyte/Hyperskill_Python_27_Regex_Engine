from abc import ABC, abstractmethod
from typing import List


def main():
    patterns, text = input().split('|')
    print(Regex(patterns).start_match(text))


class RegexEntity(ABC):
    def __init__(self, pattern: str):
        self._pattern = pattern

    @abstractmethod
    def apply(self, text: str) -> List[int]:
        """
        Try to apply the regex against the text and return all possible
        indexes where the regex ends matching the text.
        If en empty list is returned, no matches are found.
        """
        ...


class Regex:
    def __init__(self, patterns: str):
        self._entities = self._parse_entities(patterns)

    @staticmethod
    def _parse_entities(patterns: str) -> List[RegexEntity]:
        index = 0
        entities = []
        text = ''
        while index < len(patterns):
            match patterns[index]:
                case '.':
                    if text:
                        entities.append(RegexText(text))
                    entities.append(RegexDot())
                    text = ''
                    index += 1
                case a:
                    text += a
                    index += 1
        if text:
            entities.append(RegexText(text))

        return entities

    def start_match(self, text: str) -> bool:
        return self._matches(self._entities, text, 0)

    @staticmethod
    def _matches(regexes: List[RegexEntity], text: str, index: int) -> bool:
        if not regexes:
            return True
        if not text:
            return False

        indexes = regexes[0].apply(text)
        for i in indexes:
            if Regex._matches(regexes[1:], text[i:], i):
                return True
        return False


class RegexDot(RegexEntity):
    def __init__(self):
        super().__init__('.')

    def apply(self, text: str):
        return [1]


class RegexText(RegexEntity):
    def __init__(self, text: str):
        super().__init__(text)

    def apply(self, text: str):
        end = len(self._pattern)
        return [end] if text[:end] == self._pattern else []


if __name__ == '__main__':
    main()
