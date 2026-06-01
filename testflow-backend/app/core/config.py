from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    # 数据库
    DATABASE_URL: str = "postgresql://testflow:testflow123@localhost:5432/testflow"

    # JWT
    JWT_SECRET_KEY: str = "testflow-secret-key-change-in-production"
    JWT_ALGORITHM: str = "HS256"
    JWT_EXPIRE_MINUTES: int = 1440  # 24小时

    # 文件上传
    UPLOAD_DIR: str = "uploads"

    # 应用
    APP_NAME: str = "TestFlow"
    APP_VERSION: str = "1.0.0"

    class Config:
        env_file = ".env"


settings = Settings()
