"""
Shift an import for a given name from a given module to another module.
"""

import argparse
import os
import pathlib
import re
import sys
from functools import partial

from tska.helpers import Result

es_import_re = re.compile(r"import\s+(.+?)\s+from\s+[\"'](.+)[\"'];$", re.MULTILINE)


def compute_relative_import(
    this_module_path: pathlib.Path,
    dest_module_path: pathlib.Path,
) -> str:
    rel_path = str(dest_module_path.relative_to(this_module_path.parent, walk_up=True))
    if not rel_path.startswith("."):
        rel_path = "./" + rel_path
    return os.path.splitext(rel_path)[0]


def process_import(
    m: re.Match,
    *,
    this_module_path: pathlib.Path,
    source_name: str,
    source_module: str,
    dest_module: str | pathlib.Path,
):
    is_default_name = not m.group(1).startswith("{")
    names = [name.strip() for name in m.group(1).strip("{}").split(",")]
    mod = m.group(2)
    if mod != source_module:  # TODO: `source_module` is _not_ resolved
        return m.group(0)
    if source_name not in names:
        return m.group(0)
    if is_default_name:
        print(
            f"{this_module_path}: default import of {source_name} from {source_module} is not supported",
            file=sys.stderr,
        )
        return m.group(0)
    other_names = [name for name in names if name != source_name]
    if other_names:
        remaining_import = f"import {{ {', '.join(other_names)} }} from '{mod}';"
    else:
        remaining_import = ""  # Assume we don't need side-effects

    if isinstance(dest_module, pathlib.Path):
        dest_module = compute_relative_import(this_module_path, dest_module)

    new_import = f"import {{ {source_name} }} from '{dest_module}';"
    return f"{remaining_import}\n{new_import}".strip()


def process_file(
    this_module_path: pathlib.Path,
    *,
    source_name: str,
    source_module: str,
    dest_module: str | pathlib.Path,
) -> Result:
    content = this_module_path.read_text()
    new_content = re.sub(
        es_import_re,
        partial(
            process_import,
            this_module_path=this_module_path,
            source_name=source_name,
            source_module=source_module,
            dest_module=dest_module,
        ),
        content,
    )
    return Result(path=this_module_path, old_content=content, new_content=new_content)


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("--source-name", required=True)
    ap.add_argument("--source-module", required=True)
    ap.add_argument("--dest-module", required=True)
    ap.add_argument("-w", "--write", action="store_true")
    ap.add_argument("files", nargs="+")
    args = ap.parse_args(argv)

    dest_module = args.dest_module
    try:
        dest_module = pathlib.Path(dest_module).resolve()
    except FileNotFoundError:
        pass

    for file in args.files:
        result = process_file(
            pathlib.Path(file).resolve(),
            source_name=args.source_name,
            source_module=args.source_module,
            dest_module=dest_module,
        )
        result.display_diff_and_maybe_write(args.write)


if __name__ == "__main__":
    main()
