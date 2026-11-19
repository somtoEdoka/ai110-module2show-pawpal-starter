"""Skeleton classes for the PawPal+ system."""

from __future__ import annotations

import json
from dataclasses import dataclass, field
from datetime import date, datetime, time, timedelta
from enum import Enum
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple
from uuid import uuid4


def _to_json_value(value: Any) -> Any:
    """Convert supported Python values to JSON-compatible values."""
    if isinstance(value, Enum):
        return _to_json_value(value.value)
    if isinstance(value, datetime):
        return {"$pawpal_type": "datetime", "value": value.isoformat()}
    if isinstance(value, date):
        return {"$pawpal_type": "date", "value": value.isoformat()}
    if isinstance(value, time):
        return {"$pawpal_type": "time", "value": value.isoformat()}
    if isinstance(value, dict):
        return {key: _to_json_value(item) for key, item in value.items()}
    if isinstance(value, (list, tuple)):
        return [_to_json_value(item) for item in value]
    if value is None or isinstance(value, (str, int, float, bool)):
        return value
    raise TypeError(f"Unsupported JSON value: {type(value).__name__}")


def _from_json_value(value: Any) -> Any:
    """Restore tagged date and time values from JSON-compatible data."""
    if isinstance(value, list):
        return [_from_json_value(item) for item in value]
    if not isinstance(value, dict):
        return value

    value_type = value.get("$pawpal_type")
    serialized_value = value.get("value")
    if value_type == "datetime":
        return datetime.fromisoformat(serialized_value)
    if value_type == "date":
        return date.fromisoformat(serialized_value)
    if value_type == "time":
        return time.fromisoformat(serialized_value)
    return {key: _from_json_value(item) for key, item in value.items()}


def _time_to_minutes(value: object) -> Optional[float]:
    """Convert a time object or HH:MM string to minutes after midnight."""
    if isinstance(value, time):
        return (
            value.hour * 60
            + value.minute
            + value.second / 60
            + value.microsecond / 60_000_000
        )
    if isinstance(value, str):
        try:
            parsed_time = time.fromisoformat(value.strip())
        except ValueError:
            return None
        return (
            parsed_time.hour * 60
            + parsed_time.minute
            + parsed_time.second / 60
            + parsed_time.microsecond / 60_000_000
        )
    return None


@dataclass
class Owner:
    """Represent a pet owner and the owner's scheduling constraints."""

    name: str = ""
    available_minutes: int = 0
    preferences: Dict[str, Any] = field(default_factory=dict)
    pets: List[Pet] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        """Return the owner and nested pets/tasks as JSON-compatible data."""
        return _to_json_value(
            {
                "name": self.name,
                "available_minutes": self.available_minutes,
                "preferences": self.preferences,
                "pets": [pet.to_dict() for pet in self.pets],
            }
        )

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> Owner:
        """Build an owner and nested pets/tasks from serialized data."""
        restored = _from_json_value(data)
        return cls(
            name=restored.get("name", ""),
            available_minutes=int(restored.get("available_minutes", 0)),
            preferences=restored.get("preferences", {}),
            pets=[Pet.from_dict(pet) for pet in restored.get("pets", [])],
        )

    def save_to_json(self, filepath: str | Path = "data.json") -> None:
        """Save this owner and its pets/tasks to a JSON file."""
        with Path(filepath).open("w", encoding="utf-8") as file:
            json.dump(self.to_dict(), file, indent=2, ensure_ascii=False)

    @classmethod
    def load_from_json(cls, filepath: str | Path = "data.json") -> Owner:
        """Load an owner and its pets/tasks from a JSON file."""
        with Path(filepath).open("r", encoding="utf-8") as file:
            data = json.load(file)
        if not isinstance(data, dict):
            raise ValueError("PawPal data must be a JSON object.")
        return cls.from_dict(data)

    def add_pet(self, pet: Pet) -> None:
        """Add a pet to the owner."""
        self.pets.append(pet)

    def get_all_tasks(self) -> List[Task]:
        """Return all tasks belonging to the owner's pets."""
        return [task for pet in self.pets for task in pet.tasks]

    def update_availability(self, minutes: int) -> None:
        """Update the owner's available minutes."""
        self.available_minutes = max(0, int(minutes))


