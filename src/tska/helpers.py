import dataclasses
import difflib
import pathlib
from typing import Iterable


@dataclasses.dataclass(frozen=True)
class Result:
    path: pathlib.Path
    old_content: str
    new_content: str

    @property
    def has_changes(self) -> bool:
        return self.old_content != self.new_content

    def write(self) -> None:
        self.path.write_text(self.new_content)

    def unified_diff(self) -> Iterable[str]:
        return difflib.unified_diff(
            self.old_content.splitlines(),
            self.new_content.splitlines(),
            f"old {self.path}",
            f"new {self.path}",
        )

    def display_diff_and_maybe_write(self, write: bool) -> bool:
        if not self.has_changes:
            return False
        for line in self.unified_diff():
            print(line)
        if write:
            self.write()
        return True
