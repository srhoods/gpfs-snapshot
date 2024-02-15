# gpfs-snapshot - README
Simple tool to manage the rotation of GPFS snapshots

## Usage
```
usage: snapshot.py [-h] [--fs {gpfs0,gpfs1}] [--fset FSET] [--age AGE]
                   [--force] (--list | --create | --delete | --version)

GPFS/ESS Snapshot management tool

optional arguments:
  -h, --help          show this help message and exit
  --fs {gpfs0,gpfs1}  Name of target filesystem
  --fset FSET         Name of target fileset
  --age AGE           Age of snapshots to delete in days
  --force             Delete all snapshots for a given filesystem/fileset
  --list              Lists all snapshots for a given volume
  --create            Creates a snapshot for a given volume and fileset
  --delete            Deletes snapshots for a given volume and fileset
  --version, -v       Displays version of script
```
### Create a snapshot for a given volume and fileset
```
snapshot.py --create --fs gpfs0 --fset fileset1
Snapshot completed successfully: gpfs0:fileset1:2024-02-15_221455
```
### List all snapshots for a given volume
```
snapshot.py --list --fs gpfs0
Filesystem   Fileset         Snapshot Name             Timestamp                      Age (seconds)
gpfs0        fileset1        2024-02-15_221455         Thu Feb 15 22:14:56 2024       15
```
### Delete all snapshots for a given volume
```
snapshot.py --delete --fs gpfs0 --fset fileset1 --age 0 --force
Snapshot deleted successfully: gpfs0:fileset1:2024-02-15_221455
```
