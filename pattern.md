## OpenAI Agents SDK
The OpenAI Agents SDK enables you to build agentic AI apps in a lightweight, easy-to-use package with very few abstractions. It's a production-ready upgrade of our previous experimentation for agents, Swarm. The Agents SDK has a very small set of primitives:

Agents, which are LLMs equipped with instructions and tools
Handoffs, which allow agents to delegate to other agents for specific tasks
Guardrails, which enable validation of agent inputs and outputs
Sessions, which automatically maintains conversation history across agent runs
In combination with Python, these primitives are powerful enough to express complex relationships between tools and agents, and allow you to build real-world applications without a steep learning curve. In addition, the SDK comes with built-in tracing that lets you visualize and debug your agentic flows, as well as evaluate them and even fine-tune models for your application.

Why use the Agents SDK
The SDK has two driving design principles:

Enough features to be worth using, but few enough primitives to make it quick to learn.
Works great out of the box, but you can customize exactly what happens.
Here are the main features of the SDK:

Agent loop: Built-in agent loop that handles calling tools, sending results to the LLM, and looping until the LLM is done.
Python-first: Use built-in language features to orchestrate and chain agents, rather than needing to learn new abstractions.
Handoffs: A powerful feature to coordinate and delegate between multiple agents.
Guardrails: Run input validations and checks in parallel to your agents, breaking early if the checks fail.
Sessions: Automatic conversation history management across agent runs, eliminating manual state handling.
Function tools: Turn any Python function into a tool, with automatic schema generation and Pydantic-powered validation.
Tracing: Built-in tracing that lets you visualize, debug and monitor your workflows, as well as use the OpenAI suite of evaluation, fine-tuning and distillation tools.
Installation

pip install openai-agents
Hello world example

from agents import Agent, Runner

agent = Agent(name="Assistant", instructions="You are a helpful assistant")

result = Runner.run_sync(agent, "Write a haiku about recursion in programming.")
print(result.final_output)

# Code within the code,
# Functions calling themselves,
# Infinite loop's dance.
(If running this, ensure you set the OPENAI_API_KEY environment variable)


export OPENAI_API_KEY=sk-...


## agents_as_tools.py

import asyncio

from agents import Agent, ItemHelpers, MessageOutputItem, Runner, trace

"""
This example shows the agents-as-tools pattern. The frontline agent receives a user message and
then picks which agents to call, as tools. In this case, it picks from a set of translation
agents.
"""

spanish_agent = Agent(
    name="spanish_agent",
    instructions="You translate the user's message to Spanish",
    handoff_description="An english to spanish translator",
)

french_agent = Agent(
    name="french_agent",
    instructions="You translate the user's message to French",
    handoff_description="An english to french translator",
)

italian_agent = Agent(
    name="italian_agent",
    instructions="You translate the user's message to Italian",
    handoff_description="An english to italian translator",
)

orchestrator_agent = Agent(
    name="orchestrator_agent",
    instructions=(
        "You are a translation agent. You use the tools given to you to translate."
        "If asked for multiple translations, you call the relevant tools in order."
        "You never translate on your own, you always use the provided tools."
    ),
    tools=[
        spanish_agent.as_tool(
            tool_name="translate_to_spanish",
            tool_description="Translate the user's message to Spanish",
        ),
        french_agent.as_tool(
            tool_name="translate_to_french",
            tool_description="Translate the user's message to French",
        ),
        italian_agent.as_tool(
            tool_name="translate_to_italian",
            tool_description="Translate the user's message to Italian",
        ),
    ],
)

synthesizer_agent = Agent(
    name="synthesizer_agent",
    instructions="You inspect translations, correct them if needed, and produce a final concatenated response.",
)


async def main():
    msg = input("Hi! What would you like translated, and to which languages? ")

    # Run the entire orchestration in a single trace
    with trace("Orchestrator evaluator"):
        orchestrator_result = await Runner.run(orchestrator_agent, msg)

        for item in orchestrator_result.new_items:
            if isinstance(item, MessageOutputItem):
                text = ItemHelpers.text_message_output(item)
                if text:
                    print(f"  - Translation step: {text}")

        synthesizer_result = await Runner.run(
            synthesizer_agent, orchestrator_result.to_input_list()
        )

    print(f"\n\nFinal response:\n{synthesizer_result.final_output}")


if __name__ == "__main__":
    asyncio.run(main())
	
	
