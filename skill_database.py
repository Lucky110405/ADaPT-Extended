"""
memory/skill_database mpdule: When a complex decomposition succeeds, "save" that plan as a new Atomic Skill in a database.

SQLite-backed Atomic Skill Cache.
When a complex decomposition succeeds, the plan is saved as a reusable "skill".
Future similar tasks retrieve and adapt the cached plan — avoiding re-planning from scratch.
"""

