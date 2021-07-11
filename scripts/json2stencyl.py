import json
from argparse import Namespace

from idleon_save_editor.stencyl import StencylEncoder

from scripts.common import ldb_args, resolved_path


def main(args: Namespace):
    infile = args.workdir / "decoded.json"
    with open(infile, encoding="utf-8") as file:
        data = json.load(file)

    encoded = StencylEncoder(data).result

    outfile = args.workdir / "encoded.txt"
    with open(outfile, "w", encoding="ascii") as file:
        file.write(encoded)

    print(f"Wrote file: {outfile}")


if __name__ == "__main__":
    main(ldb_args())
