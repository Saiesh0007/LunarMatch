import os
from pathlib import Path
from typing import List

class Settings:
    PROJECT_NAME: str = "LunarMatch API"
    VERSION: str = "1.0.0"
    DEBUG: bool = os.getenv("DEBUG", "False").lower() in ("true", "1")
    HOST: str = os.getenv("HOST", "0.0.0.0")
    PORT: int = int(os.getenv("PORT", "8000"))
    
    BASE_DIR: Path = Path(__file__).resolve().parent.parent
    DATA_DIR: Path = BASE_DIR / "data"
    RAW_DIR: Path = DATA_DIR / "raw"
    PROCESSED_DIR: Path = DATA_DIR / "processed"
    EXAMPLES_DIR: Path = DATA_DIR / "examples"
    OUTPUTS_DIR: Path = BASE_DIR / "outputs"
    EXPERIMENTS_DIR: Path = BASE_DIR / "experiments"
    
    DEM_DIR_ENV = os.environ.get("LM_DEM_DIR")
    DEM_DIR: Path | None = Path(DEM_DIR_ENV) if DEM_DIR_ENV else None
    
    CORS_ORIGINS: List[str] = ["*"]
    SIMULATION_SEED: int = 26166

    def ensure_directories(self):
        for directory in [
            self.DATA_DIR,
            self.RAW_DIR,
            self.PROCESSED_DIR,
            self.EXAMPLES_DIR,
            self.OUTPUTS_DIR,
            self.EXPERIMENTS_DIR,
            self.EXPERIMENTS_DIR / "configs",
            self.EXPERIMENTS_DIR / "results",
        ]:
            directory.mkdir(parents=True, exist_ok=True)

settings = Settings()
settings.ensure_directories()
