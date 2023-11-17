# `meltano-rocksdb-state-backend`

[![PyPI version](https://img.shields.io/pypi/v/meltano-rocksdb-state-backend.svg?logo=pypi&logoColor=FFE873&color=blue)](https://pypi.org/project/meltano-rocksdb-state-backend)
[![Python versions](https://img.shields.io/pypi/pyversions/meltano-rocksdb-state-backend.svg?logo=python&logoColor=FFE873)](https://pypi.org/project/meltano-rocksdb-state-backend)

This is a [Meltano](https://meltano.com) plugin that provides a [RocksDict](https://github.com/Congyuwang/RocksDict) [state backend](https://docs.meltano.com/concepts/state_backends).

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
