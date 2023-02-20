from abc import ABC, abstractmethod
from typing import List, Iterable, Tuple
from enum import Enum


class Mode(Enum):
    SEARCH = 'S'
    MATCH = 'M'


RANGES = {'?': [0, 1],
          '*': [0, 0],
          '+': [1, 0]}


def main():
    patterns, text = input().split('|')
    print(Regex(patterns).start_match(text))


class RegexEntity(ABC):
    def __init__(self, pattern: str, mode: Mode):
        self._pattern = pattern
        self.mode = mode
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
        self._parse_entities(patterns)

    def _parse_entities(self, patterns: str):
        mode = Mode.SEARCH
        index = 0
        while index < len(patterns):
            match patterns[index]:
                case '\\':
                    len(patterns) > 1 and self._entities.append(
                        RegexChar(patterns[index + 1], mode))
                    index += 1
                case '^':
                    ...
                case '$':
                    self._entities and self._entities[-1].should_be_last()
                    break
                case '.':
                    self._entities.append(RegexDot(mode))
                case a if a in '?*+':
                    if self._entities:
                        last = self._entities[-1]
                        self._entities = self._entities[:-1] + [
                            RegexRepetition(a, mode, last, RANGES[a])
                        ]
                case a:
                    self._entities.append(RegexChar(a, mode))
            mode = Mode.MATCH
            index += 1

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
        if self.mode == Mode.MATCH:
            return [1]
        if self._last:
            return [len(text)]
        return list(range(1, len(text) + 1))


class RegexChar(RegexEntity):
    def __init__(self, text: str, mode: Mode):
        super().__init__(text, mode)

    def apply(self, text: str):
        rng = [0] if self.mode == Mode.MATCH else range(len(text))
        indexes = [i + 1 if self._pattern == text[i] else -1 for i in rng]
        return list(filter(lambda x: x > -1 if not self._last else x == len(text), indexes))


class RegexRepetition(RegexEntity):
    def __init__(self, pattern: str, mode: Mode, entity: RegexEntity,
                 rng: Tuple[int, int]):
        super().__init__(pattern, mode)
        self._entity = entity
        self._range = rng

    def mode(self, m: Mode):
        super().mode = m
        self._entity.mode = m

    def apply(self, text: str) -> Iterable[int]:
        length = len(text)
        res_indices = [] if self._range[0] else [0]  # none-existence of entity is included
        drop_matches = 0 if not self._range[0] else self._range[0] - 1
        max_matches = self._range[1] or length
        while text and max_matches:
            ent_indices = self._entity.apply(text)
            if not ent_indices:
                break
            ind = list(ent_indices)[0]
            if drop_matches:
                drop_matches -= 1
            else:
                res_indices.append(length - len(text) + ind)
            text = text[ind:]
            max_matches -= 1

        return res_indices if not self._last \
            else [length] if length in res_indices \
            else []


if __name__ == '__main__':
    main()
