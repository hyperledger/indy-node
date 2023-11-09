# Indy2-VDR

> Note: The library is under active development!

## Introduction

This is Rust library representing a convenient client for connecting to Indy2 Ledger and executing transactions/queries/contracts.
The library can be used to connect to multiple ledger networks simultaneously.

The library provides methods to:

- connect to node
- build transactions executing predefined contract methods
- sign transactions
  - in order to sign transactions using vdr library you need to provide callbacks for doing elliptic curve signatures
- send transactions to connected node
- parse data returned from the node
- single step contract method execution

## Prerequisites

- Indy2 Ledger running - see [instructions](../README.md) on how to run local network.

## Build

In order to build library, you must have [Rust](https://rustup.rs/) installed.

```
cargo build
```

## Usage

To use vdr, add this to your `Cargo.toml`:

```
[dependencies]
didcomm = { path = "../path/to/crate" }
```

## Code formatting

Library uses [Rustfmt](https://rust-lang.github.io/rustfmt/?version=v1.6.0&search=) to define code formatting rules.

```
cargo +nightly fmt
```

## Features

- `migration` (Optional) - module providing helper methods to convert old indy styled objects (schema id, schema, credential definition id, credential definition).
- `ledger_test` (Optional) - enable ledger integration tests (requires running network).

# Logging

- To see the logs, please set `RUST_LOG` environment variable to desired log level: `info`, `debug`, `trace` etc.