## agents_as_tools_conditional.py

import asyncio

from pydantic import BaseModel

from agents import Agent, AgentBase, RunContextWrapper, Runner, trace

"""
This example demonstrates the agents-as-tools pattern with conditional tool enabling.
Agent tools are dynamically enabled/disabled based on user access levels using the
is_enabled parameter.
"""


class AppContext(BaseModel):
    language_preference: str = "spanish_only"  # "spanish_only", "french_spanish", "european"


def french_spanish_enabled(ctx: RunContextWrapper[AppContext], agent: AgentBase) -> bool:
    """Enable for French+Spanish and European preferences."""
    return ctx.context.language_preference in ["french_spanish", "european"]


def european_enabled(ctx: RunContextWrapper[AppContext], agent: AgentBase) -> bool:
    """Only enable for European preference."""
    return ctx.context.language_preference == "european"


# Create specialized agents
spanish_agent = Agent(
    name="spanish_agent",
    instructions="You respond in Spanish. Always reply to the user's question in Spanish.",
)

french_agent = Agent(
    name="french_agent",
    instructions="You respond in French. Always reply to the user's question in French.",
)

italian_agent = Agent(
    name="italian_agent",
    instructions="You respond in Italian. Always reply to the user's question in Italian.",
)

# Create orchestrator with conditional tools
orchestrator = Agent(
    name="orchestrator",
    instructions=(
        "You are a multilingual assistant. You use the tools given to you to respond to users. "
        "You must call ALL available tools to provide responses in different languages. "
        "You never respond in languages yourself, you always use the provided tools."
    ),
    tools=[
        spanish_agent.as_tool(
            tool_name="respond_spanish",
            tool_description="Respond to the user's question in Spanish",
            is_enabled=True,  # Always enabled
        ),
        french_agent.as_tool(
            tool_name="respond_french",
            tool_description="Respond to the user's question in French",
            is_enabled=french_spanish_enabled,
        ),
        italian_agent.as_tool(
            tool_name="respond_italian",
            tool_description="Respond to the user's question in Italian",
            is_enabled=european_enabled,
        ),
    ],
)


async def main():
    """Interactive demo with LLM interaction."""
    print("Agents-as-Tools with Conditional Enabling\n")
    print(
        "This demonstrates how language response tools are dynamically enabled based on user preferences.\n"
    )

    print("Choose language preference:")
    print("1. Spanish only (1 tool)")
    print("2. French and Spanish (2 tools)")
    print("3. European languages (3 tools)")

    choice = input("\nSelect option (1-3): ").strip()
    preference_map = {"1": "spanish_only", "2": "french_spanish", "3": "european"}
    language_preference = preference_map.get(choice, "spanish_only")

    # Create context and show available tools
    context = RunContextWrapper(AppContext(language_preference=language_preference))
    available_tools = await orchestrator.get_all_tools(context)
    tool_names = [tool.name for tool in available_tools]

    print(f"\nLanguage preference: {language_preference}")
    print(f"Available tools: {', '.join(tool_names)}")
    print(f"The LLM will only see and can use these {len(available_tools)} tools\n")

    # Get user request
    user_request = input("Ask a question and see responses in available languages:\n")

    # Run with LLM interaction
    print("\nProcessing request...")
    with trace("Conditional tool access"):
        result = await Runner.run(
            starting_agent=orchestrator,
            input=user_request,
            context=context.context,
        )

        print(f"\nResponse:\n{result.final_output}")


if __name__ == "__main__":
    asyncio.run(main())
	
## deterministic.py

import asyncio

from pydantic import BaseModel

from agents import Agent, Runner, trace

"""
This example demonstrates a deterministic flow, where each step is performed by an agent.
1. The first agent generates a story outline
2. We feed the outline into the second agent
3. The second agent checks if the outline is good quality and if it is a scifi story
4. If the outline is not good quality or not a scifi story, we stop here
5. If the outline is good quality and a scifi story, we feed the outline into the third agent
6. The third agent writes the story
"""

story_outline_agent = Agent(
    name="story_outline_agent",
    instructions="Generate a very short story outline based on the user's input.",
)


class OutlineCheckerOutput(BaseModel):
    good_quality: bool
    is_scifi: bool


outline_checker_agent = Agent(
    name="outline_checker_agent",
    instructions="Read the given story outline, and judge the quality. Also, determine if it is a scifi story.",
    output_type=OutlineCheckerOutput,
)

