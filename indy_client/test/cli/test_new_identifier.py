#   Copyright 2017 Sovrin Foundation
#
#   Licensed under the Apache License, Version 2.0 (the "License");
#   you may not use this file except in compliance with the License.
#   You may obtain a copy of the License at
#
#       http://www.apache.org/licenses/LICENSE-2.0
#
#   Unless required by applicable law or agreed to in writing, software
#   distributed under the License is distributed on an "AS IS" BASIS,
#   WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#   See the License for the specific language governing permissions and
#   limitations under the License.
#


def checkWalletState(cli, totalIds, isAbbr, isCrypto):

    if cli._activeWallet:
        assert len(cli._activeWallet.idsToSigners) == totalIds

    if totalIds > 0:
        activeSigner = cli._activeWallet.idsToSigners[
            cli._activeWallet.defaultId]

        if isAbbr:
            assert activeSigner.verkey.startswith("~"), \
                "verkey {} doesn't look like abbreviated verkey".\
                format(activeSigner.verkey)

            assert cli._activeWallet.defaultId != activeSigner.verkey, \
                "new DID should not be equal to abbreviated verkey"

        if isCrypto:
            assert not activeSigner.verkey.startswith("~"), \
                "verkey {} doesn't look like cryptographic verkey". \
                format(activeSigner.verkey)

            assert cli._activeWallet.defaultId == activeSigner.verkey, \
                "new DID should be equal to verkey"


def getTotalIds(cli):
    if cli._activeWallet:
        return len(cli._activeWallet.idsToSigners)
    else:
        return 0


def testNewIdWithIncorrectSeed(be, do, aliceCLI):
    totalIds = getTotalIds(aliceCLI)
    be(aliceCLI)
    # Seed not of length 32 or 64
    do("new DID with seed aaaaaaaaaaa",
       expect=["Seed needs to be 32 or 64 characters (if hex) long"])
    checkWalletState(aliceCLI, totalIds=totalIds, isAbbr=False, isCrypto=False)

    # Seed of length 64 but not hex
    do("new DID with seed "
       "xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyy",
       expect=["Seed needs to be 32 or 64 characters (if hex) long"])
    checkWalletState(aliceCLI, totalIds=totalIds, isAbbr=False,
                     isCrypto=False)

    # Seed of length 64 and hex
    do("new DID with seed "
       "2af3d062450c942be50ee766ce2571a6c75c0aca0de322293e7e9f116959c9c3",
       expect=["Current DID set to"])
    checkWalletState(aliceCLI, totalIds=totalIds + 1, isAbbr=False,
                     isCrypto=False)


def testNewIdIsNotInvalidCommand(be, do, aliceCLI):
    totalIds = getTotalIds(aliceCLI)
    be(aliceCLI)
    do("new DID", not_expect=["Invalid command"])
    checkWalletState(aliceCLI, totalIds=totalIds +
                     1, isAbbr=False, isCrypto=False)


def testNewId(be, do, aliceCLI):
    totalIds = getTotalIds(aliceCLI)
    be(aliceCLI)
    do("new DID",
       expect=["Current DID set to"])
    checkWalletState(aliceCLI, totalIds=totalIds +
                     1, isAbbr=False, isCrypto=False)
