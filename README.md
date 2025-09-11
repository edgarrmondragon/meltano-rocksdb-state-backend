# `meltano-state-backend-rocksdb`

<!--
[![PyPI version](https://img.shields.io/pypi/v/meltano-state-backend-rocksdb.svg?logo=pypi&logoColor=FFE873&color=blue)](https://pypi.org/project/meltano-state-backend-rocksdb)
[![Python versions](https://img.shields.io/pypi/pyversions/meltano-state-backend-rocksdb.svg?logo=python&logoColor=FFE873)](https://pypi.org/project/meltano-state-backend-rocksdb)
-->

This is a [Meltano][meltano] extension that provides a [RocksDB][rocksdb] [state backend][state-backend] using the [RocksDict][rocksdict] library.

## Installation

This package needs to be installed in the same Python environment as Meltano.

### From GitHub

#### With [pipx]

```bash
pipx install meltano
pipx inject meltano 'meltano-state-backend-rocksdb @ git+https://github.com/reservoir-data/meltano-state-backend-rocksdb.git'
```

#### With [uv]

```bash
uv tool install --with 'meltano-state-backend-rocksdb @ git+https://github.com/reservoir-data/meltano-state-backend-rocksdb.git' meltano
```

### From PyPI

_This package is not yet available on PyPI._

## Configuration

### `meltano.yml`

```yaml
state_backend:
  uri: rocksdb://${MELTANO_SYS_DIR_ROOT}/state
  rocksdb:
    write_buffer_size: 0x2000000  # 32MB
```

### Environment Variables

* `MELTANO_STATE_BACKEND_URI`: The URI of the RocksDB state backend.
* `MELTANO_STATE_BACKEND_ROCKSDB_WRITE_BUFFER_SIZE`: The RocksDB write buffer size in bytes.

[meltano]: https://meltano.com
[rocksdb]: https://rocksdb.org
[rocksdict]: https://github.com/Congyuwang/RocksDict
[state-backend]: https://docs.meltano.com/concepts/state_backends
[pipx]: https://github.com/pypa/pipx
[uv]: https://docs.astral.sh/uv
