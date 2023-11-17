from __future__ import annotations

from pathlib import Path

from meltano.core.job_state import JobState
from meltano.core.project import Project
from meltano.core.state_store import state_store_manager_from_project_settings

from meltano_rocksdb_state_backend.rocksdb import RocksDBStateStoreManager


def test_state_store(tmp_path: Path) -> None:
    path = tmp_path / "test_dict"
    manager = RocksDBStateStoreManager(
        uri=f"rocksdb://{path.resolve()}",
        write_buffer_size=None,
    )

    # Set initial state
    initial_state = JobState(
        state_id="test",
        updated_at=None,
        partial_state={},
        completed_state={"key": "value"},
    )
    manager.set(initial_state)

    # Get state
    state = manager.get("test")
    assert state is not None
    assert state.completed_state == {"key": "value"}
    assert state.partial_state == {}
    assert manager.get_state_ids() == ["test"]

    # Merge partial state with existing state
    new_state = JobState(
        state_id="test",
        updated_at=None,
        partial_state={"key": "value"},
        completed_state={},
    )
    manager.set(new_state)
    state = manager.get("test")
    assert state is not None
    assert state.completed_state == {"key": "value"}
    assert state.partial_state == {"key": "value"}

    # Clear state
    manager.clear("test")
    state = manager.get("test")

    # Set partial state without existing state
    manager.set(new_state)
    state = manager.get("test")
    assert state is not None
    assert state.completed_state == {}
    assert state.partial_state == {"key": "value"}

    # Clear state for good
    manager.clear("test")
    state = manager.get("test")
    assert state is None
    assert manager.get_state_ids() == []


def test_write_buffer_size(tmp_path: Path) -> None:
    path = tmp_path / "test_dict"
    RocksDBStateStoreManager(
        uri=f"rocksdb://{path.resolve()}",
        write_buffer_size=1024,
    )


def test_get_manager() -> None:
    project = Project.find("fixtures/project")
    manager = state_store_manager_from_project_settings(project.settings)

    assert isinstance(manager, RocksDBStateStoreManager)
    assert manager.parsed.scheme == "rocksdb"
    assert manager.parsed.path.endswith("meltano/state")
    assert manager.write_buffer_size == 0x2000000

    write_buffer_size = project.settings.find_setting(
        "state_backend.rocksdb.write_buffer_size",
    )
    write_buffer_size_env_vars = [
        v.key for v in write_buffer_size.env_vars(prefixes=["meltano"])
    ]
    assert write_buffer_size_env_vars == [
        "MELTANO_STATE_BACKEND_ROCKSDB_WRITE_BUFFER_SIZE",
    ]
