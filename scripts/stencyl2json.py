import argparse
import json

from idleon_save_editor.stencyl import StencylDecoder

from scripts.common import resolved_path

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--file",
        type=resolved_path,
        default="tmp/decoded.json",
        help="location of decoded JSON save file",
    )
    args = parser.parse_args()

    with open(args.file, encoding="utf-8") as file:
        data = file.read().strip()

    decoded = StencylDecoder(data).result

    outfile = args.file.parent / "decoded.json"
    with open(outfile, "w", encoding="utf-8") as file:
        json.dump(decoded, file)

    print(f"Wrote file: {outfile}")
