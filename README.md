# Idleon Save Editor

Converts Legends of Idleon Steam save files to and from JSON.

## Warning

Re-encoding the JSON data is not yet working correctly. **Use at your own risk.**

**MAKE BACKUPS** before using and ***DO NOT USE THE ENCODER ON YOUR REAL SAVE DATABASE!***

## Disclaimer

I do not endorse using this tool to edit your live save files. 
This tool is for educational and investigative purposes only.

## Instructions

0. Copy your database to a test location and modify `config.db_path` if not using the default location (`~/dev/leveldb`):

```
cp -r ~/AppData/Roaming/legends-of-idleon/"Local Storage"/leveldb ~/dev/leveldb
```

Currently, scripts must be run individually in sequence. This process will be improved.

1. `ldb2stencyl`
2. `stencyl2json`
3. View/edit `decoded.json` file if desired
4. `json2stencyl`
5. `stencyl2ldb`
