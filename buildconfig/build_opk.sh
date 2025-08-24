#!/bin/bash
sudo apt-get update
sudo apt-get install -y squashfs-tools
mksquashfs SaiyanQuest ./build/SaiyanQuest-unstable-latest.opk -all-root -noappend -no-exports -no-xattrs
