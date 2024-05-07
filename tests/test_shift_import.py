from tska import shift_import


def test_shift_import(tmpdir):
    victim = tmpdir.join("victim.tsx")
    victim.write_text('import { Alert, Button } from "dancing-shoes";\n', "utf-8")
    subdir = tmpdir.mkdir("subdir")
    sub_victim = subdir.join("sub_victim.tsx")
    sub_victim.write_text('import { Alert } from "dancing-shoes";\n', "utf-8")
    components = tmpdir.join("components.tsx")
    components.write_text("export function Alert() {return null;}\n", "utf-8")
    shift_import.main(
        [
            "--write",
            "--source-name",
            "Alert",
            "--source-module",
            "dancing-shoes",
            "--dest-module",
            str(components),
            str(victim),
            str(sub_victim),
        ]
    )
    assert "'../components'" in sub_victim.read_text("utf-8")
    assert "'./components'" in victim.read_text("utf-8")
