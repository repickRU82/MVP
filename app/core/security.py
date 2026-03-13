from dataclasses import dataclass
from enum import StrEnum

from fastapi import HTTPException, Request, status


class UserRole(StrEnum):
    ADMIN = "administrator"
    OPERATOR = "operator"
    MANAGER = "manager"
    EXECUTOR = "executor"


@dataclass
class CurrentUser:
    user_id: int
    role: UserRole


def get_current_user(request: Request) -> CurrentUser:
    raw_user_id = request.headers.get("x-user-id") or request.query_params.get("x_user_id")
    raw_role = request.headers.get("x-user-role") or request.query_params.get("x_user_role")

    if raw_user_id is None or raw_role is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Не переданы данные пользователя")

    try:
        user_id = int(raw_user_id)
        role = UserRole(raw_role)
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Недопустимые данные пользователя") from exc
    return CurrentUser(user_id=user_id, role=role)