story_agent = Agent(
    name="story_agent",
    instructions="Write a short story based on the given outline.",
    output_type=str,
)


async def main():
    input_prompt = input("What kind of story do you want? ")

    # Ensure the entire workflow is a single trace
    with trace("Deterministic story flow"):
        # 1. Generate an outline
        outline_result = await Runner.run(
            story_outline_agent,
            input_prompt,
        )
        print("Outline generated")

        # 2. Check the outline
        outline_checker_result = await Runner.run(
            outline_checker_agent,
            outline_result.final_output,
        )

        # 3. Add a gate to stop if the outline is not good quality or not a scifi story
        assert isinstance(outline_checker_result.final_output, OutlineCheckerOutput)
        if not outline_checker_result.final_output.good_quality:
            print("Outline is not good quality, so we stop here.")
            exit(0)

        if not outline_checker_result.final_output.is_scifi:
            print("Outline is not a scifi story, so we stop here.")
            exit(0)

        print("Outline is good quality and a scifi story, so we continue to write the story.")

        # 4. Write the story
        story_result = await Runner.run(
            story_agent,
            outline_result.final_output,
        )
        print(f"Story: {story_result.final_output}")


if __name__ == "__main__":
    asyncio.run(main())
	
## forcing_tool_use.py
from __future__ import annotations

import asyncio
from typing import Any, Literal

from pydantic import BaseModel

from agents import (
    Agent,
    FunctionToolResult,
    ModelSettings,
    RunContextWrapper,
    Runner,
    ToolsToFinalOutputFunction,
    ToolsToFinalOutputResult,
    function_tool,
)

"""
This example shows how to force the agent to use a tool. It uses `ModelSettings(tool_choice="required")`
to force the agent to use any tool.

You can run it with 3 options:
1. `default`: The default behavior, which is to send the tool output to the LLM. In this case,
    `tool_choice` is not set, because otherwise it would result in an infinite loop - the LLM would
    call the tool, the tool would run and send the results to the LLM, and that would repeat
    (because the model is forced to use a tool every time.)
2. `first_tool_result`: The first tool result is used as the final output.
3. `custom`: A custom tool use behavior function is used. The custom function receives all the tool
    results, and chooses to use the first tool result to generate the final output.

Usage:
python forcing_tool_use.py -t default
python forcing_tool_use.py -t first_tool
python forcing_tool_use.py -t custom
"""


class Weather(BaseModel):
    city: str
    temperature_range: str
    conditions: str


@function_tool
def get_weather(city: str) -> Weather:
    print("[debug] get_weather called")
    return Weather(city=city, temperature_range="14-20C", conditions="Sunny with wind")


async def custom_tool_use_behavior(
    context: RunContextWrapper[Any], results: list[FunctionToolResult]
) -> ToolsToFinalOutputResult:
    weather: Weather = results[0].output
    return ToolsToFinalOutputResult(
        is_final_output=True, final_output=f"{weather.city} is {weather.conditions}."
    )


async def main(tool_use_behavior: Literal["default", "first_tool", "custom"] = "default"):
    if tool_use_behavior == "default":
        behavior: Literal["run_llm_again", "stop_on_first_tool"] | ToolsToFinalOutputFunction = (
            "run_llm_again"
        )
    elif tool_use_behavior == "first_tool":
        behavior = "stop_on_first_tool"
    elif tool_use_behavior == "custom":
        behavior = custom_tool_use_behavior

    agent = Agent(
        name="Weather agent",
        instructions="You are a helpful agent.",
        tools=[get_weather],
        tool_use_behavior=behavior,
        model_settings=ModelSettings(
            tool_choice="required" if tool_use_behavior != "default" else None
        ),
    )

    result = await Runner.run(agent, input="What's the weather in Tokyo?")
    print(result.final_output)


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser()
    parser.add_argument(
        "-t",
        "--tool-use-behavior",
        type=str,
        required=True,
        choices=["default", "first_tool", "custom"],
        help="The behavior to use for tool use. Default will cause tool outputs to be sent to the model. "
        "first_tool_result will cause the first tool result to be used as the final output. "
        "custom will use a custom tool use behavior function.",
    )
    args = parser.parse_args()
    asyncio.run(main(args.tool_use_behavior))
	
## input_guardrails.py

from __future__ import annotations

import asyncio

from pydantic import BaseModel

