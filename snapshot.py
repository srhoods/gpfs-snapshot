#!/usr/bin/env python3
#
# Script to manage the creation and deletion of GPFS snapshots
# Author: Steven Rhoods <steven@rhoods.com>
#

import subprocess
import argparse
from datetime import datetime

VERSION="0.1.2"

fs=['gpfs0', 'gpfs1']

def snapshot_timestamp_seconds(TIME):
    p = '%a %b %d %H:%M:%S %Y'
    return int(datetime.strptime(TIME, p).strftime('%s'))

def timenow_seconds():
    return int(datetime.now().strftime('%s'))

def snapshot_print(FS):
    header=['Filesystem','Fileset','Snapshot Name','Timestamp','Age (seconds)']
    mmlssnapshot=subprocess.run(["/usr/lpp/mmfs/bin/mmlssnapshot", FS, "-Y"], stdout=subprocess.PIPE)
    mmlssnapshot_split = mmlssnapshot.stdout.decode('utf-8').rstrip().split('\n')
    if len(mmlssnapshot_split) > 1:
        print('{:<12} {:<15} {:<25} {:<30} {:<15}'.format(header[0],header[1],header[2],header[3],header[4]))
        for items in mmlssnapshot_split:
            if items.split(':')[2] == 'HEADER':
                continue
            else:
                row=items.split(':')
                print('{:<12} {:<15} {:<25} {:<30} {:<15}'.format(row[6],
                                        row[14],
                                        row[7],
                                        row[10].replace('%3A',':'),
                                        (timenow_seconds() - snapshot_timestamp_seconds(row[10].replace('%3A',':')))))
    else:
        print("No snapshots found")

def snapshot_create(FS, FILESET):
    snapshotname=FILESET + ":" + datetime.now().strftime('%Y-%m-%d_%H%M%S')
    mmcrsnapshot=subprocess.run(["/usr/lpp/mmfs/bin/mmcrsnapshot", FS, snapshotname], stdout=subprocess.PIPE)
    if mmcrsnapshot.returncode == 0:
        print("Snapshot completed successfully: " + FS + ":" + snapshotname)
    else:
        print("Snapshot failed: " + FS + ":" + snapshotname)
        exit(1)
    return mmcrsnapshot

def snapshot_delete(SNAPSHOTS):
    if len(SNAPSHOTS) != 0:
        for snapshot in SNAPSHOTS:
            snapshotname=snapshot["fileset"] + ":" + snapshot["name"]
            mmdelsnapshot=subprocess.run(["/usr/lpp/mmfs/bin/mmdelsnapshot", snapshot["fs"], snapshotname], stdout=subprocess.PIPE)

            if mmdelsnapshot.returncode == 0:
                print("Snapshot deleted successfully: " + snapshot["fs"] + ":" + snapshotname)
            else:
                print("Failed to delete snapshot: " + snapshot["fs"] + ":" + snapshotname)
                exit(1)

def return_aged_snapshots(FS, FILESET, AGE):
    snapshots = []
    mmlssnapshot=subprocess.run(["/usr/lpp/mmfs/bin/mmlssnapshot", FS, "-j", FILESET, "-Y"], stdout=subprocess.PIPE)
    mmlssnapshot_split = mmlssnapshot.stdout.decode('utf-8').rstrip().split('\n')

    if len(mmlssnapshot_split) > 1:
        for items in mmlssnapshot_split:
            if items.split(':')[2] == 'HEADER':
                continue
            else:
                row=items.split(':')
                SECONDS=timenow_seconds() - snapshot_timestamp_seconds(row[10].replace('%3A',':'))
                if SECONDS > AGE:
                    snapshots.append({'fs': row[6], 
                            'fileset': row[14], 
                            'name': row[7], 
                            'age': SECONDS})
    if len(snapshots) == 0:
        print("No snapshots found which meet the deletion criteria")
    return snapshots

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="GPFS/ESS Snapshot management tool")
    parser.add_argument('--fs', type=str, help="Name of target filesystem", choices=fs, required=False)
    parser.add_argument('--fset', type=str, help="Name of target fileset", required=False)
    parser.add_argument('--age', type=int, help="Age of snapshots to delete in days", required=False)
    parser.add_argument('--force', help="Delete all snapshots for a given filesystem/fileset", action='store_true', required=False)
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument('--list', help="Lists all snapshots for a given volume", action='store_true')
    group.add_argument('--create', help="Creates a snapshot for a given volume and fileset", action='store_true')
    group.add_argument('--delete', help="Deletes snapshots for a given volume and fileset", action='store_true')
    group.add_argument('--version', '-v', help="Displays version of script", action='store_true')
    args = parser.parse_args()

    if args.list == True:
        if args.fs is not None:
            snapshot_print(args.fs)
        else:
            print("--fs option must be specified")
            exit(1)

    if args.create == True:
        if args.fs is not None and args.fset is not None:
            snapshot_create(args.fs, args.fset)
        else:
            print("--fs and --fset options must be specified")
            exit(1)

    if args.delete == True:
        if args.fs is not None and args.fset is not None and args.age is not None:
            if args.age == 0:
                if args.force != True:
                    print("Setting '--age 0' will delete all snapshots - confirm with --force option")
                    exit(1)
            seconds=args.age*86400
            snapshot_delete(return_aged_snapshots(args.fs, args.fset, seconds))
        else:
            print("--fs, --fset and --age options must be specified")
            exit(1)

    if args.version == True:
        print("Version: " + VERSION)
