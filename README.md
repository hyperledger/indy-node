![logo](collateral/logos/indy-logo.png)

## Indy Node

This codebase embodies all the functionality to run nodes--validators and/or observers
that provide a [self-sovereign identity ecosystem](https://sovrin.org) on top of a
distributed ledger. It is the core project for Indy; over time, all other indy-\* projects may
collapse into this one, except for [indy-sdk](https://github.com/hyperledger/indy-sdk).

This code is independent from but commonly associated with [Sovrin](https://sovrin.org). Sovrin is a public utility
for identity, built on top of this codebase. People who install sovrin packages (e.g., with
`sudo apt install sovrin`) get prepackaged genesis transactions that integrate
with an Indy validator pool using [Sovrin's governance and trust framework](https://sovrin.org/wp-content/uploads/2017/06/SovrinProvisionalTrustFramework2017-03-22.pdf). However, it is possible to use Indy Node
with a different network, using whatever conventions a community chooses.

Bugs, stories, and backlog for this codebase are managed in [Hyperledger's Jira](https://jira.hyperledger.org).
Use project name `INDY`.

Join us on [Jira's Rocket.Chat](https://chat.hyperledger.org/channel/indy) at `#indy` to discuss.

Today, documentation for Indy is sparse. Most materials that exist were written for Sovrin. Therefore,
we recommend that developers should explore Sovrin's [Getting Started Guide](https://github.com/hyperledger/indy-node/blob/stable/getting-started.md) to learn about Indy Node basics. In the future, documentation
will be part of [indy-sdk](https://github.com/hyperledger/indy-sdk).

Have a look at [Setup Instructions](setup.md)
to understand how to work with the code. Note that setup instructions may change often.

## Contributions

We'd love your help; see these [instructions on how to contribute](http://bit.ly/2ugd0bq).
You may also want to read this info about [maintainers](MAINTAINERS.md).
