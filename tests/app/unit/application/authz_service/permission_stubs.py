from common.domain.core.entities.permission import PermissionContext, Permission


class DummyContext(PermissionContext):
    pass


class AlwaysAllow(Permission[DummyContext]):
    def is_satisfied_by(self, context: DummyContext) -> bool:
        return True


class AlwaysDeny(Permission[DummyContext]):
    def is_satisfied_by(self, context: DummyContext) -> bool:
        return False
