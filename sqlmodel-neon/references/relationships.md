# SQLModel Relationships Guide

This guide covers defining and working with relationships in SQLModel.

## One-to-Many Relationships

The most common relationship - one parent, many children.

```python
from sqlmodel import SQLModel, Field, Relationship
from typing import List, Optional

class Team(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    name: str
    heroes: List["Hero"] = Relationship(back_populates="team")


class Hero(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    name: str
    team_id: int | None = Field(default=None, foreign_key="team.id")
    team: Team | None = Relationship(back_populates="heroes")
```

### Using One-to-Many Relationships

```python
# Create team with heroes
team = Team(name="Avengers")
hero1 = Hero(name="Iron Man", team=team)
hero2 = Hero(name="Captain America", team=team)

with Session(engine) as session:
    session.add(team)
    session.commit()
    session.refresh(team)
    # team.heroes will contain both heroes
```

## Many-to-Many Relationships

Requires a link table with foreign keys to both models.

```python
class Hero(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    name: str
    teams: List["Team"] = Relationship(back_populates="heroes", link_model="HeroTeamLink")


class Team(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    name: str
    heroes: List["Hero"] = Relationship(back_populates="teams", link_model="HeroTeamLink")


class HeroTeamLink(SQLModel, table=True):
    team_id: int | None = Field(default=None, foreign_key="team.id", primary_key=True)
    hero_id: int | None = Field(default=None, foreign_key="hero.id", primary_key=True)
```

### Using Many-to-Many Relationships

```python
# Create heroes and teams
iron_man = Hero(name="Iron Man")
cap = Hero(name="Captain America")
avengers = Team(name="Avengers")
defenders = Team(name="Defenders")

iron_man.teams.append(avengers)
iron_man.teams.append(defenders)
cap.teams.append(avengers)

with Session(engine) as session:
    session.add(iron_man)
    session.add(cap)
    session.commit()
```

## One-to-One Relationships

Use `sa_relationship_kwargs` with `uselist=False`:

```python
from sqlmodel import Field, Relationship
from sqlalchemy.orm import sa_relationship

class User(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    email: str
    profile: "Profile" = Relationship(
        back_populates="user",
        sa_relationship_kwargs={"uselist": False}
    )


class Profile(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    bio: str | None = None
    user_id: int | None = Field(default=None, foreign_key="user.id")
    user: User = Relationship(
        back_populates="profile",
        sa_relationship_kwargs={"uselist": False}
    )
```

## Lazy vs Eager Loading

### Lazy Loading (default)

Relationships are loaded when accessed:

```python
with Session(engine) as session:
    hero = session.get(Hero, 1)
    # team is not loaded yet
    print(hero.team)  # team loaded here
```

### Eager Loading with selectin

Load relationships in the same query:

```python
from sqlmodel import select

with Session(engine) as session:
    statement = select(Hero).where(Hero.name == "Iron Man")
    result = session.exec(statement).one()
    session.refresh(result, ["team"])  # Explicitly load
```

### Eager Loading with joined

Join tables for better performance:

```python
from sqlmodel import selectinload

with Session(engine) as session:
    statement = (
        select(Hero)
        .options(selectinload(Hero.team))
        .where(Hero.name == "Iron Man")
    )
    result = session.exec(statement).one()
```

## Cascading Operations

Automatically delete children when parent is deleted:

```python
from sqlalchemy import cascade

class Parent(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    name: str
    children: List["Child"] = Relationship(
        back_populates="parent",
        sa_relationship_kwargs={
            "cascade": "all, delete-orphan"
        }
    )


class Child(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    name: str
    parent_id: int | None = Field(default=None, foreign_key="parent.id")
    parent: Parent = Relationship(back_populates="children")
```

## Self-Referential Relationships

Models that reference themselves (e.g., categories, hierarchies):

```python
class Category(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    name: str
    parent_id: int | None = Field(default=None, foreign_key="category.id")
    parent: "Category | None" = Relationship(
        back_populates="children",
        sa_relationship_kwargs={"remote_side": "Category.id"}
    )
    children: List["Category"] = Relationship(back_populates="parent")
```

## Async Relationships

For async sessions, refresh relationships explicitly:

```python
async def get_hero_with_team(hero_id: int):
    async with async_session_maker() as session:
        hero = await session.get(Hero, hero_id)
        await session.refresh(hero, ["team"])
        return hero
```

## Relationship Tips

1. **Always define both sides** - Use `back_populates` on both models
2. **Foreign key on child** - The "many" side gets the foreign key
3. **Link table for many-to-many** - Create a separate table model
4. **Consider performance** - Use eager loading for relationships you always need
5. **Cascade carefully** - Only use cascade deletes when appropriate
