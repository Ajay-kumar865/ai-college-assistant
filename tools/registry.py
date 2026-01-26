# tools/registry.py

from typing import Callable, Dict

from tools import (
    admission,
    hostel,
    events,
    notices,
    documents,
)

# Type alias for clarity
ToolFn = Callable[[str], str]

# Central registry: intent -> tool function
TOOL_REGISTRY: Dict[str, ToolFn] = {
    "admission": admission.run,
    "hostel": hostel.run,
    "event": events.run,
    "notice": notices.run,
    "document": documents.run,
}
