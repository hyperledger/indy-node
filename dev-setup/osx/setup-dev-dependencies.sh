#!/bin/bash

brew update

echo 'Installing libsodium...'
brew install https://raw.githubusercontent.com/Homebrew/homebrew-core/65effd2b617bade68a8a2c5b39e1c3089cc0e945/Formula/libsodium.rb   
echo 'Installed libsodium'

echo 'Installing RocksDB...'
brew install rocksdb
echo 'Installing RocksDB...'

echo 'Installing Charm Crypto...'
xcode-select --install
brew install gmp
brew install pbc
pushd /tmp
git clone https://github.com/JHUISI/charm.git
pushd charm
./configure.sh --enable-darwin
make
make install
make test
popd
rm -rf charm
popd
echo 'Installed Charm Crypto'

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
cargo build --release
cp target/release/libindy.dylib /usr/local/lib/
popd
rm -rf indy-sdk
popd
echo 'Installed libindy'

echo 'Installing libcrypto...'
pushd /tmp
git clone https://github.com/hyperledger/indy-crypto.git
pushd indy-crypto/libindy-crypto
cargo build --release
cp target/release/libindy_crypto.dylib /usr/local/lib/
popd
rm -rf indy-crypto
popd
echo 'Installed libcrypto'
