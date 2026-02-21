#!/usr/bin/env bash
set -e

sudo apt update
sudo apt install -y git cmake build-essential python3

cd ~
if [ ! -d piper ]; then
  git clone https://github.com/rhasspy/piper.git
fi

cd piper
mkdir -p build
cd build
cmake ..
cmake --build . --config Release