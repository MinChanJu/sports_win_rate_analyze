from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    PROJECT_NAME: str = "Sports Win Rate Analysis API"
    API_V1_STR: str = "/api/v1"
    MODEL_PATH: str = "data/best_model.pt"
    FEATURE_ORDER_PATH: str = "data/feature_order.json"
    CODE_MAP_PATH: str = "data/code_map.json"
    
    class Config:
        case_sensitive = True

settings = Settings()
