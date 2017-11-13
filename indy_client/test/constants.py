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

from config.config import cmod

primes = {
    "prime1":
        (
            cmod.integer(int(
                "".join(
                    """15732949138937579391219059496113493280403242640311079747
                   67301078043564845160610513453327631418060058384363049226124
                   95876180233509449197495032194146432047460167589034147716097
                   41788050395213980524159162235382862938333286942502908689845
                   22278954188297999456509738489839014597334262127359796688359
                   84691928193677469"""
                    .split()
                ))),
            cmod.integer(int(
                "".join(
                    """1513238926483731965795157528265196838367648736076320720
                    5759183721669862272955753403513858727659415632080076852582
                    5023728398410073692081011811496168877166664537052088207068
                    0611725948793987738723529209123909831994169273886883192079
                    4649381044920370210055927143958675325672890071399009716848
                    4829574000438573295723"""
                    .split()
                )))
        ), "prime2":
        (
            cmod.integer(int(
                "".join(
                    """1506196778844683532080581566329538914319752714166209556
                    1454803993724676961062201703338539465887948418685223146923
                    8992217246264205570458379437126692055331206248530723117202
                    1317399667377603997554909355892234011237620518236023438105
                    5497880303280360690776193758710196919324192135101143075097
                    0746500680609001799529"""
                    .split()
                ))),
            cmod.integer(int(
                "".join(
                    """1715908575684366449923593477197037640485010783986660619
                    2171906439582749697069687948174031114114827360739265732110
                    3691543916274965279072000206208571551864201305434022165176
                    5633639549211835762300728126357446293372902429546994271603
                    6258610206896228507621320082845183814295963700604843930727
                    3563604553818326766703"""
                    .split()
                )))
        )
}
