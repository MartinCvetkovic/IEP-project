from datetime import timedelta
import os

databaseUrl = os.environ["DATABASE_URL"]
redisHost = os.environ.get("REDIS_HOST", default="")


class Configuration:
    SQLALCHEMY_DATABASE_URI = f"mysql+pymysql://root:root@{databaseUrl}/market"
    REDIS_HOST = redisHost
    REDIS_BUFFER_LIST = "buffer"
    JWT_SECRET_KEY = "JWT_SECRET_KEY"
    JWT_ACCESS_TOKEN_EXPIRES = timedelta(hours=1)
    JWT_REFRESH_TOKEN_EXPIRES = timedelta(days=30)