from agents import (
    Agent,
    GuardrailFunctionOutput,
    InputGuardrailTripwireTriggered,
    RunContextWrapper,
    Runner,
    TResponseInputItem,
    input_guardrail,
)

"""
This example shows how to use guardrails.

Guardrails are checks that run in parallel to the agent's execution.
They can be used to do things like:
- Check if input messages are off-topic
- Check that input messages don't violate any policies
- Take over control of the agent's execution if an unexpected input is detected

In this example, we'll setup an input guardrail that trips if the user is asking to do math homework.
If the guardrail trips, we'll respond with a refusal message.
"""


### 1. An agent-based guardrail that is triggered if the user is asking to do math homework
class MathHomeworkOutput(BaseModel):
    reasoning: str
    is_math_homework: bool


guardrail_agent = Agent(
    name="Guardrail check",
    instructions="Check if the user is asking you to do their math homework.",
    output_type=MathHomeworkOutput,
)


@input_guardrail
async def math_guardrail(
    context: RunContextWrapper[None], agent: Agent, input: str | list[TResponseInputItem]
) -> GuardrailFunctionOutput:
    """This is an input guardrail function, which happens to call an agent to check if the input
    is a math homework question.
    """
    result = await Runner.run(guardrail_agent, input, context=context.context)
    final_output = result.final_output_as(MathHomeworkOutput)

    return GuardrailFunctionOutput(
        output_info=final_output,
        tripwire_triggered=final_output.is_math_homework,
    )


### 2. The run loop


async def main():
    agent = Agent(
        name="Customer support agent",
        instructions="You are a customer support agent. You help customers with their questions.",
        input_guardrails=[math_guardrail],
    )

    input_data: list[TResponseInputItem] = []

    while True:
        user_input = input("Enter a message: ")
        input_data.append(
            {
                "role": "user",
                "content": user_input,
            }
        )

        try:
            result = await Runner.run(agent, input_data)
            print(result.final_output)
            # If the guardrail didn't trigger, we use the result as the input for the next run
            input_data = result.to_input_list()
        except InputGuardrailTripwireTriggered:
            # If the guardrail triggered, we instead add a refusal message to the input
            message = "Sorry, I can't help you with your math homework."
            print(message)
            input_data.append(
                {
                    "role": "assistant",
                    "content": message,
                }
            )

    # Sample run:
    # Enter a message: What's the capital of California?
    # The capital of California is Sacramento.
    # Enter a message: Can you help me solve for x: 2x + 5 = 11
    # Sorry, I can't help you with your math homework.


if __name__ == "__main__":
    asyncio.run(main())
	
## llm_as_a_judge.py

from __future__ import annotations

import asyncio
from dataclasses import dataclass
from typing import Literal

from agents import Agent, ItemHelpers, Runner, TResponseInputItem, trace

"""
This example shows the LLM as a judge pattern. The first agent generates an outline for a story.
The second agent judges the outline and provides feedback. We loop until the judge is satisfied
with the outline.
"""

story_outline_generator = Agent(
    name="story_outline_generator",
    instructions=(
        "You generate a very short story outline based on the user's input. "
        "If there is any feedback provided, use it to improve the outline."
    ),
)


@dataclass
class EvaluationFeedback:
    feedback: str
    score: Literal["pass", "needs_improvement", "fail"]


evaluator = Agent[None](
    name="evaluator",
    instructions=(
        "You evaluate a story outline and decide if it's good enough. "
        "If it's not good enough, you provide feedback on what needs to be improved. "
        "Never give it a pass on the first try. After 5 attempts, you can give it a pass if the story outline is good enough - do not go for perfection"
    ),
    output_type=EvaluationFeedback,
)


async def main() -> None:
    msg = input("What kind of story would you like to hear? ")
    input_items: list[TResponseInputItem] = [{"content": msg, "role": "user"}]

    latest_outline: str | None = None

    # We'll run the entire workflow in a single trace
    with trace("LLM as a judge"):
        while True:
            story_outline_result = await Runner.run(
                story_outline_generator,
                input_items,
            )

            input_items = story_outline_result.to_input_list()
            latest_outline = ItemHelpers.text_message_outputs(story_outline_result.new_items)
            print("Story outline generated")

            evaluator_result = await Runner.run(evaluator, input_items)
            result: EvaluationFeedback = evaluator_result.final_output

            print(f"Evaluator score: {result.score}")

            if result.score == "pass":
                print("Story outline is good enough, exiting.")
                break

            print("Re-running with feedback")

            input_items.append({"content": f"Feedback: {result.feedback}", "role": "user"})

    print(f"Final story outline: {latest_outline}")


