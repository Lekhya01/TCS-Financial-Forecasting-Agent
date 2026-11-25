from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    app_name: str = "TCS Financial Forecasting Agent"
    mysql_url: str = "mysql+pymysql://root:root@localhost:3306/tcs_forecast"
    openai_api_key: str = ""
    openai_model: str = "gpt-4o-mini"
    embedding_model: str = "sentence-transformers/all-MiniLM-L6-v2"
    data_dir: str = "data"
    vector_dir: str = "data/vectorstore"
    documents_dir: str = "data/documents"
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

settings = Settings()
