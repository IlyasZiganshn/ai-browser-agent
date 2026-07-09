TOOLS = [
    {
        "type": "function",
        "function": {
            "name": "navigate",
            "description": "Перейти по URL",
            "parameters": {
                "type": "object",
                "properties": {
                    "url": {"type": "string"}
                },
                "required": ["url"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "click",
            "description": "Клик по элементу по тексту",
            "parameters": {
                "type": "object",
                "properties": {
                    "text": {"type": "string"}
                },
                "required": ["text"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "scroll",
            "description": "Прокрутка страницы вниз",
            "parameters": {
                "type": "object",
                "properties": {
                    "pixels": {
                        "type": "integer",
                        "default": 800
                    }
                }
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "type_text",
            "description": "Ввести текст в поле ввода и нажать Enter",
            "parameters": {
                "type": "object",
                "properties": {
                    "text": {"type": "string"}
                },
                "required": ["text"]
            }
        }
    }
]
