### Build indy-plenum using docker

```
./build-indy-plenum-docker.sh <path-to-sources> <version>
```
Built package is placed in a docker volume `indy-plenum-deb-u1604`. 

### Build indy-plenum

```
./build-indy-plenum.sh <path to sources> <version> <output-path: default='.'>
```

Built package is placed in the `output-path` folder.

### Build 3rd-party dependencies using docker

```
./build-3rd-parties-docker.sh
```

Built packages are placed in a docker volume `indy-plenum-deb-u1604`.

### Build 3rd-party dependencies

```
./build-3rd-parties-docker.sh <output-path: default='.'>
```

Built packages are placed in the `output-path` folder.
