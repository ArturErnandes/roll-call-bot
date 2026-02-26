from dataclasses import dataclass


@dataclass(frozen=True)
class DbConfig:
    admin: str
    password: str
    host: str
    port: int
    db_name: str


@dataclass(frozen=True)
class User:
    id: int
    name: str


@dataclass(frozen=True)
class UsersConfig:
    users: list[User]