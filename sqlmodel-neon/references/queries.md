# Advanced SQLModel Queries

This guide covers advanced querying patterns with SQLModel.

## Select with Filtering

### Basic Filtering

```python
from sqlmodel import select, Session

with Session(engine) as session:
    # Simple equals
    statement = select(User).where(User.email == "user@example.com")

    # Multiple conditions (AND)
    statement = select(User).where(
        User.is_active == True,
        User.age >= 18
    )

    # OR conditions
    from sqlmodel import or_
    statement = select(User).where(
        or_(User.age < 18, User.age > 65)
    )

    result = session.exec(statement).all()
```

### Case-Insensitive Search

```python
from sqlmodel import col

with Session(engine) as session:
    # Contains (LIKE %term%)
    statement = select(User).where(
        col(User.email).icontains("example.com")
    )

    # Starts with
    statement = select(User).where(
        col(User.name).istartswith("John")
    )

    # Ends with
    statement = select(User).where(
        col(User.name).iendswith("Smith")
    )
```

### IN and NOT IN

```python
with Session(engine) as session:
    # IN query
    statement = select(User).where(User.id.in_([1, 2, 3]))

    # NOT IN query
    statement = select(User).where(User.id.not_in([4, 5, 6]))
```

### IS NULL and IS NOT NULL

```python
with Session(engine) as session:
    # IS NULL
    statement = select(User).where(User.full_name == None)

    # IS NOT NULL
    statement = select(User).where(User.full_name != None)

    # Alternative
    from sqlmodel import is_, is_not
    statement = select(User).where(is_(User.deleted_at, None))
```

## Ordering and Limiting

```python
with Session(engine) as session:
    # Order by ascending
    statement = select(User).order_by(User.created_at)

    # Order by descending
    from sqlmodel import desc
    statement = select(User).order_by(desc(User.created_at))

    # Multiple order by
    statement = select(User).order_by(
        User.last_name.asc(),
        User.first_name.asc()
    )

    # Limit and offset (pagination)
    statement = select(User).offset(0).limit(10)

    # Page 2
    page = 2
    per_page = 10
    statement = select(User).offset((page-1) * per_page).limit(per_page)
```

## Joins

### Inner Join

```python
with Session(engine) as session:
    statement = select(User, Post).join(
        Post, User.id == Post.user_id
    ).where(Post.published == True)

    results = session.exec(statement)
    for user, post in results:
        print(f"{user.email} wrote {post.title}")
```

### Left Join (Outer Join)

```python
from sqlmodel import left

with Session(engine) as session:
    statement = select(User, Post).join(
        Post, User.id == Post.user_id, isouter=True
    )

    results = session.exec(statement)
    for user, post in results:
        # Post will be None for users without posts
        if post:
            print(f"{user.email} wrote {post.title}")
        else:
            print(f"{user.email} has no posts")
```

### Select Specific Columns

```python
with Session(engine) as session:
    # Select specific columns
    statement = select(User.id, User.email, User.full_name)

    results = session.exec(statement)
    for user_id, email, name in results:
        print(f"{user_id}: {email}")

    # With labels
    from sqlalchemy import label
    statement = select(
        label("user_id", User.id),
        label("user_email", User.email)
    )
```

## Aggregations

### Count

```python
from sqlalchemy import func

with Session(engine) as session:
    # Count all
    statement = select(func.count()).select_from(User)
    count = session.exec(statement).one()

    # Count with condition
    statement = select(func.count()).select_from(User).where(User.is_active == True)
    active_count = session.exec(statement).one()
```

### Sum, Avg, Min, Max

```python
with Session(engine) as session:
    # Sum
    statement = select(func.sum(Order.amount))
    total = session.exec(statement).one()

    # Average
    statement = select(func.avg(Order.amount))
    average = session.exec(statement).one()

    # Min/Max
    statement = select(
        func.min(Order.amount),
        func.max(Order.amount)
    )
    min_amt, max_amt = session.exec(statement).one()
```

### Group By

```python
with Session(engine) as session:
    statement = select(
        Post.user_id,
        func.count(Post.id).label("post_count")
    ).group_by(Post.user_id).order_by(desc("post_count"))

    results = session.exec(statement)
    for user_id, count in results:
        print(f"User {user_id}: {count} posts")
```

### Having (filter groups)

```python
with Session(engine) as session:
    statement = select(
        Post.user_id,
        func.count(Post.id).label("post_count")
    ).group_by(Post.user_id).having(
        func.count(Post.id) > 5
    )

    results = session.exec(statement)
```

## Subqueries

### Subquery in WHERE clause

```python
from sqlalchemy import exists

with Session(engine) as session:
    # Find users who have posts
    subquery = select(Post.id).where(Post.user_id == User.id)
    statement = select(User).where(exists(subquery))

    results = session.exec(statement).all()
```

### Subquery in FROM clause

```python
from sqlalchemy import alias

with Session(engine) as session:
    # Average posts per user
    subq = select(
        Post.user_id,
        func.count(Post.id).label("count")
    ).group_by(Post.user_id).subquery()

    user_post_counts = alias(subq, "user_post_counts")

    statement = select(
        User,
        user_post_counts.c.count
    ).join(user_post_counts, User.id == user_post_counts.c.user_id)
```

## Window Functions

```python
from sqlalchemy.over
from sqlalchemy.sql.expression import label

with Session(engine) as session:
    statement = select(
        Post.id,
        Post.title,
        func.row_number().over(
            order_by=Post.created_at,
            partition_by=Post.user_id
        ).label("row_num")
    )

    results = session.exec(statement)
```

## Upsert (Update or Insert)

PostgreSQL-specific upert with ON CONFLICT:

```python
from sqlalchemy.dialects.postgresql import insert

with Session(engine) as session:
    stmt = insert(User).values(
        email="user@example.com",
        name="User"
    ).on_conflict_do_update(
        index_elements=['email'],
        set_=dict(name="Updated User")
    )

    session.execute(stmt)
    session.commit()
```

## Batch Operations

### Bulk Insert

```python
with Session(engine) as session:
    users = [
        User(email="user1@example.com", name="User 1"),
        User(email="user2@example.com", name="User 2"),
        User(email="user3@example.com", name="User 3"),
    ]
    session.add_all(users)
    session.commit()
```

### Bulk Update

```python
with Session(engine) as session:
    # Update all matching rows
    statement = (
        update(User)
        .where(User.is_active == False)
        .values(is_active=True)
    )
    session.exec(statement)
    session.commit()
```

### Bulk Delete

```python
from sqlmodel import delete

with Session(engine) as session:
    statement = delete(User).where(User.last_login < "2024-01-01")
    session.exec(statement)
    session.commit()
```

## Raw SQL

When you need raw SQL:

```python
from sqlalchemy import text

with Session(engine) as session:
    result = session.execute(
        text("SELECT * FROM users WHERE email = :email"),
        {"email": "user@example.com"}
    )

    for row in result:
        print(row)
```

## Query Tips

1. **Use indexes** - Create indexes on frequently filtered columns
2. **Limit results** - Always use limit with potentially large datasets
3. **Select only needed columns** - Don't fetch everything if not needed
4. **Use joins efficiently** - Consider N+1 query problems
5. **Profile queries** - Use `echo=True` in engine to see SQL