@dataclass
class Pet:
    """Represent a pet and the tasks associated with it."""

    name: str = ""
    species: str = ""
    breed: str = ""
    age: int = 0
    tasks: List[Task] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        """Return the pet and its tasks as JSON-compatible data."""
        return _to_json_value(
            {
                "name": self.name,
                "species": self.species,
                "breed": self.breed,
                "age": self.age,
                "tasks": [task.to_dict() for task in self.tasks],
            }
        )

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> Pet:
        """Build a pet and its tasks from serialized data."""
        restored = _from_json_value(data)
        return cls(
            name=restored.get("name", ""),
            species=restored.get("species", ""),
            breed=restored.get("breed", ""),
            age=int(restored.get("age", 0)),
            tasks=[Task.from_dict(task) for task in restored.get("tasks", [])],
        )

    def add_task(self, task: Task) -> None:
        """Add a task to the pet."""
        self.tasks.append(task)

    def remove_task(self, task_id: str) -> None:
        """Remove a task identified by task_id."""
        self.tasks = [task for task in self.tasks if task.task_id != task_id]

    def get_tasks_by_priority(self, priority: str) -> List[Task]:
        """Return tasks matching the requested priority."""
        requested_priority = priority.strip().lower()
        return [
            task
            for task in self.tasks
            if task.priority.strip().lower() == requested_priority
        ]


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

    def to_dict(self) -> Dict[str, Any]:
        """Return this task as JSON-compatible data."""
        return _to_json_value(
            {
                "title": self.title,
                "category": self.category,
                "duration_minutes": self.duration_minutes,
                "priority": self.priority,
                "preferred_time": self.preferred_time,
                "recurrence": self.recurrence,
                "start_date": self.start_date,
                "recurrence_interval": self.recurrence_interval,
                "recurrence_days": self.recurrence_days,
                "completed": self.completed,
                "task_id": self.task_id,
            }
        )

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> Task:
        """Build a task from serialized data."""
        restored = _from_json_value(data)
        preferred_time = restored.get("preferred_time")
        start_date = restored.get("start_date")
        if isinstance(preferred_time, str):
            preferred_time = time.fromisoformat(preferred_time)
        if isinstance(start_date, str):
            start_date = date.fromisoformat(start_date)
        return cls(
            title=restored.get("title", ""),
            category=restored.get("category", ""),
            duration_minutes=int(restored.get("duration_minutes", 0)),
            priority=restored.get("priority", "medium"),
            preferred_time=preferred_time,
            recurrence=restored.get("recurrence", "once"),
            start_date=start_date,
            recurrence_interval=int(restored.get("recurrence_interval", 1)),
            recurrence_days=list(restored.get("recurrence_days", [])),
            completed=bool(restored.get("completed", False)),
            task_id=restored.get("task_id", uuid4().hex[:8]),
        )

    def mark_complete(self) -> None:
        """Mark the task as completed."""
        self.completed = True

    def is_due_today(self, target_date: date) -> bool:
        """Return whether the task is due on target_date."""
        recurrence = self.recurrence.strip().lower()
        start = self.start_date

        if recurrence == "once":
            return True if start is None else target_date == start

        if start is not None and target_date < start:
            return False

        interval = max(1, int(self.recurrence_interval or 1))

        if recurrence == "daily":
            if start is None:
                return True
            return (target_date - start).days % interval == 0

        if recurrence == "weekly":
            if not self.recurrence_days:
                if start is None:
                    return True
                if target_date.weekday() != start.weekday():
                    return False
                start_monday = start - timedelta(days=start.weekday())
                target_monday = target_date - timedelta(days=target_date.weekday())
                week_difference = (target_monday - start_monday).days // 7
                return week_difference % interval == 0

            allowed_weekdays: set[int] = set()
            day_names = {
                "monday": 0,
                "tuesday": 1,
                "wednesday": 2,
                "thursday": 3,
                "friday": 4,
                "saturday": 5,
                "sunday": 6,
                "mon": 0,
                "tue": 1,
                "wed": 2,
                "thu": 3,
                "fri": 4,
                "sat": 5,
                "sun": 6,
            }
            for value in self.recurrence_days:
                if isinstance(value, str):
                    weekday = day_names.get(value.strip().lower())
                    if weekday is not None:
                        allowed_weekdays.add(weekday)
                elif isinstance(value, int):
                    if 0 <= value <= 6:
                        allowed_weekdays.add(value)
                    elif 1 <= value <= 7:
                        allowed_weekdays.add(value - 1)

            if target_date.weekday() not in allowed_weekdays:
                return False

            if start is not None:
                start_monday = start - timedelta(days=start.weekday())
                target_monday = target_date - timedelta(days=target_date.weekday())
                week_difference = (target_monday - start_monday).days // 7
                return week_difference % interval == 0

            return True

        return False

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
        if title is not None:
            self.title = title
        if category is not None:
            self.category = category
        if duration_minutes is not None:
            self.duration_minutes = duration_minutes
        if priority is not None:
            self.priority = priority
        if preferred_time is not None:
            self.preferred_time = preferred_time
        if recurrence is not None:
            self.recurrence = recurrence
        if start_date is not None:
            self.start_date = start_date
        if recurrence_interval is not None:
            self.recurrence_interval = recurrence_interval
        if recurrence_days is not None:
            self.recurrence_days = recurrence_days
        if completed is not None:
            self.completed = completed


