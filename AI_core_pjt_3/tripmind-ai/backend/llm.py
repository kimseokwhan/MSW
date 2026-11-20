from backend.config import chat_tool_options


def call_function(client, model, messages, function, *, required=False):
    name = function["name"]
    if model == "gpt-6-astra":
        response = client.responses.create(
            model=model, input=messages,
            tools=[{"type": "function", **function, "strict": False}],
            tool_choice={"type": "function", "name": name} if required else "auto",
            reasoning={"effort": "low"},
            store=False,
        )
        return next((item.arguments for item in response.output
                     if item.type == "function_call" and item.name == name), None)
    response = client.chat.completions.create(
        model=model, messages=messages, tools=[{"type": "function", "function": function}],
        tool_choice={"type": "function", "function": {"name": name}} if required else "auto",
        **chat_tool_options(model),
    )
    if not response.choices:
        return None
    calls = response.choices[0].message.tool_calls or []
    return next((call.function.arguments for call in calls
                 if call.type == "function" and call.function.name == name), None)
