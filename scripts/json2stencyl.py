import json
from argparse import Namespace

from idleon_saver.ldb import ldb_args
from idleon_saver.stencyl.encoder import StencylEncoder


def main(args: Namespace):
    infile = args.workdir / "decoded_types.json"
    with open(infile, encoding="utf-8") as file:
        data = json.load(file)

    encoded = StencylEncoder(data).result

    outfile = args.workdir / "encoded.txt"
    with open(outfile, "w", encoding="ascii") as file:
        file.write(encoded)

    print(f"Wrote file: {outfile}")


if __name__ == "__main__":
    main(ldb_args())
