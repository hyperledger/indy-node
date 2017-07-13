# Indy Node

[![Build Status](https://jenkins.evernym.com/buildStatus/icon?job=Sovrin%20Node/master)](https://jenkins.evernym.com/view/Core/job/Sovrin%20Node/job/master/)    

This codebase embodies all the functionality to run nodes--validators and/or observers
that provide a [self-sovereign identity ecosystem](https://sovrin.org) on top of a
distributed ledger. It is the core project for Indy; over time, all other indy-\* projects may
collapse into this one, except for [indy-sdk](https://github.com/hyperledger/indy-sdk).

This code is tightly associated with [Sovrin](https://sovrin.org). Sovrin is a public utility
for identity, built on top of this codebase. People who install sovrin packages (e.g., with
`sudo apt install sovrin-node`) get prepackaged genesis transactions that integrate a
with an Indy validator pool using [Sovrin's governance and trust framework](https://sovrin.org/wp-content/uploads/2017/06/SovrinProvisionalTrustFramework2017-03-22.pdf). However, it is possible to use Indy Node
with a different network, using whatever conventions a community chooses.

Bugs, stories, and backlog for this codebase are managed in [Hyperledger's Jira](https://jira.hyperledger.org).
Use project name INDY.

Join us on [Jira's Rocket.Chat](chat.hyperledger.org) at #indy to discuss

Today, documentation for Indy is sparse. Most materials that exist were written for Sovrin. Therefore,
we recommend that developers should explore Sovrin's [Getting Started Guide](https://github.com/sovrin-foundation/sovrin-client/blob/master/getting-started.md) to learn about Indy Node basics. In the future, documentation
will be part of [indy-sdk](https://github.com/hyperledger/indy-sdk).

Have a look at [Setup Instructions](https://github.com/sovrin-foundation/sovrin-client/blob/master/setup.md)
to understand how to work with the code. Note that setup instructions are
still changing hour-by-hour as we identify
install preconditions.

# Indy Client    

[![Build Status](https://jenkins.evernym.com/buildStatus/icon?job=Sovrin%20Client/master)](https://jenkins.evernym.com/job/Sovrin%20Client/job/master/)    

Indy Client provides a command-line tool and underlying interfaces to interact with
a [self-sovereign identity](https://sovrin.org) ecosystem on top of distributed ledger technology.
This codebase will eventually be subsumed by (Indy SDK)[https://github.com/hyperledger/indy-sdk);
if you are looking to build a client or agent, we recommend that you use the SDK instead, because
the encapsulation and documentation here are not as clean.

[Indy Node](https://github.com/hyperledger/indy-node) is more "core" to Indy; if you want to
understand how Indy works, starting there may be better.

All bugs, backlog, and stories for Indy (except the SDK) are managed in [Hyperledger's Jira](https://jira.hyperledger.org); use project name INDY.

Developers may want to explore Sovrin's [Getting Started Guide](https://github.com/sovrin-foundation/sovrin-client/blob/master/getting-started.md) to learn about how Indy works. (Sovrin is the public, open ecosystem
built on top of Indy technology; for more info, see [https://sovrin.org].)

Have a look at [Setup Instructions](https://github.com/sovrin-foundation/sovrin-client/blob/master/setup.md)
to understand how to work with the code. Note that setup instructions are still changing hour-by-hour as we identify install preconditions.

# Indy Common

[![Build Status](https://jenkins.evernym.com/buildStatus/icon?job=Sovrin%20Common/master)](https://jenkins.evernym.com/view/Core/job/Sovrin%20Common/job/master/)

Common utility functions for other Indy repos (like indy-client, indy-node etc)

This repo will be merged with indy-node at some point soon.

All bugs, backlog, and stories for this repo are managed in [Hyperledger's Jira](https://jira.hyperledger.org).

Join us on [Jira's Rocket.Chat](chat.hyperledger.org) at #indy to discuss.

