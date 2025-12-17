from common.domain.core.entities.permission import PermissionContext, Permission
from features.user.domain.core.constants import AUTHZ_NOT_AUTHORIZED
from features.account.entrypoint.exceptions.authorization import \
    AuthorizationError


def authorize[PC: PermissionContext](
    permission: Permission[PC],
    *,
    context: PC,
) -> None:
    """:raises AuthorizationError:"""
    if not permission.is_satisfied_by(context):
        raise AuthorizationError(AUTHZ_NOT_AUTHORIZED)
