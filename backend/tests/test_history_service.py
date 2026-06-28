import asyncio
from uuid import uuid4

from app.services.history_service import delete_user_history, get_user_history


class FakeResult:
    def __init__(self, scalar=None, items=None, rowcount=0) -> None:
        self.scalar = scalar
        self.items = items or []
        self.rowcount = rowcount

    def scalar_one(self):
        return self.scalar

    def scalars(self):
        return self

    def all(self):
        return self.items


class FakeDatabase:
    def __init__(self, results) -> None:
        self.results = list(results)
        self.statements = []
        self.commit_count = 0

    async def execute(self, statement):
        self.statements.append(statement)
        return self.results.pop(0)

    async def commit(self) -> None:
        self.commit_count += 1


def test_get_user_history_returns_items_and_total() -> None:
    expected_items = [object(), object()]
    db = FakeDatabase([FakeResult(scalar=5), FakeResult(items=expected_items)])

    items, total = asyncio.run(get_user_history(db, str(uuid4()), limit=2, offset=2))

    assert items == expected_items
    assert total == 5
    assert len(db.statements) == 2


def test_delete_user_history_commits_and_returns_deleted_count() -> None:
    db = FakeDatabase([FakeResult(rowcount=4)])

    deleted = asyncio.run(delete_user_history(db, str(uuid4())))

    assert deleted == 4
    assert db.commit_count == 1
    assert len(db.statements) == 1
