TOOLS_WITH_XY = [
    "add",
    "subtract",
    "multiply",
    "divide",
    "mod",
    "get_x_percentage_of_y",
]

TOOLS_WITHOUT_ARGS = [
    "pi",
]

AGENT_SCHEMA = {
    "type": "object",
    "properties": {
        "thought": {"type": "string"},
        "action": {
            "type": "string",
            "enum": ["tool_call", "final"]
        },
        "tool_name": {
            "type": ["string", "null"],
            "enum": TOOLS_WITH_XY + TOOLS_WITHOUT_ARGS + [None]
        },
        "arguments": {
            "type": "object",
            "properties": {
                "x": {"type": "number"},
                "y": {"type": "number"}
            },
            "additionalProperties": False
        },
        "message": {
            "type": "string"
        }
    },
    "required": ["thought", "action", "tool_name", "arguments", "message"],
    "additionalProperties": False
}

TOOL_SPECS = {
    "add": {
        "type": "object",
        "properties": {
            "x": {"type": "number"},
            "y": {"type": "number"}
        },
        "required": ["x", "y"],
        "additionalProperties": False
    },
    "subtract": {
        "type": "object",
        "properties": {
            "x": {"type": "number"},
            "y": {"type": "number"}
        },
        "required": ["x", "y"],
        "additionalProperties": False
    },
    "multiply": {
        "type": "object",
        "properties": {
            "x": {"type": "number"},
            "y": {"type": "number"}
        },
        "required": ["x", "y"],
        "additionalProperties": False
    },
    "divide": {
        "type": "object",
        "properties": {
            "x": {"type": "number"},
            "y": {"type": "number"}
        },
        "required": ["x", "y"],
        "additionalProperties": False
    },
    "mod": {
        "type": "object",
        "properties": {
            "x": {"type": "number"},
            "y": {"type": "number"}
        },
        "required": ["x", "y"],
        "additionalProperties": False
    },
    "get_x_percentage_of_y": {
        "type": "object",
        "properties": {
            "x": {"type": "number"},
            "y": {"type": "number"}
        },
        "required": ["x", "y"],
        "additionalProperties": False
    },
    "pi": {
        "type": "object",
        "properties": {},
        "required": [],
        "additionalProperties": False
    }
}