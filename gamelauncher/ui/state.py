from __future__ import annotations

from enum import StrEnum


class ViewState(StrEnum):
    LOADING = "loading"
    EMPTY = "empty"
    ERROR = "error"
    SUCCESS = "success"

    @property
    def label(self) -> str:
        labels = {
            ViewState.LOADING: "Loading",
            ViewState.EMPTY: "Empty",
            ViewState.ERROR: "Error",
            ViewState.SUCCESS: "Success",
        }
        return labels[self]
