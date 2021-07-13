import json
from argparse import Namespace

from idleon_save_editor.ldb import ldb_args
from idleon_save_editor.stencyl import StencylDecoder


def main(args: Namespace):
    infile = args.workdir / "encoded.txt"
    with open(infile, encoding="ascii") as file:
        data = file.read().strip()

    decoded = StencylDecoder(data).result

    for name, attr in (
        ("decoded_plain", "unwrapped"),
        ("decoded_types", "wrapped"),
    ):
        outfile = args.workdir / f"{name}.json"
        with open(outfile, "w", encoding="utf-8") as file:
            # TODO: dict keys are coerced to str
            json.dump(getattr(decoded, attr), file)

        print(f"Wrote file: {outfile}")


if __name__ == "__main__":
    main(ldb_args())
