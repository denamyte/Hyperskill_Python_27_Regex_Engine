from abc import ABC, abstractmethod
from typing import List, Iterable
from enum import Enum


class Mode(Enum):
    SEARCH = 'S'
    MATCH = 'M'


def main():
    patterns, text = input().split('|')
    print(Regex(patterns).start_match(text))


class RegexEntity(ABC):
    def __init__(self, pattern: str, mode: Mode):
        self._pattern = pattern
        self._mode = mode
        self._last = False

    def should_be_last(self):
        self._last = True

    @abstractmethod
    def apply(self, text: str) -> Iterable[int]:
        """
        Try to apply the regex against the text and return all possible
        indexes where the regex ends matching the text.
        If en empty list is returned, no matches are found.
        """
        ...


class Regex:
    def __init__(self, patterns: str):
        self._entities: List[RegexEntity] = []
        self._mode = Mode.SEARCH
        self._text = ''
        self._parse_entities(patterns)

    def _parse_entities(self, patterns: str):
        for index in range(len(patterns)):
            match patterns[index]:
                case '^':
                    self._mode = Mode.MATCH
                case '.':
                    self._check_text()
                    self._entities.append(RegexDot(self._mode))
                case '$':
                    self._check_text()
                    self._entities and self._entities[-1].should_be_last()
                    break
                case a:
                    self._text += a
        self._check_text()

    def _check_text(self):
        if self._text:
            self._entities.append(RegexText(self._text, self._mode))
            self._text = ''

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
    def __init__(self, mode: Mode):
        super().__init__('.', mode)

    def apply(self, text: str):
        if self._mode == Mode.MATCH:
            return [1]
        if self._last:
            return [len(text)]
        return list(range(1, len(text) + 1))


class RegexText(RegexEntity):
    def __init__(self, text: str, mode: Mode):
        super().__init__(text, mode)

    def apply(self, text: str):
        pt_len = len(self._pattern)
        if pt_len > len(text):
            return []
        rng = [0] if self._mode == Mode.MATCH \
            else range(len(text) - pt_len + 1)
        indexes = [pt_len + i if self._pattern == text[i:pt_len + i] else -1
                   for i in rng]
        return list(filter(lambda x: x > -1 if not self._last else x == len(text), indexes))


if __name__ == '__main__':
    main()
