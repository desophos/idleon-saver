# Idleon Saver

[![Build](https://github.com/desophos/idleon-saver/actions/workflows/build.yml/badge.svg)](https://github.com/desophos/idleon-saver/actions/workflows/build.yml)
[![Test](https://github.com/desophos/idleon-saver/actions/workflows/test.yml/badge.svg)](https://github.com/desophos/idleon-saver/actions/workflows/test.yml)
[![Coverage Status](https://coveralls.io/repos/github/desophos/idleon-saver/badge.svg?branch=main)](https://coveralls.io/github/desophos/idleon-saver?branch=main)
[![Maintainability](https://api.codeclimate.com/v1/badges/bda291e68f16afb3fbfe/maintainability)](https://codeclimate.com/github/desophos/idleon-saver/maintainability)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)

Converts Legends of Idleon Steam save files to and from JSON with [a friendly GUI](https://github.com/desophos/idleon-saver/releases) that makes it easy to export your save data to [Idleon Companion](https://idleoncompanion.com/), [Cogstruction](https://github.com/automorphis/Cogstruction), and other tools.

## Disclaimer

**Use at your own risk.**

**MAKE BACKUPS** before using and ***DO NOT USE THE ENCODER ON YOUR REAL SAVE DATABASE!***

I do not endorse using this tool to edit your live save files.
This tool is for educational and investigative purposes only.

## For Users

Most users will only need to **download [the latest exe release](https://github.com/desophos/idleon-saver/releases/latest)**.

## For Developers

### Setup

Use either [`poetry install`](https://python-poetry.org/docs/master/) (recommended) or `pip install .` to install dependencies.
If using poetry, replace `python` with `poetry run python` in this document (or run from a `poetry shell`).

If using leveldb scripts, copy your database to a test location (default is `~/dev/leveldb`). For example:

```
cp -r ~/AppData/Roaming/legends-of-idleon/"Local Storage"/leveldb ~/dev/leveldb
```

### Running the GUI

To launch the GUI, run `python idleon_saver/gui/main.py`.

### Running scripts directly

#### Preamble

The first iteration of this project used scripts that interact with the leveldb directly instead of launching the game.
The flakiness of leveldb on Windows has prompted me to abandon that route, which is why the GUI doesn't use the leveldb scripts.

However, these scripts are still available for use if desired.

#### Usage

You can pass `--help` to any script to see the arguments it takes.
If your paths don't match the defaults, you'll need to pass your paths to the scripts.

Script arguments:

| Argument          | Description                                   | Default                                                           |
| ----------------- | --------------------------------------------- | ----------------------------------------------------------------- |
| `-n`, `--idleon`  | Legends of Idleon install path                | `C:/Program Files (x86)/Steam/steamapps/common/Legends of Idleon` |
| `-l`, `--ldb`     | Path to the leveldb to work with              | `~/dev/leveldb`                                                   |
| `-w`, `--workdir` | Working directory where files will be created | `<package directory>/work`                                        |
| `-i`, `--infile`  | Input filename                                | Varies by script                                                  |
| `-o`, `--outfile` | Output filename                               | Varies by script                                                  |

`python scripts/decode.py` will decode leveldb data into 2 JSON files:

- `decoded_plain.json`, which is easier to read, and
- `decoded_types.json`, which contains all the information required to re-encode the data back into the leveldb.

`python scripts/encode.py` will encode the data in `decoded_types.json` back into the database.

After you've obtained your `decoded_plain.json`, you can export it into formats used by community tools with `python scripts/export.py`. This script takes one additional argument:

| Argument   | Description                                   | Default            | Choices                                       |
| ---------- | --------------------------------------------- | ------------------ | --------------------------------------------- |
| `--to`     | Community tool format to export your data to  | `idleon_companion` | `idleon_companion`, `cogstruction`            |

The `idleon_companion` option produces `idleon_companion.json` for import into [Idleon Companion](https://idleoncompanion.com/).

The `cogstruction` option produces `cog_datas.csv` and `empties_datas.csv` for use with [Cogstruction](https://github.com/automorphis/Cogstruction).

### Contributing

Feedback, suggestions, and contributions are welcome!

Use `poetry install --with dev,test` to install the optional dependencies. Run tests with [`pytest`](https://docs.pytest.org/en/latest/index.html). Please run [Black](https://black.readthedocs.io/en/stable/) before submitting a PR; I have it configured to run on save. Thanks for reading!
