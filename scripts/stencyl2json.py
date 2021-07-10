import argparse
import json
from pathlib import Path

from idleon_save_editor.stencyl import StencylDecoder

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--file",
        default="tmp/decoded.txt",
        help="location of decoded Stencyl save file",
    )
    args = parser.parse_args()

    infile = Path(args.file).resolve()
    with open(infile, encoding="utf-8") as file:
        data = file.read().strip()

    decoded = StencylDecoder(data).result

    outfile = infile.parent / "decoded.json"
    with open(outfile, "w", encoding="utf-8") as file:
        json.dump(decoded, file)

    print(f"Wrote file: {outfile}")
