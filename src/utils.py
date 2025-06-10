import logging
import os
from datetime import datetime
import uuid
import re
import math
from python_a2a import TaskStatus, TaskState

def setup_logging(agent_name: str):
    """Configure logging to a file for an agent."""
    log_dir = "logs"
    os.makedirs(log_dir, exist_ok=True)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    log_file = os.path.join(log_dir, f"{agent_name}_{timestamp}_{uuid.uuid4()}.log")
    
    logger = logging.getLogger(agent_name)
    logger.setLevel(logging.DEBUG)
    if not logger.handlers:  # Avoid duplicate handlers
        file_handler = logging.FileHandler(log_file)
        formatter = logging.Formatter("%(asctime)s - [%(levelname)s] %(name)s: %(message)s")
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)
    return logger

def parse_task_message(task) -> str:
    """Extract text from task message."""
    try:
        message = task.message or {}
        content = message.get("content", {})
        return content.get("text", "") if isinstance(content, dict) else str(content)
    except Exception as e:
        logging.error(f"Error parsing task message: {e}")
        return ""

def parse_angle(query: str) -> tuple[float, bool]:
    """Parse angle and unit (degrees or radians) from query."""
    query = query.lower()
    # Match number with optional decimal and unit
    pattern = r"([-+]?[0-9]*\.?[0-9]+)\s*(degrees?|deg|°|radians?|rad|π)?"
    match = re.search(pattern, query)
    if not match:
        return None, None
    
    value = float(match.group(1))
    unit = match.group(2) or ""
    
    if unit == "π":
        value *= math.pi
        is_degree = False
    else:
        is_degree = "degree" in unit or "deg" in unit or "°" in unit
        # Return original angle value and whether it's in degrees
        angle = value if not is_degree else math.radians(value)
    
    return angle, is_degree