"""A state store manager that uses RocksDB as the backend."""

from __future__ import annotations

import fnmatch
import typing as t
from urllib.parse import urlparse

from meltano.core.job_state import JobState
from meltano.core.setting_definition import SettingDefinition
from meltano.core.state_store.base import StateStoreManager
from rocksdict import Options, Rdict

WRITE_BUFFER_SIZE = SettingDefinition(
    name="state_backend.rocksdb.write_buffer_size",
    label="write_buffer_size",
    kind="integer",
    default=67108864,  # 64MB
)


class RocksDBStateStoreManager(StateStoreManager):  # type: ignore[misc]
    """A state store manager that uses RocksDB as the backend."""

    label: str = "On-disk RocksDB key-value store"

    def __init__(
        self,
        uri: str,
        *,
        write_buffer_size: int | None,
        **kwargs: t.Any,
    ) -> None:
        """Create a RocksDBStateStoreManager.

        Args:
            uri: The URI to use to connect to the RocksDB database
            **kwargs: Additional kwargs to pass to the underlying rocksdict.Rdict
        """
        super().__init__(**kwargs)
        self.uri = uri
        self.parsed = urlparse(self.uri)
        self.path = self.parsed.path

        self.write_buffer_size = write_buffer_size

        options = Options()
        if self.write_buffer_size:
            options.set_write_buffer_size(self.write_buffer_size)

        self.db = Rdict(self.path, options=options)

    def set(self, state: JobState) -> None:
        """Set state for the given state_id.

        Args:
            state: The state to set
        """
        if state.is_complete():
            self.db[state.state_id] = {
                "completed": state.completed_state,
                "partial": state.partial_state,
            }
            return

        existing_state: dict[str, t.Any] = self.db.get(state.state_id)  # type: ignore[assignment]
        if existing_state:
            state_to_write = JobState(
                state_id=state.state_id,
                completed_state=existing_state.get("completed", {}),
                partial_state=existing_state.get("partial", {}),
            )
            state_to_write.merge_partial(state)
        else:
            state_to_write = state

        self.db[state.state_id] = {
            "completed": state_to_write.completed_state,
            "partial": state_to_write.partial_state,
        }

    def get(self, state_id: str) -> JobState | None:
        """Get state for the given state_id.
        Args:
            state_id: The state_id to get state for
        Returns:
            Dict representing state that would be used in the next run.
        """
        state_dict: dict[str, t.Any] | None = self.db.get(state_id)
        return (
            JobState(
                state_id=state_id,
                completed_state=state_dict.get("completed", {}),
                partial_state=state_dict.get("partial", {}),
            )
            if state_dict
            else None
        )

    def clear(self, state_id: str) -> None:
        """Clear state for the given state_id.
        Args:
            state_id: the state_id to clear state for
        """
        self.db.delete(state_id)

    def get_state_ids(self, pattern: str | None = None) -> list[str]:
        """Get all state_ids available in this state store manager.
        Args:
            pattern: glob-style pattern to filter by
        Returns:
            List of state_ids available in this state store manager.
        """
        return [
            state_id  # type: ignore[misc]
            for state_id in self.db.keys()  # noqa: SIM118
            if not pattern or fnmatch.fnmatch(state_id, pattern)  # type: ignore
        ]

    def acquire_lock(self, state_id: str) -> None:
        """Acquire a naive lock for the given job's state.
        Args:
            state_id: the state_id to lock
        """
        pass  # pragma: no cover
