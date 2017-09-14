### Build indy-node using docker

```
./build-indy-node-docker.sh <path-to-sources> <version>
```
Built package is placed in a docker volume `indy-node-deb-u1604`. 

### Build indy-node

```
./build-indy-node.sh <path to sources> <version> <output-path: default='.'>
```

Built package is placed in the `output-path` folder.

### Build 3rd-party dependencies using docker

```
./build-3rd-parties-docker.sh
```

Built packages are placed in a docker volume `indy-node-deb-u1604`.

### Build 3rd-party dependencies

```
./build-3rd-parties-docker.sh <output-path: default='.'>
```

Built packages are placed in the `output-path` folder.