if __name__ == "__main__":
    asyncio.run(main())
	
## output_guardrails.py
from __future__ import annotations

import asyncio
import json

from pydantic import BaseModel, Field

from agents import (
    Agent,
    GuardrailFunctionOutput,
    OutputGuardrailTripwireTriggered,
    RunContextWrapper,
    Runner,
    output_guardrail,
)

"""
This example shows how to use output guardrails.

Output guardrails are checks that run on the final output of an agent.
They can be used to do things like:
- Check if the output contains sensitive data
- Check if the output is a valid response to the user's message

In this example, we'll use a (contrived) example where we check if the agent's response contains
a phone number.
"""


# The agent's output type
class MessageOutput(BaseModel):
    reasoning: str = Field(description="Thoughts on how to respond to the user's message")
    response: str = Field(description="The response to the user's message")
    user_name: str | None = Field(description="The name of the user who sent the message, if known")


@output_guardrail
async def sensitive_data_check(
    context: RunContextWrapper, agent: Agent, output: MessageOutput
) -> GuardrailFunctionOutput:
    phone_number_in_response = "650" in output.response
    phone_number_in_reasoning = "650" in output.reasoning

    return GuardrailFunctionOutput(
        output_info={
            "phone_number_in_response": phone_number_in_response,
            "phone_number_in_reasoning": phone_number_in_reasoning,
        },
        tripwire_triggered=phone_number_in_response or phone_number_in_reasoning,
    )


agent = Agent(
    name="Assistant",
    instructions="You are a helpful assistant.",
    output_type=MessageOutput,
    output_guardrails=[sensitive_data_check],
)


async def main():
    # This should be ok
    await Runner.run(agent, "What's the capital of California?")
    print("First message passed")

    # This should trip the guardrail
    try:
        result = await Runner.run(
            agent, "My phone number is 650-123-4567. Where do you think I live?"
        )
        print(
            f"Guardrail didn't trip - this is unexpected. Output: {json.dumps(result.final_output.model_dump(), indent=2)}"
        )

    except OutputGuardrailTripwireTriggered as e:
        print(f"Guardrail tripped. Info: {e.guardrail_result.output.output_info}")


if __name__ == "__main__":
    asyncio.run(main())
	
## parallelization.py
import asyncio

from agents import Agent, ItemHelpers, Runner, trace

"""
This example shows the parallelization pattern. We run the agent three times in parallel, and pick
the best result.
"""

spanish_agent = Agent(
    name="spanish_agent",
    instructions="You translate the user's message to Spanish",
)

translation_picker = Agent(
    name="translation_picker",
    instructions="You pick the best Spanish translation from the given options.",
)


async def main():
    msg = input("Hi! Enter a message, and we'll translate it to Spanish.\n\n")

    # Ensure the entire workflow is a single trace
    with trace("Parallel translation"):
        res_1, res_2, res_3 = await asyncio.gather(
            Runner.run(
                spanish_agent,
                msg,
            ),
            Runner.run(
                spanish_agent,
                msg,
            ),
            Runner.run(
                spanish_agent,
                msg,
            ),
        )

        outputs = [
            ItemHelpers.text_message_outputs(res_1.new_items),
            ItemHelpers.text_message_outputs(res_2.new_items),
            ItemHelpers.text_message_outputs(res_3.new_items),
        ]

        translations = "\n\n".join(outputs)
        print(f"\n\nTranslations:\n\n{translations}")

        best_translation = await Runner.run(
            translation_picker,
            f"Input: {msg}\n\nTranslations:\n{translations}",
        )

    print("\n\n-----")

    print(f"Best translation: {best_translation.final_output}")


if __name__ == "__main__":
    asyncio.run(main())
	
## routing.py
import asyncio
import uuid

from openai.types.responses import ResponseContentPartDoneEvent, ResponseTextDeltaEvent

from agents import Agent, RawResponsesStreamEvent, Runner, TResponseInputItem, trace

"""
This example shows the handoffs/routing pattern. The triage agent receives the first message, and
then hands off to the appropriate agent based on the language of the request. Responses are
streamed to the user.
"""

french_agent = Agent(
    name="french_agent",
    instructions="You only speak French",
)

