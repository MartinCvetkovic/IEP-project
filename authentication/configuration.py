from datetime import timedelta
# import os
#
# databaseUrl = os.environ["DATABASE_URL"]


class Configuration:
    SQLALCHEMY_DATABASE_URI = f"mysql+pymysql://root:root@localhost:3307/authentication"  # umesto localhost:3307 treba {databaseUrl}
    JWT_SECRET_KEY = "JWT_SECRET_KEY"
    JWT_ACCESS_TOKEN_EXPIRES = timedelta(hours=1)
    JWT_REFRESH_TOKEN_EXPIRES = timedelta(days=30)
