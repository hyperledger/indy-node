#!/usr/bin/env bash

if [ "$#" -ne 2 ]; then
 echo "Please specify indy-sdk version tag"
 echo "e.g ./setup-dev-dependencies.sh 1.6.7"
 exit 1
fi

indy_sdk_version=$1

brew update

echo 'Installing libsodium...'
brew install https://raw.githubusercontent.com/Homebrew/homebrew-core/65effd2b617bade68a8a2c5b39e1c3089cc0e945/Formula/libsodium.rb
echo 'Installed libsodium'

echo 'Installing RocksDB 5.8.8...'
brew install https://gist.githubusercontent.com/faisal00813/4059a5b41c10aa87270351c4795af752/raw/551d4de01a83f884c798ec5c2cb28a1b15d04db8/rocksdb.rb
echo 'Installing RocksDB...'

echo 'Installing libindy...'
brew install pkg-config
brew install automake 
brew install autoconf
brew install cmake
brew install openssl
brew install zeromq
brew install zmq
export PKG_CONFIG_ALLOW_CROSS=1
export CARGO_INCREMENTAL=1
export RUST_LOG=indy=trace
export RUST_TEST_THREADS=1
export OPENSSL_DIR=$(brew --prefix openssl)
pushd /tmp
git clone https://github.com/hyperledger/indy-sdk.git
pushd indy-sdk/libindy
git fetch --all --tags --prune
git checkout tags/v"${indy_sdk_version}"
cargo build --release
cp target/release/libindy.dylib /usr/local/lib/
popd
rm -rf indy-sdk
popd
echo 'Installed libindy'
