"""Skeleton classes for the PawPal+ system."""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import date, datetime, time
from typing import Any, Dict, List, Optional, Tuple
from uuid import uuid4


@dataclass
class Owner:
    """Represent a pet owner and the owner's scheduling constraints."""

    name: str = ""
    available_minutes: int = 0
    preferences: Dict[str, Any] = field(default_factory=dict)
    pets: List[Pet] = field(default_factory=list)

    def add_pet(self, pet: Pet) -> None:
        """Add a pet to the owner."""
        raise NotImplementedError

    def get_all_tasks(self) -> List[Task]:
        """Return all tasks belonging to the owner's pets."""
        raise NotImplementedError

    def update_availability(self, minutes: int) -> None:
        """Update the owner's available minutes."""
        raise NotImplementedError


@dataclass
class Pet:
    """Represent a pet and the tasks associated with it."""

    name: str = ""
    species: str = ""
    breed: str = ""
    age: int = 0
    tasks: List[Task] = field(default_factory=list)

    def add_task(self, task: Task) -> None:
        """Add a task to the pet."""
        raise NotImplementedError

    def remove_task(self, task_id: str) -> None:
        """Remove a task identified by task_id."""
        raise NotImplementedError

    def get_tasks_by_priority(self, priority: str) -> List[Task]:
        """Return tasks matching the requested priority."""
        raise NotImplementedError


@dataclass
class Task:
    """Represent a care task that can be scheduled for a pet."""

    title: str = ""
    category: str = ""
    duration_minutes: int = 0
    priority: str = "medium"
    preferred_time: Optional[time] = None
    recurrence: str = "once"
    start_date: Optional[date] = None
    recurrence_interval: int = 1
    recurrence_days: list[int] = field(default_factory=list)
    completed: bool = False
    task_id: str = field(default_factory=lambda: uuid4().hex[:8])

    def mark_complete(self) -> None:
        """Mark the task as completed."""
        raise NotImplementedError

    def is_due_today(self, target_date: date) -> bool:
        """Return whether the task is due on target_date."""
        raise NotImplementedError

    def update_details(
        self,
        title: Optional[str] = None,
        category: Optional[str] = None,
        duration_minutes: Optional[int] = None,
        priority: Optional[str] = None,
        preferred_time: Optional[time] = None,
        recurrence: Optional[str] = None,
        start_date: Optional[date] = None,
        recurrence_interval: Optional[int] = None,
        recurrence_days: Optional[list[int]] = None,
        completed: Optional[bool] = None,
    ) -> None:
        """Update any supplied task details."""
        raise NotImplementedError


@dataclass
class ScheduledItem:
    """Represent a task placed in a time slot in a daily plan."""

    task: Task = field(default_factory=Task)
    start_time: datetime = field(default_factory=datetime.now)
    end_time: datetime = field(default_factory=datetime.now)
    reason: str = ""

    def overlaps_with(self, other: ScheduledItem) -> bool:
        """Return whether this scheduled item overlaps another item."""
        raise NotImplementedError

    def format_display(self) -> str:
        """Return a display-friendly description of the scheduled item."""
        raise NotImplementedError


@dataclass
class DailyPlan:
    """Represent the scheduled care plan for a pet on a target date."""

    date: date = field(default_factory=date.today)
    pet_name: str = ""
    scheduled_items: List[ScheduledItem] = field(default_factory=list)
    skipped_tasks: List[Tuple[Task, str]] = field(default_factory=list)
    total_minutes_scheduled: int = 0

    def get_summary(self) -> str:
        """Return a summary of the daily plan."""
        raise NotImplementedError

    def get_conflicts(self) -> List[Tuple[ScheduledItem, ScheduledItem]]:
        """Return pairs of scheduled items that conflict."""
        raise NotImplementedError


@dataclass
class Scheduler:
    """Generate and explain daily schedules within owner constraints."""

    owner: Owner = field(default_factory=Owner)
    buffer_minutes: int = 0
    day_start: time = time(8, 0)
    day_end: time = time(20, 0)

    def generate_plan(self, target_date: date) -> DailyPlan:
        """Generate a daily plan for target_date."""
        raise NotImplementedError

    def sort_tasks(self, tasks: List[Task]) -> List[Task]:
        """Return tasks in scheduling order."""
        raise NotImplementedError

    def filter_due_tasks(
        self, tasks: List[Task], target_date: date
    ) -> List[Task]:
        """Return tasks due on target_date."""
        raise NotImplementedError

    def resolve_conflict(
        self,
        item_a: ScheduledItem,
        item_b: ScheduledItem,
    ) -> ScheduledItem:
        """Resolve a conflict between two scheduled items."""
        raise NotImplementedError

    def explain_decision(self, task: Task, status: str) -> str:
        """Explain why a task received its scheduling status."""
        raise NotImplementedError
