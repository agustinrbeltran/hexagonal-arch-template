from abc import ABC, abstractmethod
from dataclasses import dataclass


@dataclass(frozen=True)
class PermissionContext:
    pass


class Permission[PC: PermissionContext](ABC):
    @abstractmethod
    def is_satisfied_by(self, context: PC) -> bool: ...


class AnyOf[PC: PermissionContext](Permission[PC]):
    def __init__(self, *permissions: Permission[PC]) -> None:
        self._permissions = permissions

    def is_satisfied_by(self, context: PC) -> bool:
        return any(p.is_satisfied_by(context) for p in self._permissions)