spanish_agent = Agent(
    name="spanish_agent",
    instructions="You only speak Spanish",
)

english_agent = Agent(
    name="english_agent",
    instructions="You only speak English",
)

triage_agent = Agent(
    name="triage_agent",
    instructions="Handoff to the appropriate agent based on the language of the request.",
    handoffs=[french_agent, spanish_agent, english_agent],
)


async def main():
    # We'll create an ID for this conversation, so we can link each trace
    conversation_id = str(uuid.uuid4().hex[:16])

    msg = input("Hi! We speak French, Spanish and English. How can I help? ")
    agent = triage_agent
    inputs: list[TResponseInputItem] = [{"content": msg, "role": "user"}]

    while True:
        # Each conversation turn is a single trace. Normally, each input from the user would be an
        # API request to your app, and you can wrap the request in a trace()
        with trace("Routing example", group_id=conversation_id):
            result = Runner.run_streamed(
                agent,
                input=inputs,
            )
            async for event in result.stream_events():
                if not isinstance(event, RawResponsesStreamEvent):
                    continue
                data = event.data
                if isinstance(data, ResponseTextDeltaEvent):
                    print(data.delta, end="", flush=True)
                elif isinstance(data, ResponseContentPartDoneEvent):
                    print("\n")

        inputs = result.to_input_list()
        print("\n")

        user_msg = input("Enter a message: ")
        inputs.append({"content": user_msg, "role": "user"})
        agent = result.current_agent


if __name__ == "__main__":
    asyncio.run(main())
	
## streaming_guardrails.py

from __future__ import annotations

import asyncio

from openai.types.responses import ResponseTextDeltaEvent
from pydantic import BaseModel, Field

from agents import Agent, Runner

"""
This example shows how to use guardrails as the model is streaming. Output guardrails run after the
final output has been generated; this example runs guardails every N tokens, allowing for early
termination if bad output is detected.

The expected output is that you'll see a bunch of tokens stream in, then the guardrail will trigger
and stop the streaming.
"""


agent = Agent(
    name="Assistant",
    instructions=(
        "You are a helpful assistant. You ALWAYS write long responses, making sure to be verbose "
        "and detailed."
    ),
)


class GuardrailOutput(BaseModel):
    reasoning: str = Field(
        description="Reasoning about whether the response could be understood by a ten year old."
    )
    is_readable_by_ten_year_old: bool = Field(
        description="Whether the response is understandable by a ten year old."
    )


guardrail_agent = Agent(
    name="Checker",
    instructions=(
        "You will be given a question and a response. Your goal is to judge whether the response "
        "is simple enough to be understood by a ten year old."
    ),
    output_type=GuardrailOutput,
    model="gpt-4o-mini",
)


async def check_guardrail(text: str) -> GuardrailOutput:
    result = await Runner.run(guardrail_agent, text)
    return result.final_output_as(GuardrailOutput)


async def main():
    question = "What is a black hole, and how does it behave?"
    result = Runner.run_streamed(agent, question)
    current_text = ""

    # We will check the guardrail every N characters
    next_guardrail_check_len = 300
    guardrail_task = None

    async for event in result.stream_events():
        if event.type == "raw_response_event" and isinstance(event.data, ResponseTextDeltaEvent):
            print(event.data.delta, end="", flush=True)
            current_text += event.data.delta

            # Check if it's time to run the guardrail check
            # Note that we don't run the guardrail check if there's already a task running. An
            # alternate implementation is to have N guardrails running, or cancel the previous
            # one.
            if len(current_text) >= next_guardrail_check_len and not guardrail_task:
                print("Running guardrail check")
                guardrail_task = asyncio.create_task(check_guardrail(current_text))
                next_guardrail_check_len += 300

        # Every iteration of the loop, check if the guardrail has been triggered
        if guardrail_task and guardrail_task.done():
            guardrail_result = guardrail_task.result()
            if not guardrail_result.is_readable_by_ten_year_old:
                print("\n\n================\n\n")
                print(f"Guardrail triggered. Reasoning:\n{guardrail_result.reasoning}")
                break

    # Do one final check on the final output
    guardrail_result = await check_guardrail(current_text)
    if not guardrail_result.is_readable_by_ten_year_old:
        print("\n\n================\n\n")
        print(f"Guardrail triggered. Reasoning:\n{guardrail_result.reasoning}")


if __name__ == "__main__":
    asyncio.run(main())
	
