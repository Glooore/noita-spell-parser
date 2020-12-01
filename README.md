# Noita Spell Parser

This is a simple script for going through Notia's Lua files to extract spell data. As of now, the script doesn't have command line parameters and needs to be edited manually.

## How to use:

Open the script in your editor of choice and change `path_to_data` to a directory containing a `data` folder. You can also change in which file the data will be saved (default: `./spells.csv`).

Run the script with `python3 spell_parser.py`

## TODOs:

- add in command line parameters
- add removing duplicate attributes in XML files (so a bunch of spells work)
- parse add_projectile() function instead of getting the XML file from `related_projectiles` variable in Lua files
-- also, add `related_projectiles` as a backup file
