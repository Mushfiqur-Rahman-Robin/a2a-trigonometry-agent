from python_a2a import A2AServer, skill, agent, run_server, TaskStatus, TaskState
from src.utils import setup_logging, parse_task_message, parse_angle
import math
import re
import sys

@agent(
    name="Trigonometry Agent",
    description="Calculates trigonometric functions (sine, cosine, tangent, cosecant, secant, cotangent) for specific angles in degrees or radians and provides trigonometric identities (basic, angle sum/difference, double angle, half angle, product-to-sum, sum-to-product, reciprocal/quotient, cofunction). Not for generating code.",
    version="1.0.0"
)
class TrigonometryAgent(A2AServer):
    FUNCTION_SYNONYMS = {
        "sin": "sine", "sine": "sine",
        "cos": "cosine", "cosine": "cosine",
        "tan": "tangent", "tangent": "tangent",
        "csc": "cosecant", "cosecant": "cosecant",
        "sec": "secant", "secant": "secant",
        "cot": "cotangent", "cotangent": "cotangent"
    }
    
    IDENTITY_GROUPS = {
        "basic": [
            "sin²(θ) + cos²(θ) = 1",
            "1 + tan²(θ) = sec²(θ)",
            "1 + cot²(θ) = csc²(θ)"
        ],
        "angle_sum_diff": [
            "sin(a ± b) = sin(a)cos(b) ± cos(a)sin(b)",
            "cos(a ± b) = cos(a)cos(b) ∓ sin(a)sin(b)",
            "tan(a ± b) = (tan(a) ± tan(b)) / (1 ∓ tan(a)tan(b))"
        ],
        "double_angle": [
            "sin(2θ) = 2sin(θ)cos(θ)",
            "cos(2θ) = cos²(θ) - sin²(θ)",
            "tan(2θ) = (2tan(θ)) / (1 - tan²(θ))"
        ],
        "half_angle": [
            "sin(θ/2) = ±√((1 - cos(θ))/2)",
            "cos(θ/2) = ±√((1 + cos(θ))/2)",
            "tan(θ/2) = (1 - cos(θ))/sin(θ)"
        ],
        "product_to_sum": [
            "sin(a)sin(b) = (1/2)[cos(a-b) - cos(a+b)]",
            "cos(a)cos(b) = (1/2)[cos(a+b) + cos(a-b)]",
            "sin(a)cos(b) = (1/2)[sin(a+b) + sin(a-b)]"
        ],
        "sum_to_product": [
            "sin(a) + sin(b) = 2sin((a+b)/2)cos((a-b)/2)",
            "sin(a) - sin(b) = 2cos((a+b)/2)sin((a-b)/2)",
            "cos(a) + cos(b) = 2cos((a+b)/2)cos((a-b)/2)"
        ],
        "reciprocal_quotient": [
            "csc(θ) = 1/sin(θ)",
            "sec(θ) = 1/cos(θ)",
            "cot(θ) = 1/tan(θ)",
            "tan(θ) = sin(θ)/cos(θ)",
            "cot(θ) = cos(θ)/sin(θ)"
        ],
        "cofunction": [
            "sin(π/2 - θ) = cos(θ)",
            "cos(π/2 - θ) = sin(θ)",
            "tan(π/2 - θ) = cot(θ)"
        ]
    }
    
    KEYWORDS_IDENTITIES = {
        "basic": ["basic", "pythagorean", "fundamental"],
        "angle_sum_diff": ["angle sum", "angle difference", "sum identities", "difference identities", "sum formula", "difference formula"],
        "double_angle": ["double angle", "double"],
        "half_angle": ["half angle", "half"],
        "product_to_sum": ["product to sum", "product-to-sum", "product identities"],
        "sum_to_product": ["sum to product", "sum-to-product"],
        "reciprocal_quotient": ["reciprocal", "quotient"],
        "cofunction": ["cofunction"]
    }

    def __init__(self):
        super().__init__()
        self.logger = setup_logging(self.__class__.__name__)

    @skill(
        name="Get Trigonometric Calculation",
        description="Calculates trigonometric functions (sine, cosine, tangent, cosecant, secant, cotangent) for specific angles in degrees or radians. Example queries: 'sine of 30 degrees', 'calculate tan of 1.57 radians', 'sin 30 deg'.",
        tags=["trigonometry", "calculate", "sine", "cosine", "tangent", "cosecant", "secant", "cotangent", "math", "value", "evaluation"],
        examples=["Calculate sine of 30 degrees", "Tan of 1.57 radians", "Sin 30 deg", "What is cos(45)?", "Evaluate secant of pi/3"]
    )
    def get_calculation(self, query: str):
        """Calculate trigonometric functions."""
        query = query.lower().strip()
        self.logger.debug(f"Attempting calculation for query: '{query}'")
        
        angle_rad, is_degree = parse_angle(query)
        if angle_rad is None:
            return "Could not extract a valid angle. Please specify an angle (e.g., 'sine of 30 degrees')."

        # Determine display value based on original unit for user clarity
        display_angle_val = math.degrees(angle_rad) if is_degree else angle_rad
        unit = 'degrees' if is_degree else 'radians'
        
        func = None
        for key, value in self.FUNCTION_SYNONYMS.items():
            if key in query:
                func = value
                break
        
        if func is None:
            return "Please specify a trigonometric function to calculate (e.g., sine, cosine, tangent)."

        try:
            if func == "sine":
                return f"The sine of {display_angle_val:.2f} {unit} is {math.sin(angle_rad):.4f}"
            elif func == "cosine":
                return f"The cosine of {display_angle_val:.2f} {unit} is {math.cos(angle_rad):.4f}"
            elif func == "tangent":
                # Check for undefined points (multiples of pi/2 + pi*n for tan)
                if abs(math.cos(angle_rad)) < 1e-9:
                    return f"The tangent of {display_angle_val:.2f} {unit} is undefined (angle is near a multiple of π/2 where cosine is zero)."
                return f"The tangent of {display_angle_val:.2f} {unit} is {math.tan(angle_rad):.4f}"
            elif func == "cosecant":
                sin_val = math.sin(angle_rad)
                if abs(sin_val) < 1e-9:
                    return f"The cosecant of {display_angle_val:.2f} {unit} is undefined (angle is near a multiple of π radians where sine is zero)."
                return f"The cosecant of {display_angle_val:.2f} {unit} is {(1/sin_val):.4f}"
            elif func == "secant":
                cos_val = math.cos(angle_rad)
                if abs(cos_val) < 1e-9:
                    return f"The secant of {display_angle_val:.2f} {unit} is undefined (angle is near an odd multiple of 90 degrees or π/2 radians where cosine is zero)."
                return f"The secant of {display_angle_val:.2f} {unit} is {(1/cos_val):.4f}"
            elif func == "cotangent":
                sin_val = math.sin(angle_rad)
                if abs(sin_val) < 1e-9:
                    return f"The cotangent of {display_angle_val:.2f} {unit} is undefined (angle is near a multiple of π radians where sine is zero)."
                return f"The cotangent of {display_angle_val:.2f} {unit} is {(1/math.tan(angle_rad)):.4f}"
            else:
                return f"Unknown trigonometric function: {func}. Please use sine, cosine, tangent, cosecant, secant, or cotangent."
        except ValueError as e:
            self.logger.error(f"ValueError in calculation for '{query}': {e}")
            return f"Error in calculation: {e}"
        except Exception as e:
            self.logger.error(f"Unexpected calculation error for query '{query}': {e}")
            return f"An unexpected error occurred during calculation."

    @skill(
        name="Get Trigonometric Identities",
        description="Provides various trigonometric identities including basic, angle sum/difference, double angle, half angle, product-to-sum, sum-to-product, reciprocal/quotient, and cofunction identities. Example queries: 'List basic identities', 'Show angle sum formulas', 'Cofunction identities', 'List all trig identities'.",
        tags=["trigonometry", "identities", "basic", "angle sum", "double angle", "half angle", "product-to-sum", "sum-to-product", "reciprocal", "quotient", "cofunction", "formulas", "math"],
        examples=["List basic identities", "Show angle sum formulas", "What are cofunction identities", "List all trig identities", "Tell me about double angle formulas", "What is the formula for sin(a+b)?"]
    )
    def get_identities(self, query: str):
        """Return requested trigonometric identities."""
        query = query.lower().strip()
        self.logger.debug(f"Attempting to find identities for query: '{query}'")
        
        response = []
        
        if "all" in query or "every" in query:
            for group, formulas in self.IDENTITY_GROUPS.items():
                response.append(f"{group.replace('_', ' ').title()} Identities:")
                response.extend([f"- {f}" for f in formulas])
        else:
            found_group = False
            for group, keywords in self.KEYWORDS_IDENTITIES.items():
                if any(keyword in query for keyword in keywords):
                    response.append(f"{group.replace('_', ' ').title()} Identities:")
                    response.extend([f"- {f}" for f in self.IDENTITY_GROUPS[group]])
                    found_group = True
                    break
            
            if not found_group:
                return "Please specify a type of trigonometric identity (e.g., 'basic identities', 'angle sum formulas') or ask for 'all' identities."
        
        return "\n".join(response)

    def handle_task(self, task):
        text = parse_task_message(task)
        text_lower = text.lower().strip()
        self.logger.info(f"TrigonometryAgent received task: '{text}'")
        
        # First and foremost, reject code generation requests
        if any(k in text_lower for k in ["code", "python", "generate code", "write code", "function", "script", "program"]):
            self.logger.warning(f"TrigonometryAgent rejecting code generation query: '{text}'")
            task.status = TaskStatus(
                state=TaskState.INPUT_REQUIRED,
                message={"role": "agent", "content": {"text": "Please ask for Python code related to trigonometry (e.g., 'code for sine calculation' or 'generate a function for angle sum identity')."}}
            )
            return task

        is_calculation_query = False
        is_identity_query = False
        
        # Check for calculation keywords AND presence of a number/angle
        calc_keywords = list(self.FUNCTION_SYNONYMS.keys()) + ["calculate", "value of", "evaluate", "what is", "find the"]
        if any(k in text_lower for k in calc_keywords) and parse_angle(text_lower)[0] is not None:
            is_calculation_query = True
        
        # Check for identity keywords
        identity_keywords = sum(self.KEYWORDS_IDENTITIES.values(), []) + ["identities", "formulas", "list", "show", "tell me about", "what are", "define"]
        if any(k in text_lower for k in identity_keywords):
            is_identity_query = True
        
        # Prioritize based on content and intent
        if is_calculation_query and not is_identity_query:
            result = self.get_calculation(text)
            task.artifacts = [{"parts": [{"type": "text", "text": result}]}]
            task.status = TaskStatus(state=TaskState.COMPLETED)
        elif is_identity_query and not is_calculation_query:
            result = self.get_identities(text)
            task.artifacts = [{"parts": [{"type": "text", "text": result}]}]
            task.status = TaskStatus(state=TaskState.COMPLETED)
        elif is_calculation_query and is_identity_query:
            # Ambiguous: e.g., "What is the double angle formula for cos(30)?" -> likely identity + calc in one.
            # Router should ideally separate. If it reaches here, we try to guess.
            # If the query contains "formula" or "identity" very strongly, treat as identity.
            if any(k in text_lower for k in ["identity", "identities", "formula", "formulas", "list", "show", "tell me about"]):
                result = self.get_identities(text)
                task.artifacts = [{"parts": [{"type": "text", "text": result}]}]
                task.status = TaskStatus(state=TaskState.COMPLETED)
            else: # Otherwise, lean towards calculation if an angle was detected
                result = self.get_calculation(text)
                task.artifacts = [{"parts": [{"type": "text", "text": result}]}]
                task.status = TaskStatus(state=TaskState.COMPLETED)
        else:
            self.logger.warning(f"TrigonometryAgent cannot process ambiguous query: '{text}'. Falling back to input-required.")
            task.status = TaskStatus(
                state=TaskState.INPUT_REQUIRED,
                message={"role": "agent", "content": {"text": "Please ask for a trigonometric calculation (e.g., 'sine of 30 degrees') or an identity (e.g., 'list basic identities')."}}
            )
        
        return task

if __name__ == "__main__":
    agent = TrigonometryAgent()
    run_server(agent, port=8001, debug=True)