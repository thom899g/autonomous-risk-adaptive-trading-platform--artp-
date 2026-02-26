"""
ARTP Configuration Manager with Pydantic validation
Handles environment variables, default parameters, and runtime configuration
"""
import os
from typing import Dict, Any, Optional
from pathlib import Path
from dataclasses import dataclass, field
from pydantic import BaseSettings, Field, validator
from dotenv import load_dotenv
import structlog

# Load environment variables
load_dotenv()

logger = structlog.get_logger(__name__)


class ARTPConfig(BaseSettings):
    """Main configuration class with validation"""
    
    # Firebase Configuration
    firebase_credentials_path: str = Field(
        default="./firebase-credentials.json",
        description="Path to Firebase service account credentials"
    )
    firebase_project_id: str = Field(
        default="artp-production",
        description="Firebase project ID"
    )
    firestore_collection: str = Field(
        default="artp_state",
        description="Firestore collection for state persistence"
    )
    
    # Exchange Configuration
    exchange_api_key: Optional[str] = Field(
        default=None,
        description="Exchange API key (CCXT compatible)"
    )
    exchange_secret: Optional[str] = Field(
        default=None,
        description="Exchange API secret"
    )
    exchange_testnet: bool = Field(
        default=True,
        description="Use exchange testnet/sandbox"
    )
    
    # Risk Parameters
    max_drawdown_threshold: float = Field(
        default=0.20,
        ge=0.0,
        le=1.0,
        description="Maximum allowed drawdown before risk reduction"
    )
    volatility_window_days: int = Field(
        default=30,
        gt=0,
        description="Window for volatility calculation in days"
    )
    correlation_threshold: float = Field(
        default=0.75,
        description="Asset correlation threshold for diversification"
    )
    
    # Logging
    log_level: str = Field(
        default="INFO",
        description="Logging level (DEBUG, INFO, WARNING, ERROR)"
    )
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = False
    
    @validator("firebase_credentials_path")
    def validate_firebase_credentials(cls, v):
        """Validate Firebase credentials file exists"""
        if not Path(v).exists():
            logger.warning(
                "firebase_credentials_missing",
                path=v,
                message="Firebase credentials file not found. Firebase features will be disabled."
            )
        return v


@dataclass
class RuntimeConfig:
    """Runtime configuration with mutable state"""
    
    # Current market regime
    current_regime: str = "normal"  # normal, volatile, crisis
    regime_confidence: float = 0.0
    
    # Risk limits
    current_risk_multiplier: float = 1.0
    max_position_size_usd: float = 10000.0
    max_leverage: float = 3.0
    
    # Performance tracking
    daily_pnl: float = 0.0
    current_drawdown: float = 0.0
    
    # Feature toggles
    trading_enabled: bool = False
    risk_adaptation_enabled: bool = True
    emergency_stop_triggered: bool = False
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for Firestore storage"""
        return {
            "current_regime": self.current_regime,
            "regime_confidence": self.regime_confidence,
            "current_risk_multiplier": self.current_risk_multiplier,
            "max_position_size_usd": self.max_position_size_usd,
            "max_leverage": self.max_leverage,
            "daily_pnl": self.daily_pnl,
            "current_drawdown": self.current_drawdown,
            "trading_enabled": self.trading_enabled,
            "risk_adaptation_enabled": self.risk_adaptation_enabled,
            "emergency_stop_triggered": self.emergency_stop_triggered,
            "timestamp": datetime.now().isoformat()
        }


# Global configuration instance
config = ARTPConfig()
runtime_config = RuntimeConfig()