# Idleon Saver

Converts Legends of Idleon Steam save files to and from JSON.

## Disclaimer

**Use at your own risk.**

**MAKE BACKUPS** before using and ***DO NOT USE THE ENCODER ON YOUR REAL SAVE DATABASE!***

I do not endorse using this tool to edit your live save files.
This tool is for educational and investigative purposes only.

## Instructions

### Setup

Use either `poetry install` (recommended) or `pip install .` to install dependencies.
If using poetry, replace `python` with `poetry run python` in this document.

If using leveldb scripts, copy your database to a test location (default is `~/dev/leveldb`). For example:

```
cp -r ~/AppData/Roaming/legends-of-idleon/"Local Storage"/leveldb ~/dev/leveldb
```

### Running the GUI

An executable will be released once the GUI is polished enough.
However, it currently needs to be launched via Python (after installing dependencies).

For now, to launch the GUI, run `python idleon_saver/gui/main.py`.

### Running scripts directly

#### Preamble

The first iteration of this project used scripts that interact with the leveldb directly instead of launching the game.
The flakiness of leveldb on Windows has prompted me to abandon that route, which is why the GUI doesn't use the leveldb scripts.

However, these scripts are still available for use if desired.

#### Usage

You can pass `--help` to any script to see the arguments it takes.
If your paths don't match the defaults, you'll need to pass your paths to the scripts.

Script arguments:

| Argument    | Description                                   | Default                                                           |
| ----------  | --------------------------------------------- | ----------------------------------------------------------------- |
| `--workdir` | Working directory where files will be created | `<package directory>/work`                                        |
| `--idleon`  | Legends of Idleon install path                | `C:/Program Files (x86)/Steam/steamapps/common/Legends of Idleon` |
| `--ldb`     | Path to the leveldb to work with              | `~/dev/leveldb`                                                   |

`python scripts/decode.py` will decode leveldb data into 2 JSON files:

- `decoded_plain.json`, which is easier to read, and
- `decoded_types.json`, which contains all the information required to re-encode the data back into the leveldb.

`python scripts/encode.py` will encode the data in `decoded_types.json` back into the database.
