import hashlib
import json
import os
import subprocess
from functools import lru_cache
from pathlib import Path
from typing import Self

from pydantic import BaseModel, Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class KeybindSettings(BaseModel):
    key: str | None = Field(description="Global hotkey to trigger Process SAV", default=None)


class SavSettings(BaseModel):
    """Settings for SAV file watcher."""

    enabled: bool = Field(default=False)
    sav_file: str | None = Field(description="Path to Foxhole .sav file", default=None)
    fs_sav_exe: str | None = Field(description="Path to fs-sav executable", default=None)
    endpoint: str | None = Field(description="SAV submission endpoint", default=None)
    token: str | None = Field(description="X-API-TOKEN for SAV endpoint", default=None)

    PUBLIC_TYPES: list[str] = Field(default=[
        "FortBaseT1", "FortBaseT2", "FortBaseT3",
        "RelicBase1",
        "TownBase1", "TownBase2", "TownBase3",
        "ForwardBase1",
        "GarrisonStation",
        "LargeShipBaseShip",
        "LargeShipStorageShip",
    ])

    def is_configured(self) -> bool:
        return bool(self.sav_file and self.fs_sav_exe and self.endpoint and self.token)

    def parse(self) -> list[dict] | None:
        try:
            result = subprocess.run(
                [self.fs_sav_exe, "parse", self.sav_file],
                capture_output=True, text=True
            )
            if result.returncode != 0:
                return None
            return json.loads(result.stdout)
        except Exception:
            return None

    def filter_stockpiles(self, stockpiles: list[dict]) -> list[dict]:
        filtered = []
        for s in stockpiles:
            if s.get("is_reserve") or s.get("type") in self.PUBLIC_TYPES:
                if s.get("items") is None:
                    s["items"] = []
                filtered.append(s)
        return filtered

    @staticmethod
    def compute_hash(stockpile: dict) -> str:
        items = sorted(stockpile.get("items") or [], key=lambda i: (i["code"], i["crated"]))
        return hashlib.md5(json.dumps(items, sort_keys=True).encode()).hexdigest()

    @staticmethod
    def stockpile_key(stockpile: dict) -> str:
        return f"{stockpile.get('name', '')}::{stockpile.get('type', '')}"

    @staticmethod
    def auto_detect_sav_file() -> str | None:
        """Auto-detect the Foxhole MapData.sav file in the default save path."""
        local_app_data = os.environ.get("LOCALAPPDATA")
        if not local_app_data:
            return None
        save_games_dir = Path(local_app_data) / "Foxhole" / "Saved" / "SaveGames"
        if not save_games_dir.is_dir():
            return None
        for entry in save_games_dir.iterdir():
            if entry.is_file() and entry.name.endswith("MapData.sav"):
                return str(entry.resolve())
        return None


class AppSettings(BaseSettings):
    model_config = SettingsConfigDict(extra="ignore")

    language: str = Field(default="en")
    keybind: KeybindSettings = Field(default_factory=KeybindSettings)
    sav: SavSettings = Field(default_factory=SavSettings)

    @classmethod
    def from_json(cls, file_path: str = "config.json") -> Self:
        config_file = Path(file_path)
        if not config_file.exists():
            return cls()
        with open(config_file) as f:
            data = json.load(f)
        return cls(**data)

    def save(self, file_path: str = "config.json") -> None:
        config_file = Path(file_path)
        data = self.model_dump(mode="json")
        with open(config_file, "w") as f:
            json.dump(data, f, indent=2)


@lru_cache
def get_settings() -> AppSettings:
    return AppSettings.from_json()


settings = get_settings()