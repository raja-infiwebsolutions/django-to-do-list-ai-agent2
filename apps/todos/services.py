from typing import Any, Dict, Optional
from datetime import date
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.db import transaction
from django.core.exceptions import PermissionDenied, ValidationError
from django.utils.dateparse import parse_date

from .models import Todo


def _coerce_bool(val: Any) -> Optional[bool]:
    """Normalize various truthy/falsey representations to Python bool.

    Accepts booleans, integers and common string values.
    Returns True/False for recognized values, and None for unrecognized inputs
    so callers can surface validation errors instead of silently coercing.
    """
    if isinstance(val, bool):
        return val
    if isinstance(val, int):
        return bool(val)
    if isinstance(val, str):
        v = val.strip().lower()
        if v in ("1", "true", "yes", "y", "t"):
            return True
        if v in ("0", "false", "no", "n", "f"):
            return False
    return None


def _parse_due_date(val: Any) -> Optional[date]:
    """Parse a date string or pass through a date object.

    Returns a date object or None. Raises ValidationError for invalid string formats.
    """
    if val is None:
        return None
    # If it's already a date/datetime, allow model validation to handle it
    if not isinstance(val, str):
        return val
    parsed = parse_date(val)
    if parsed is None:
        raise ValidationError({"due_date": "Invalid date format. Expected YYYY-MM-DD."})
    return parsed


def _validate_priority(val: Any) -> Optional[int]:
    """Validate and coerce priority to an integer within allowed bounds.

    Allowed range: 0..5 inclusive. Returns None if input is None/empty.
    Raises ValidationError for invalid values.
    """
    if val is None:
        return None
    if isinstance(val, str) and val.strip() == "":
        return None
    try:
        pr = int(val)
    except (TypeError, ValueError):
        raise ValidationError({"priority": "Must be an integer between 0 and 5."})
    if not 0 <= pr <= 5:
        raise ValidationError({"priority": "Must be between 0 and 5."})
    return pr


