from dataclasses import dataclass

@dataclass
class DatabaseConfig:
    host: str = "localhost"
    port: int = 5433
    database: str = "myappdb"
    user: str = "myappuser"
    password: str = "myapppass"
    
db_config = DatabaseConfig()
