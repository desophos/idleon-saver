import json
from argparse import Namespace

from idleon_saver.ldb import ldb_args
from idleon_saver.stencyl.encoder import StencylEncoder
from idleon_saver.utility import normalize_workfile


def main(args: Namespace):
    infile = normalize_workfile(args.workdir, "decoded_types.json")
    workdir = infile.parent

    with open(infile, encoding="utf-8") as file:
        data = json.load(file)

    encoded = StencylEncoder(data).result

    outfile = workdir / "encoded.txt"
    with open(outfile, "w", encoding="ascii") as file:
        file.write(encoded)

    print(f"Wrote file: {outfile}")


if __name__ == "__main__":
    main(ldb_args())
