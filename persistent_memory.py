"""persistent_memory.py

JSON-backed persistent memory for storing tasks and hierarchical subtasks.

Features:
- Tasks stored hierarchically (tasks contain nested `subtasks` arrays).
- Call history records the order tasks/subtasks were added (timestamps).
- Atomic file writes to avoid corruption.

Example usage (run the module as a script):
  python persistent_memory.py

The file `persistent_memory.json` will be created next to this module.
"""

from __future__ import annotations

import json
import os
import tempfile
import uuid
from datetime import datetime
from typing import Any, Dict, List, Optional, Tuple


def _now_iso() -> str:
	return datetime.utcnow().replace(microsecond=0).isoformat() + "Z"


class PersistentMemory:
	"""Simple JSON-backed persistent memory for tasks and subtasks.

	Data format:
	{
	  "tasks": [ { task-object }, ... ],
	  "call_history": [ {"id":..., "type":"task|subtask", "timestamp":...}, ... ]
	}
	"""

	def __init__(self, path: Optional[str] = None) -> None:
		if path is None:
			path = os.path.join(os.path.dirname(__file__), "persistent_memory.json")
		self.path = path
		self._data: Dict[str, Any] = {"tasks": [], "call_history": [], "map": {}}
		self._load()

	# --- persistence helpers ---
	def _load(self) -> None:
		if os.path.exists(self.path):
			try:
				with open(self.path, "r", encoding="utf-8") as f:
					self._data = json.load(f)
			except Exception:
				# If load fails, keep an empty structure but do not overwrite immediately
				self._data = {"tasks": [], "call_history": []}

	def _save(self) -> None:
		dirpath = os.path.dirname(self.path)
		if dirpath and not os.path.exists(dirpath):
			os.makedirs(dirpath, exist_ok=True)
		tmp_fd, tmp_path = tempfile.mkstemp(dir=dirpath, prefix=".pm_", text=True)
		try:
			with os.fdopen(tmp_fd, "w", encoding="utf-8") as tmpf:
				json.dump(self._data, tmpf, indent=2, ensure_ascii=False)
			os.replace(tmp_path, self.path)
		finally:
			if os.path.exists(tmp_path):
				try:
					os.remove(tmp_path)
				except Exception:
					pass

	# --- helpers to navigate and mutate the task tree ---
	@staticmethod
	def _make_node(title: str, description: Optional[str] = None, metadata: Optional[Dict] = None) -> Dict:
		return {
			"id": str(uuid.uuid4()),
			"title": title,
			"description": description or "",
			"metadata": metadata or {},
			"created_at": _now_iso(),
			"completed": False,
			"completed_at": None,
			"subtasks": [],
		}

	def _find_node(self, node_list: List[Dict], node_id: str) -> Optional[Dict]:
		for node in node_list:
			if node.get("id") == node_id:
				return node
			found = self._find_node(node.get("subtasks", []), node_id)
			if found:
				return found
		return None

	def _find_parent(self, node_list: List[Dict], child_id: str) -> Optional[Tuple[List[Dict], Dict]]:
		for node in node_list:
			for child in node.get("subtasks", []):
				if child.get("id") == child_id:
					return node.get("subtasks"), node
			result = self._find_parent(node.get("subtasks", []), child_id)
			if result:
				return result
		return None

	# --- public API ---
	def create_task(self, title: str, description: Optional[str] = None, metadata: Optional[Dict] = None) -> str:
		"""Create a top-level task and return its id."""
		node = self._make_node(title, description, metadata)
		self._data.setdefault("tasks", []).append(node)
		self._data.setdefault("call_history", []).append({"id": node["id"], "type": "task", "timestamp": node["created_at"]})
		self._save()
		return node["id"]

	def add_subtask(self, parent_id: str, title: str, description: Optional[str] = None, metadata: Optional[Dict] = None) -> Optional[str]:
		"""Add a subtask under `parent_id`. Returns the subtask id or None if parent not found."""
		parent = self._find_node(self._data.get("tasks", []), parent_id)
		if parent is None:
			return None
		node = self._make_node(title, description, metadata)
		parent.setdefault("subtasks", []).append(node)
		self._data.setdefault("call_history", []).append({"id": node["id"], "type": "subtask", "parent_id": parent_id, "timestamp": node["created_at"]})
		self._save()
		return node["id"]

	def mark_completed(self, node_id: str) -> bool:
		node = self._find_node(self._data.get("tasks", []), node_id)
		if not node:
			return False
		node["completed"] = True
		node["completed_at"] = _now_iso()
		self._save()
		return True

	def get_hierarchy(self) -> List[Dict]:
		"""Return the hierarchical tasks structure (deep copy is not performed)."""
		return self._data.get("tasks", [])

	# --- nested map (user requested) ---
	def add_task_path(self, path: List[str]) -> None:
		"""Create nested map keys for the path.

		Example: path=["task1","task2","task4"] results in:
		{"task1": {"task2": {"task4": {}}}}
		Order of insertion is preserved by Python dicts (3.7+).
		"""
		if not path:
			return
		node = self._data.setdefault("map", {})
		for part in path:
			if part not in node:
				node[part] = {}
			node = node[part]
		# record call history as the path string
		self._data.setdefault("call_history", []).append({
			"id": "::".join(path),
			"type": "map_node",
			"path": path,
			"timestamp": _now_iso(),
		})
		self._save()

	def get_map(self) -> Dict[str, Any]:
		"""Return the nested map structure used for compact hierarchical JSON."""
		return self._data.get("map", {})

	def get_call_history(self) -> List[Dict]:
		"""Return the call history array in the order items were added."""
		return self._data.get("call_history", [])

	def find(self, node_id: str) -> Optional[Dict]:
		return self._find_node(self._data.get("tasks", []), node_id)

	def list_tasks_flat(self) -> List[Dict]:
		"""Return a flat list of all tasks + subtasks in creation order by traversing timestamps."""
		flat: List[Dict] = []

		def _walk(nodes: List[Dict]):
			for n in nodes:
				flat.append(n)
				_walk(n.get("subtasks", []))

		_walk(self._data.get("tasks", []))
		flat.sort(key=lambda n: n.get("created_at", ""))
		return flat


if __name__ == "__main__":
	pm = PersistentMemory()
	# Demo: create nested map structure and print only the compact map
	pm.add_task_path(["task1", "task2", "task4"])
	pm.add_task_path(["task1", "task3", "task5", "task7"])
	pm.add_task_path(["task1", "task3", "task6"])
	print(json.dumps(pm.get_map(), indent=2, ensure_ascii=False))
