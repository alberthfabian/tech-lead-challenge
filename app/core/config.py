from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    app_name: str = "Tech Lead Challenge"
    env: str = "dev"

    # reglas de pricing
    delivery_base_fee: int = 5000
    discount_threshold: int = 100_000
    discount_rate: float = 0.05

    class Config:
        env_file = ".env"

settings = Settings()