class TodoService:
    DEFAULT_PAGE = 1
    DEFAULT_LIMIT = 20
    MAX_LIMIT = 100

    @staticmethod
    @transaction.atomic
    def create_todo(user: Any, data: Dict[str, Any]) -> Todo:
        """
        Create a todo for an authenticated user.
        Returns a Todo model instance. Views/serializers are responsible for converting to JSON and
        for mapping model fields to API responses (this service intentionally returns ORM objects).
        """
        if not getattr(user, "is_authenticated", False):
            raise PermissionDenied("Authentication required")

        title = data.get("title")
        if not title:
            raise ValidationError({"title": "This field is required."})

        # Accept optional fields safely and normalize
        description = data.get("description", "")
        completed_raw = data.get("completed", False)
        completed = _coerce_bool(completed_raw)
        if completed is None:
            raise ValidationError({"completed": "Invalid boolean value."})

        priority = _validate_priority(data.get("priority"))
        due_date = _parse_due_date(data.get("due_date", None))

        # Build instance, run model validation, then persist
        todo = Todo(
            user=user,
            title=title,
            description=description,
            completed=completed,
            priority=priority,
            due_date=due_date,
        )
        todo.full_clean()
        todo.save()
        return todo

    @staticmethod
    def list_todos(user: Any, page: int = DEFAULT_PAGE, limit: int = DEFAULT_LIMIT, status: Optional[str] = None) -> Dict[str, Any]:
        """
        Returns a paginated list of todos (ORM model instances) for the given user.
        status: "completed" | "incomplete" | None

        NOTE: This method returns model instances; the caller (view/serializer) should
        convert them to serializable data and must not expose sensitive fields.

        Pagination behavior on out-of-range pages: returns the last available page if
        page number is greater than available pages. If there are zero items, returns
        an empty list and pages=0 with page=0 to clearly indicate no results.
        """
        if not getattr(user, "is_authenticated", False):
            raise PermissionDenied("Authentication required")

        # sanitize and cap pagination params
        try:
            limit = int(limit)
        except (ValueError, TypeError):
            limit = TodoService.DEFAULT_LIMIT
        limit = max(1, min(limit, TodoService.MAX_LIMIT))

        try:
            page = int(page)
        except (ValueError, TypeError):
            page = TodoService.DEFAULT_PAGE
        page = max(1, page)

        # use select_related if caller needs related user fields to avoid N+1
        qs = Todo.objects.filter(user=user).select_related("user").order_by("-created_at")

        if status is not None:
            s = str(status).lower()
            if s == "completed":
                qs = qs.filter(completed=True)
            elif s in ("incomplete", "pending", "not_completed"):
                qs = qs.filter(completed=False)

        paginator = Paginator(qs, limit)
        try:
            page_obj = paginator.page(page)
        except PageNotAnInteger:
            page_obj = paginator.page(1)
        except EmptyPage:
            if paginator.num_pages >= 1:
                page_obj = paginator.page(paginator.num_pages)
            else:
                # No items at all
                items = []
                meta = {
                    "total": paginator.count,
                    # use page=0 to indicate empty dataset clearly
                    "page": 0,
                    "limit": limit,
                    "pages": 0,
                }
                return {"items": items, "meta": meta}

        items = list(page_obj.object_list)
        meta = {
            "total": paginator.count,
            "page": page_obj.number,
            "limit": limit,
            "pages": paginator.num_pages,
        }
        return {"items": items, "meta": meta}

    @staticmethod
    def get_todo(user: Any, todo_id: Any) -> Todo:
        """
        Retrieve a single todo by ID. Raises Todo.DoesNotExist if not found.
        This method intentionally restricts the lookup to the provided user so that
        non-existence and unauthorized access are indistinguishable at the service layer.
        Caller (view) should translate model exceptions into HTTP responses.
        """
        if not getattr(user, "is_authenticated", False):
            raise PermissionDenied("Authentication required")

        # Filter by user to avoid leaking resource existence
        todo = Todo.objects.select_related("user").get(pk=todo_id, user=user)
        return todo

    @staticmethod
    @transaction.atomic
    def update_todo(user: Any, todo_id: Any, data: Dict[str, Any]) -> Todo:
        """
        Partially update a todo. Uses select_for_update() to lock the row in a transaction
        to prevent concurrent lost updates. Validation is performed via full_clean().

        The select_for_update lookup is filtered by user to avoid locking other users' rows
        and to keep error semantics consistent with get_todo.
        """
        if not getattr(user, "is_authenticated", False):
            raise PermissionDenied("Authentication required")

        # Lock only the requested user's row for update
        todo = Todo.objects.select_for_update().get(pk=todo_id, user=user)

        # Partial update: only set provided allowed fields with normalization
        allowed_fields = {"title", "description", "completed", "priority", "due_date"}
        dirty = False
        for key, value in data.items():
            if key not in allowed_fields:
                continue
            if key == "completed":
                coerced = _coerce_bool(value)
                if coerced is None:
                    raise ValidationError({"completed": "Invalid boolean value."})
                if getattr(todo, "completed", None) != coerced:
                    setattr(todo, "completed", coerced)
                    dirty = True
            elif key == "due_date":
                parsed = _parse_due_date(value)
                if getattr(todo, "due_date", None) != parsed:
                    setattr(todo, "due_date", parsed)
                    dirty = True
            elif key == "priority":
                pr = _validate_priority(value)
                if getattr(todo, "priority", None) != pr:
                    setattr(todo, "priority", pr)
                    dirty = True
            elif key == "title":
                if value is None or (isinstance(value, str) and value.strip() == ""):
                    raise ValidationError({"title": "This field may not be blank."})
                if getattr(todo, "title", None) != value:
                    setattr(todo, "title", value)
                    dirty = True
            elif key == "description":
                if value is None:
                    value = ""
                if getattr(todo, "description", None) != value:
                    setattr(todo, "description", value)
                    dirty = True

        if dirty:
            # validate and save
            todo.full_clean()
            todo.save()

        return todo

    @staticmethod
    @transaction.atomic
    def delete_todo(user: Any, todo_id: Any) -> None:
        """
        Delete a todo that belongs to the given user. Raises Todo.DoesNotExist if not found.
        """
        if not getattr(user, "is_authenticated", False):
            raise PermissionDenied("Authentication required")

        todo = Todo.objects.select_for_update().get(pk=todo_id, user=user)
        # delete the instance
        todo.delete()
        return None
