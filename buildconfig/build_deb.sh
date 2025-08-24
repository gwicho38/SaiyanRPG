#!/bin/bash
set -e
export PYBUILD_DISABLE=test
python3 -m build --sdist
cd dist
tar -xf SaiyanQuest-*.tar.gz
cd SaiyanQuest-*
cp ../SaiyanQuest-*.tar.gz ..
debmake -b':py3'
echo "./mods usr/share/SaiyanQuest/" > debian/install
dpkg-buildpackage -us -uc -b
cd ..
version=$(python3 -c "import SaiyanQuest; print(SaiyanQuest.__version__)")
branch=$(git rev-parse --abbrev-ref HEAD)
date=$(date +%Y%m%d)
mkdir -p build
mv SaiyanQuest*.deb build/SaiyanQuest-${version}-${branch}-${date}.deb
