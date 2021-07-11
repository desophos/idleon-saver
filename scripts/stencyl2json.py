import json
from argparse import Namespace

from idleon_save_editor.stencyl import StencylDecoder

from scripts.common import ldb_args, resolved_path


def main(args: Namespace):
    infile = args.workdir / "encoded.txt"
    with open(infile, encoding="ascii") as file:
        data = file.read().strip()

    decoded = StencylDecoder(data).result

    outfile = args.workdir / "decoded.json"
    with open(outfile, "w", encoding="utf-8") as file:
        json.dump(decoded, file)

    print(f"Wrote file: {outfile}")


if __name__ == "__main__":
    main(ldb_args())
