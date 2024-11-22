from __future__ import annotations

import shutil
from typing import TYPE_CHECKING

import pytest
from meltano.core.project import Project
from meltano.core.setting_definition import SettingKind
from meltano.core.state_store import (
    MeltanoState,
    state_store_manager_from_project_settings,
)

from meltano_rocksdb_state_backend.rocksdb import RocksDBStateStoreManager

if TYPE_CHECKING:
    from pathlib import Path


@pytest.fixture
def project(tmp_path: Path) -> Project:
    path = tmp_path / "project"
    shutil.copytree(
        "fixtures/project",
        path,
        ignore=shutil.ignore_patterns(".meltano/**"),
    )
    return Project.find(path.resolve())  # type: ignore[no-any-return]


def test_state_store(tmp_path: Path) -> None:
    path = tmp_path / "test_dict"
    manager = RocksDBStateStoreManager(
        uri=f"rocksdb://{path.resolve().as_posix()}",
        write_buffer_size=None,
    )

    # Set initial state
    initial_state = MeltanoState(
        state_id="test",
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
    new_state = MeltanoState(
        state_id="test",
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


def test_get_manager(project: Project) -> None:
    write_buffer_size = 0x2000000
    project.settings.set("state_backend.rocksdb.write_buffer_size", write_buffer_size)  # type: ignore[no-untyped-call]

    manager = state_store_manager_from_project_settings(project.settings)

    assert isinstance(manager, RocksDBStateStoreManager)
    assert manager.scheme == "rocksdb"
    assert manager.db.path().endswith(".meltano/state")
    assert manager.write_buffer_size == write_buffer_size

    manager.set(
        MeltanoState(
            state_id="test",
            partial_state={},
            completed_state={"key": "value"},
        ),
    )
    sys_dir_root = project.sys_dir_root
    assert sys_dir_root.joinpath("state", "rocksdict-config.json").exists()


def test_settings(project: Project) -> None:
    setting_name = "state_backend.rocksdb.write_buffer_size"
    project.settings.set(setting_name, 0x2000000)  # type: ignore[no-untyped-call]

    write_buffer_size = project.settings.find_setting(setting_name)

    assert write_buffer_size.label == "Writer Buffer Size"
    assert write_buffer_size.kind == SettingKind.INTEGER

    env_vars = write_buffer_size.env_vars(prefixes=["meltano"])
    assert env_vars[0].key == "MELTANO_STATE_BACKEND_ROCKSDB_WRITE_BUFFER_SIZE"
