from python_a2a import A2AServer, skill, agent, run_server, TaskStatus, TaskState
from src.utils import setup_logging, parse_task_message
import re
import logging

@agent(
    name="Coding Agent",
    description="Generates executable Python code for trigonometric functions, equations, or identities. Specifically for queries like 'code for sine calculation', 'python function for angle sum identity', 'generate code for cos(2θ) formula'. This agent provides runnable Python scripts/functions.",
    version="1.0.0"
)
class CodingAgent(A2AServer):
    def __init__(self):
        super().__init__()
        self.logger = setup_logging(self.__class__.__name__)

    @skill(
        name="Generate Trigonometric Code",
        description="Generates Python code for trigonometric equations or calculations. Examples: 'Generate code for sine calculation', 'Python code for angle sum identity', 'Code for cos(2θ)', 'write python code for tangent', 'give me a function for double angle sine'.",
        tags=["trigonometry", "code", "python", "programming", "generator", "function", "script"],
        examples=["Generate code for sine calculation", "Python code for angle sum identity", "Code for cos(2θ)", "write python code for tangent", "give me a function for double angle sine"]
    )
    def generate_code(self, query: str):
        """Generate Python code for trigonometric equations or calculations."""
        query = query.lower().strip()
        self.logger.debug(f"Processing coding query: '{query}'")
        
        # Prioritize more specific matches
        if "double angle" in query:
            code = """import math

def double_angle_sine(theta_degrees):
    \"\"\"Calculate sin(2θ) using double angle identity.\"\"\"
    theta_rad = math.radians(theta_degrees)
    return 2 * math.sin(theta_rad) * math.cos(theta_rad)

def double_angle_cosine(theta_degrees):
    \"\"\"Calculate cos(2θ) using double angle identity.\"\"\"
    theta_rad = math.radians(theta_degrees)
    # Different forms: cos^2(theta) - sin^2(theta) or 2cos^2(theta) - 1 or 1 - 2sin^2(theta)
    return math.cos(theta_rad)**2 - math.sin(theta_rad)**2

def double_angle_tangent(theta_degrees):
    \"\"\"Calculate tan(2θ) using double angle identity.\"\"\"
    theta_rad = math.radians(theta_degrees)
    tan_theta = math.tan(theta_rad)
    denominator = 1 - tan_theta**2
    if abs(denominator) < 1e-9: # Check for division by zero (tangent of 2*theta undefined)
        return "Undefined (angle or double angle is near an odd multiple of 90 degrees)"
    return (2 * tan_theta) / denominator

# Example usage
theta = 30  # degrees
print(f"sin(2 * {theta}) = {double_angle_sine(theta):.4f}")
print(f"cos(2 * {theta}) = {double_angle_cosine(theta):.4f}")
print(f"tan(2 * {theta}) = {double_angle_tangent(theta):.4f}")"""

        elif "angle sum" in query or "angle difference" in query:
            code = """import math

def angle_sum_sine(a_degrees, b_degrees):
    \"\"\"Calculate sin(a + b) using angle sum identity.\"\"\"
    a_rad = math.radians(a_degrees)
    b_rad = math.radians(b_degrees)
    return math.sin(a_rad) * math.cos(b_rad) + math.cos(a_rad) * math.sin(b_rad)

def angle_sum_cosine(a_degrees, b_degrees):
    \"\"\"Calculate cos(a + b) using angle sum identity.\"\"\"
    a_rad = math.radians(a_degrees)
    b_rad = math.radians(b_degrees)
    return math.cos(a_rad) * math.cos(b_rad) - math.sin(a_rad) * math.sin(b_rad)

def angle_sum_tangent(a_degrees, b_degrees):
    \"\"\"Calculate tan(a + b) using angle sum identity.\"\"\"
    a_rad = math.radians(a_degrees)
    b_rad = math.radians(b_degrees)
    tan_a = math.tan(a_rad)
    tan_b = math.tan(b_rad)
    denominator = 1 - tan_a * tan_b
    if abs(denominator) < 1e-9:
        return "Undefined (denominator is zero)"
    return (tan_a + tan_b) / denominator

# Example usage
a, b = 30, 45  # degrees
print(f"sin({a} + {b}) = {angle_sum_sine(a, b):.4f}")
print(f"cos({a} + {b}) = {angle_sum_cosine(a, b):.4f}")
print(f"tan({a} + {b}) = {angle_sum_tangent(a, b):.4f}")"""

        elif "sine" in query or "sin" in query:
            code = """import math

def calculate_sine(angle_degrees):
    \"\"\"Calculate sine of an angle in degrees.\"\"\"
    angle_radians = math.radians(angle_degrees)
    return math.sin(angle_radians)

# Example usage
angle = 30  # degrees
result = calculate_sine(angle)
print(f"Sine of {angle} degrees is {result:.4f}")"""

        elif "cosine" in query or "cos" in query:
            code = """import math

def calculate_cosine(angle_degrees):
    \"\"\"Calculate cosine of an angle in degrees.\"\"\"
    angle_radians = math.radians(angle_degrees)
    return math.cos(angle_radians)

# Example usage
angle = 30  # degrees
result = calculate_cosine(angle)
print(f"Cosine of {angle} degrees is {result:.4f}")"""

        elif "tangent" in query or "tan" in query:
            code = """import math

def calculate_tangent(angle_degrees):
    \"\"\"Calculate tangent of an angle in degrees.\"\"\"
    angle_radians = math.radians(angle_degrees)
    if abs(math.cos(angle_radians)) < 1e-9:
        return "Undefined (angle is near an odd multiple of 90 degrees)"
    return math.tan(angle_radians)

# Example usage
angle = 45  # degrees
result = calculate_tangent(angle)
print(f"Tangent of {angle} degrees is {result:.4f}")"""

        # Generic fallback if no specific match
        else:
            self.logger.warning(f"No specific code generation pattern matched for query: '{query}'. Providing generic example.")
            code = """import math

def example_trig_function(angle_degrees, func_type="sin"):
    \"\"\"
    Example trigonometric function. Modify func_type to 'cos' or 'tan' as needed.
    For more complex functions or identities, specify in your query.
    \"\"\"
    angle_radians = math.radians(angle_degrees)
    if func_type == "sin":
        return math.sin(angle_radians)
    elif func_type == "cos":
        return math.cos(angle_radians)
    elif func_type == "tan":
        if abs(math.cos(angle_radians)) < 1e-9:
            return "Undefined"
        return math.tan(angle_radians)
    else:
        return "Unsupported function type"

# Example usage
angle = 30  # degrees
result = example_trig_function(angle, "sin")
print(f"Sine of {angle} degrees is {result:.4f}")"""
        
        return f"```python\n{code}\n```"

    def handle_task(self, task):
        text = parse_task_message(task)
        text_lower = text.lower().strip()
        self.logger.info(f"CodingAgent received task: '{text}'")
        
        has_code_keywords = any(k in text_lower for k in ["code", "python", "generate code", "write code", "function", "script", "program"])
        has_trig_keywords = any(k in text_lower for k in ["sin", "sine", "cos", "cosine", "tan", "tangent", "trigonometry", "angle sum", "double angle", "half angle", "identity"])
        
        # Refined condition: must contain clear code intent AND trig related terms
        # It should NOT contain terms that clearly point to calculation or identity listing
        is_calculation_or_identity_phrase = any(k in text_lower for k in ["calculate", "value of", "what is", "list", "show", "tell me about", "formula", "identities"])
        
        if has_code_keywords and has_trig_keywords and not is_calculation_or_identity_phrase:
            result = self.generate_code(text)
            task.artifacts = [{"parts": [{"type": "text", "text": result}]}]
            task.status = TaskStatus(state=TaskState.COMPLETED)
        else:
            self.logger.warning(f"CodingAgent determined input '{text}' is not for code generation (Code keywords: {has_code_keywords}, Trig keywords: {has_trig_keywords}, Is Calc/Identity Phrase: {is_calculation_or_identity_phrase}).")
            task.status = TaskStatus(
                state=TaskState.INPUT_REQUIRED,
                message={"role": "agent", "content": {"text": "Please ask for Python code related to trigonometry (e.g., 'code for sine calculation' or 'generate a function for angle sum identity')."}}
            )
        
        return task

if __name__ == "__main__":
    agent = CodingAgent()
    run_server(agent, port=8003, debug=True)