@dataclass
class ScheduledItem:
    """Represent a task placed in a time slot in a daily plan."""

    task: Task = field(default_factory=Task)
    start_time: datetime = field(default_factory=datetime.now)
    end_time: datetime = field(default_factory=datetime.now)
    reason: str = ""

    def overlaps_with(self, other: ScheduledItem) -> bool:
        """Return whether this scheduled item overlaps another item."""
        return self.start_time < other.end_time and other.start_time < self.end_time

    def format_display(self) -> str:
        """Return a display-friendly description of the scheduled item."""
        duration = max(0, int((self.end_time - self.start_time).total_seconds() // 60))
        return (
            f"{self.start_time.strftime('%H:%M')} — {self.task.title} "
            f"({duration} min) [priority: {self.task.priority.lower()}]"
        )


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
        if self.pet_name:
            lines = [f"Daily plan for {self.pet_name} on {self.date.isoformat()}:"]
        else:
            lines = [f"Daily plan for {self.date.isoformat()}:"]

        if self.scheduled_items:
            lines.extend(
                f"  {item.format_display()}" for item in self.scheduled_items
            )
        else:
            lines.append("  No tasks scheduled.")

        lines.append(f"Total scheduled: {self.total_minutes_scheduled} minutes")

        if self.skipped_tasks:
            lines.append("Skipped tasks:")
            lines.extend(
                f"  {task.title} — {reason}" for task, reason in self.skipped_tasks
            )

        return "\n".join(lines)

    def get_conflicts(self) -> List[Tuple[ScheduledItem, ScheduledItem]]:
        """Return pairs of scheduled items that conflict."""
        conflicts: List[Tuple[ScheduledItem, ScheduledItem]] = []
        for index, item in enumerate(self.scheduled_items):
            for other in self.scheduled_items[index + 1 :]:
                if item.overlaps_with(other):
                    conflicts.append((item, other))
        return conflicts


@dataclass
class Scheduler:
    """Generate and explain daily schedules within owner constraints."""

    owner: Owner = field(default_factory=Owner)
    buffer_minutes: int = 0
    day_start: time = time(8, 0)
    day_end: time = time(20, 0)

    def generate_plan(self, target_date: date) -> DailyPlan:
        """Generate a daily plan for target_date."""
        tasks = self.owner.get_all_tasks()
        due_tasks = self.filter_due_tasks(tasks, target_date)
        ordered_tasks = self.sort_tasks(due_tasks)

        pet_names = [pet.name for pet in self.owner.pets if pet.name]
        pet_name = ", ".join(pet_names)
        plan = DailyPlan(date=target_date, pet_name=pet_name)

        remaining_minutes = max(0, int(self.owner.available_minutes))
        start_datetime = datetime.combine(target_date, self.day_start)
        end_datetime = datetime.combine(target_date, self.day_end)
        cursor = start_datetime

        for task in ordered_tasks:
            duration = int(task.duration_minutes)
            if duration <= 0:
                plan.skipped_tasks.append((task, "Invalid duration"))
                continue

            if duration > remaining_minutes:
                plan.skipped_tasks.append(
                    (task, "Not enough available time")
                )
                continue

            if task.preferred_time is not None:
                preferred = datetime.combine(target_date, task.preferred_time)
                if preferred > cursor:
                    candidate_start = preferred
                else:
                    candidate_start = cursor
            else:
                candidate_start = cursor

            candidate_end = candidate_start + timedelta(minutes=duration)
            if candidate_start < start_datetime or candidate_end > end_datetime:
                plan.skipped_tasks.append(
                    (task, "Outside the planning window")
                )
                continue

            item = ScheduledItem(
                task=task,
                start_time=candidate_start,
                end_time=candidate_end,
                reason=self.explain_decision(task, "scheduled"),
            )
            plan.scheduled_items.append(item)
            plan.total_minutes_scheduled += duration
            remaining_minutes -= duration
            cursor = candidate_end + timedelta(minutes=max(0, int(self.buffer_minutes)))

        return plan

    def sort_tasks(self, tasks: List[Task]) -> List[Task]:
        """Return tasks in scheduling order."""
        priority_rank = {"high": 0, "medium": 1, "low": 2}

        def sort_key(task: Task) -> Tuple[int, time, str]:
            priority = priority_rank.get(task.priority.strip().lower(), 3)
            preferred = task.preferred_time or time(23, 59)
            return priority, preferred, task.title.lower()

        return sorted(tasks, key=sort_key)

    def sort_by_time(self, tasks: List[Task]) -> List[Task]:
        """Return tasks in chronological preferred-time order, with unscheduled tasks last."""
        return sorted(
            tasks,
            key=lambda task: (
                _time_to_minutes(task.preferred_time) is None,
                _time_to_minutes(task.preferred_time) or 0,
            ),
        )

    def sort_by_priority_and_time(self, tasks: List[Task]) -> List[Task]:
        """Sort tasks by priority, then preferred time with unscheduled tasks last."""
        priority_rank = {"high": 0, "medium": 1, "low": 2}

        def sort_key(task: Task) -> Tuple[int, bool, float]:
            preferred_minutes = _time_to_minutes(task.preferred_time)
            return (
                priority_rank.get(task.priority.strip().lower(), 3),
                preferred_minutes is None,
                preferred_minutes or 0,
            )

        return sorted(tasks, key=sort_key)

    def find_next_available_slot(
        self, target_date: date, duration_minutes: int
    ) -> Optional[datetime]:
        """Find the earliest window that fits between scheduled items."""
        if duration_minutes <= 0:
            return None

        plan = self.generate_plan(target_date)
        candidate_start = datetime.combine(target_date, self.day_start)
        day_end = datetime.combine(target_date, self.day_end)
        duration = timedelta(minutes=duration_minutes)
        buffer = timedelta(minutes=max(0, int(self.buffer_minutes)))

        scheduled_items = sorted(
            plan.scheduled_items, key=lambda item: item.start_time
        )
        for item in scheduled_items:
            if candidate_start + duration + buffer <= item.start_time:
                return candidate_start
            candidate_start = max(candidate_start, item.end_time + buffer)

        if candidate_start + duration <= day_end:
            return candidate_start
        return None

    def filter_tasks(
        self,
        pet_name: Optional[str] = None,
        completed: Optional[bool] = None,
    ) -> List[Task]:
        """Return owner tasks matching the requested pet and completion status."""
        requested_pet = pet_name.strip().casefold() if pet_name is not None else None
        return [
            task
            for pet in self.owner.pets
            if requested_pet is None or pet.name.strip().casefold() == requested_pet
            for task in pet.tasks
            if completed is None or task.completed is completed
        ]

    def mark_task_complete(self, task: Task) -> Optional[Task]:
        """Complete a task and add its next daily or weekly occurrence to the same pet."""
        if task.completed:
            return None

        recurrence = task.recurrence.strip().lower()
        owning_pet = next(
            (
                pet
                for pet in self.owner.pets
                if any(existing_task is task for existing_task in pet.tasks)
            ),
            None,
        )
        if recurrence in {"daily", "weekly"} and owning_pet is None:
            raise ValueError("Recurring tasks must belong to a pet owned by this scheduler.")

        task.mark_complete()
        if owning_pet is None or recurrence not in {"daily", "weekly"}:
            return None

        next_date = (task.start_date or date.today()) + timedelta(
            days=1 if recurrence == "daily" else 7
        )
        next_task = Task(
            title=task.title,
            category=task.category,
            duration_minutes=task.duration_minutes,
            priority=task.priority,
            preferred_time=task.preferred_time,
            recurrence=task.recurrence,
            start_date=next_date,
            recurrence_interval=task.recurrence_interval,
            recurrence_days=list(task.recurrence_days),
            completed=False,
        )
        owning_pet.add_task(next_task)
        return next_task

    def detect_conflicts(self, tasks: Optional[List[Task]] = None) -> List[str]:
        """Return readable warnings for tasks with matching or overlapping time slots."""
        candidate_tasks = self.owner.get_all_tasks() if tasks is None else tasks
        conflicts: List[str] = []
        for index, task in enumerate(candidate_tasks):
            start = _time_to_minutes(task.preferred_time)
            if start is None:
                continue
            try:
                duration = int(task.duration_minutes)
            except (TypeError, ValueError):
                continue
            if duration <= 0:
                continue

            end = start + duration
            for other in candidate_tasks[index + 1 :]:
                if (
                    task.start_date is not None
                    and other.start_date is not None
                    and task.start_date != other.start_date
                ):
                    continue
                other_start = _time_to_minutes(other.preferred_time)
                if other_start is None:
                    continue
                try:
                    other_duration = int(other.duration_minutes)
                except (TypeError, ValueError):
                    continue
                if other_duration <= 0:
                    continue

                other_end = other_start + other_duration
                if start == other_start or (start < other_end and other_start < end):
                    conflicts.append(
                        f"Conflict: '{task.title}' ({task.preferred_time}) and "
                        f"'{other.title}' ({other.preferred_time}) have overlapping "
                        "time slots."
                    )
        return conflicts

    def filter_due_tasks(
        self, tasks: List[Task], target_date: date
    ) -> List[Task]:
        """Return tasks due on target_date."""
        return [
            task
            for task in tasks
            if not task.completed and task.is_due_today(target_date)
        ]

    def resolve_conflict(
        self,
        item_a: ScheduledItem,
        item_b: ScheduledItem,
    ) -> ScheduledItem:
        """Resolve a conflict between two scheduled items."""
        if not item_a.overlaps_with(item_b):
            return item_a if item_a.start_time <= item_b.start_time else item_b

        priority_rank = {"high": 0, "medium": 1, "low": 2}
        rank_a = priority_rank.get(item_a.task.priority.strip().lower(), 3)
        rank_b = priority_rank.get(item_b.task.priority.strip().lower(), 3)
        if rank_a != rank_b:
            return item_a if rank_a < rank_b else item_b
        if item_a.start_time != item_b.start_time:
            return item_a if item_a.start_time < item_b.start_time else item_b
        return item_a if item_a.task.task_id <= item_b.task.task_id else item_b

    def explain_decision(self, task: Task, status: str) -> str:
        """Explain why a task received its scheduling status."""
        normalized_status = status.strip().lower()
        if normalized_status == "scheduled":
            return (
                f"{task.title} fits within the available time and planning window."
            )
        if "time" in normalized_status:
            return f"{task.title} was skipped because not enough time is available."
        if "window" in normalized_status:
            return f"{task.title} was skipped because it falls outside the planning window."
        return f"{task.title} was marked {normalized_status}."
