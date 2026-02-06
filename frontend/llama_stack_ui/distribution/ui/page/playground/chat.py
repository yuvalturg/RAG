# Copyright (c) Meta Platforms, Inc. and affiliates.
# All rights reserved.
#
# This source code is licensed under the terms described in the LICENSE file in
# the root directory of this source tree.

import enum
import json
import sys
import uuid

import streamlit as st
from llama_stack_client.lib.agents.agent import Agent
from llama_stack_client.lib.agents.react.agent import ReActAgent
from llama_stack_client.types import UserMessage

from llama_stack_ui.distribution.ui.modules.api import llama_stack_api
from llama_stack_ui.distribution.ui.modules.utils import (
    get_suggestions_for_databases,
    get_vector_db_name,
)


class AgentType(enum.Enum):
    REGULAR = "Regular"
    REACT = "ReAct"

def get_strategy(temperature, top_p):
    """Determines the sampling strategy for the LLM based on temperature."""
    return {'type': 'greedy'} if temperature == 0 else {
            'type': 'top_p', 'temperature': temperature, 'top_p': top_p
        }


def render_history(tool_debug):
    """Renders the chat history from the session state.
    Also displays debug events for assistant messages if tool_debug is enabled.
    """
    # Initialize messages in the session state if not present
    if 'messages' not in st.session_state:
        st.session_state.messages = [{"role": "assistant", "content": "How can I help you?"}]
    # Initialize debug_events in the session state if not present
    if 'debug_events' not in st.session_state:
        st.session_state.debug_events = []

    for i, msg in enumerate(st.session_state.messages):
        with st.chat_message(msg['role']):
            st.markdown(msg['content'])

            # Display debug events expander for assistant messages (excluding the initial greeting)
            if msg['role'] == 'assistant' and tool_debug and i > 0:
                # Debug events are stored per assistant turn.
                # The index for debug_events corresponds to the assistant message turn.
                # messages: [A_initial, U_1, A_1, U_2, A_2, ...]
                # debug_events: [events_for_A_1, events_for_A_2, ...]
                # For A_1 (msg index 2), the debug_events index is (2//2)-1 = 0.
                debug_event_list_index = (i // 2) - 1
                if 0 <= debug_event_list_index < len(st.session_state.debug_events):
                    current_turn_events_list = (
                        st.session_state.debug_events[debug_event_list_index]
                    )

                    # Only show expander if there are events
                    if current_turn_events_list:
                        with st.expander("Tool/Debug Events", expanded=False):
                            if (isinstance(current_turn_events_list, list)
                                    and len(current_turn_events_list) > 0):
                                for event_idx, event_item in enumerate(current_turn_events_list):
                                    with st.container():
                                        if isinstance(event_item, dict):
                                            st.json(event_item, expanded=False)
                                        elif isinstance(event_item, str):
                                            st.text_area(
                                                label=f"Debug Event {event_idx + 1}",
                                                value=event_item,
                                                height=100,
                                                disabled=True,
                                                # Unique key for each text area
                                                key=f"debug_event_msg{i}_item{event_idx}",
                                            )
                                        else:
                                            # Fallback for other data types
                                            st.write(event_item)
                                        if event_idx < len(current_turn_events_list) - 1:
                                            st.divider()
                            elif (isinstance(current_turn_events_list, list)
                                    and not current_turn_events_list):
                                st.caption("No debug events recorded for this turn.")
                            else: # Should not happen with current logic
                                st.write("Debug data for this turn (unexpected format):")
                                st.write(current_turn_events_list)

def tool_chat_page():
    st.title("💬 Chat")

    client = llama_stack_api.client
    models = client.models.list()
    model_list = [model.identifier for model in models if model.api_model_type == "llm"]

    tool_groups = client.toolgroups.list()
    tool_groups_list = [tool_group.identifier for tool_group in tool_groups]
    mcp_tools_list = [tool for tool in tool_groups_list if tool.startswith("mcp::")]
    builtin_tools_list = [tool for tool in tool_groups_list if not tool.startswith("mcp::")]

    selected_vector_dbs = []

    def reset_agent():
        st.session_state.clear()
        st.cache_resource.clear()

    with st.sidebar:
        st.title("Configuration")
        st.subheader("Model")
        model = st.selectbox(
            label="Model",
            options=model_list,
            on_change=reset_agent,
            label_visibility="collapsed",
        )

        ## Added mode
        processing_mode = st.radio(
            "Processing mode",
            ["Direct", "Agent-based"],
            index=0, # Default to Direct
            captions=[
                "Directly calls the model with optional RAG.",
                "Uses an Agent with tools.",
            ],
            on_change=reset_agent,
            help=(
                "Choose how requests are processed. 'Direct' bypasses "
                "agents, 'Agent-based' uses them."
            ),
        )


        toolgroup_selection = []
        if processing_mode == "Direct":
            vector_dbs = llama_stack_api.client.vector_stores.list() or []
            if not vector_dbs:
                st.info("No vector databases available for selection.")
            vector_db_names = [get_vector_db_name(vector_db) for vector_db in vector_dbs]
            selected_vector_dbs = st.multiselect(
                label="Select Document Collections to use in RAG queries",
                options=vector_db_names,
                on_change=reset_agent,
            )
        if processing_mode == "Agent-based":
            st.subheader("Available ToolGroups")

            toolgroup_selection = st.pills(
                label="Built-in tools",
                options=builtin_tools_list,
                selection_mode="multi",
                on_change=reset_agent,
                format_func=lambda tool: "".join(tool.split("::")[1:]),
                help="List of built-in tools from your llama stack server.",
            )

            if "builtin::rag" in toolgroup_selection:
                vector_dbs = llama_stack_api.client.vector_stores.list() or []
                if not vector_dbs:
                    st.info("No vector databases available for selection.")
                vector_db_names = [get_vector_db_name(vector_db) for vector_db in vector_dbs]
                selected_vector_dbs = st.multiselect(
                    label="Select Document Collections to use in RAG queries",
                    options=vector_db_names,
                    on_change=reset_agent,
                )

            # Display mcp list only if there are mcp tools
            if len(mcp_tools_list) > 0:
                mcp_selection = st.pills(
                    label="MCP Servers",
                    options=mcp_tools_list,
                    selection_mode="multi",
                    on_change=reset_agent,
                    format_func=lambda tool: "".join(tool.split("::")[1:]),
                    help="List of MCP servers registered to your llama stack server.",
                )

                toolgroup_selection.extend(mcp_selection)

            grouped_tools = {}
            total_tools = 0

            for toolgroup_id in toolgroup_selection:
                tools = client.tools.list(toolgroup_id=toolgroup_id)
                grouped_tools[toolgroup_id] = [tool.name for tool in tools]
                total_tools += len(tools)

            st.markdown(f"Active Tools: 🛠 {total_tools}")

            for group_id, tools in grouped_tools.items():
                with st.expander(f"🔧 Tools from `{group_id}`"):
                    for idx, tool in enumerate(tools, start=1):
                        st.markdown(f"{idx}. `{tool.split(':')[-1]}`")

            agent_type = AgentType.REGULAR

        st.subheader("Sampling Parameters")

        # Temperature - supported in both modes
        temperature = st.slider(
            "Temperature",
            0.0, 2.0, 0.1, 0.05,
            on_change=reset_agent,
            help="Controls randomness. Higher values = more random.",
        )

        # Max inference iterations - supported in both modes
        max_infer_iters = st.slider(
            "Max Inference Iterations",
            1, 50, 10, 1,
            on_change=reset_agent,
            help="Maximum number of inference iterations before stopping",
        )

        st.subheader("System Prompt")
        default_prompt = "You are a helpful AI assistant."
        if processing_mode == "Agent-based" and agent_type == AgentType.REACT:
            default_prompt = (
                "You are a helpful ReAct agent. Reason step-by-step to "
                "fulfill the user query using available tools."
            )
        system_prompt = st.text_area(
            "System Prompt", value=default_prompt, on_change=reset_agent, height=100
        )

        st.subheader("Response Handling")
        tool_debug = st.toggle("Show Tool/Debug Info", value=False)

        if st.button("Clear Chat & Reset Config", use_container_width=True):
            reset_agent()
            st.rerun()


    updated_toolgroup_selection = []
    if processing_mode == "Agent-based":
        for _, tool_name in enumerate(toolgroup_selection):
            if tool_name == "builtin::rag":
                if len(selected_vector_dbs) > 0:
                    vector_dbs = llama_stack_api.client.vector_stores.list() or []
                    vector_db_ids = [
                        vector_db.id for vector_db in vector_dbs
                        if get_vector_db_name(vector_db) in selected_vector_dbs
                    ]
                    # Use the new file_search tool format
                    tool_dict = {
                        "type": "file_search",
                        "vector_store_ids": list(vector_db_ids),
                    }
                    updated_toolgroup_selection.append(tool_dict)
            else:
                updated_toolgroup_selection.append(tool_name)

    @st.cache_resource
    def create_agent():
        # Version 0.3.3 of llama-stack-client has a simplified Agent API
        # It doesn't support sampling_params, shields, etc. directly
        # Those are configured on the server side

        if "agent_type" in st.session_state and st.session_state.agent_type == AgentType.REACT:
            return ReActAgent(
                client=client,
                model=model,
                tools=updated_toolgroup_selection,
                json_response_format=True,
            )
        else:
            updated_system_prompt = system_prompt.strip()
            if not updated_system_prompt.strip().endswith('.'):
                updated_system_prompt = updated_system_prompt + '.'
            return Agent(
                client=client,
                model=model,
                instructions=(
                    f"{updated_system_prompt} When you use a tool always "
                    "respond with a summary of the result."
                ),
                tools=updated_toolgroup_selection,
            )

    if processing_mode == "Agent-based":
        st.session_state.agent_type = agent_type
        agent = create_agent()

        if "agent_session_id" not in st.session_state:
            session_name = f"tool_demo_{uuid.uuid4()}"
            st.session_state["agent_session_id"] = agent.create_session(
                session_name=session_name
            )

        session_id = st.session_state["agent_session_id"]

    if "messages" not in st.session_state:
        st.session_state["messages"] = [
            {
                "role": "assistant",
                "content": "How can I help you?",
                "stop_reason": "end_of_turn",
            }
        ]

    if "debug_events" not in st.session_state: # Per-turn debug logs
        st.session_state["debug_events"] = []

    if "show_more_questions" not in st.session_state:
        st.session_state["show_more_questions"] = False

    if "selected_question" not in st.session_state:
        st.session_state["selected_question"] = None

    render_history(tool_debug) # Display the current chat history and any past debug events

    # Display suggested questions if databases are selected
    def display_suggested_questions():
        """Display suggested questions based on selected databases."""
        if not selected_vector_dbs:
            return

        vector_dbs = llama_stack_api.client.vector_stores.list() or []
        suggestions = get_suggestions_for_databases(selected_vector_dbs, vector_dbs)

        if not suggestions:
            return

        st.markdown("### 💡 Suggested Questions")

        # Determine how many questions to show
        if st.session_state.show_more_questions:
            num_to_show = len(suggestions)
        else:
            num_to_show = min(4, len(suggestions))

        # Display questions in a grid-like format using columns
        cols_per_row = 2
        for i in range(0, num_to_show, cols_per_row):
            cols = st.columns(cols_per_row)
            for j in range(cols_per_row):
                idx = i + j
                if idx < num_to_show:
                    question, db_name = suggestions[idx]
                    with cols[j]:
                        # Create a button for each question
                        button_key = f"question_btn_{idx}_{hash(question)}"
                        if st.button(
                            question,
                            key=button_key,
                            use_container_width=True,
                            help=f"From: {db_name}"
                        ):
                            st.session_state.selected_question = question
                            st.rerun()

        # Show "Show More" or "Show Less" button if there are more than 4 questions
        if len(suggestions) > 4:
            _, col2, _ = st.columns([1, 1, 1])
            with col2:
                if st.session_state.show_more_questions:
                    if st.button("Show Less", use_container_width=True):
                        st.session_state.show_more_questions = False
                        st.rerun()
                else:
                    button_text = f"Show More ({len(suggestions) - 4} more)"
                    if st.button(button_text, use_container_width=True):
                        st.session_state.show_more_questions = True
                        st.rerun()

        st.markdown("---")

    display_suggested_questions()

    def response_generator(turn_response, debug_events_list):
        if st.session_state.get("agent_type") == AgentType.REACT:
            return _handle_react_response(turn_response)
        else:
            return _handle_regular_response(turn_response, debug_events_list)

    def _handle_react_response(turn_response):
        current_step_content = ""
        final_answer = None
        tool_results = []

        for response in turn_response:
            if not hasattr(response.event, "payload"):
                yield (
                    "\n\n🚨 :red[_Llama Stack server Error:_]\n"
                    "The response received is missing an expected `payload` attribute.\n"
                    "This could indicate a malformed response or an internal issue "
                    "within the server.\n\n"
                    f"Error details: {response}"
                )
                return

            payload = response.event.payload

            if payload.event_type == "step_progress" and hasattr(payload.delta, "text"):
                current_step_content += payload.delta.text
                continue

            if payload.event_type == "step_complete":
                step_details = payload.step_details

                if step_details.step_type == "inference":
                    yield from _process_inference_step(
                        current_step_content, tool_results, final_answer
                    )
                    current_step_content = ""
                elif step_details.step_type == "tool_execution":
                    tool_results = _process_tool_execution(step_details, tool_results)
                    current_step_content = ""
                else:
                    current_step_content = ""

        if not final_answer and tool_results:
            yield from _format_tool_results_summary(tool_results)

    def _process_inference_step(current_step_content, tool_results, final_answer):
        try:
            react_output_data = json.loads(current_step_content)
            thought = react_output_data.get("thought")
            action = react_output_data.get("action")
            answer = react_output_data.get("answer")

            if answer and answer != "null" and answer is not None:
                final_answer = answer

            if thought:
                with st.expander("🤔 Thinking...", expanded=False):
                    st.markdown(f":grey[__{thought}__]")

            if action and isinstance(action, dict):
                tool_name = action.get("tool_name")
                tool_params = action.get("tool_params")
                with st.expander(f'🛠 Action: Using tool "{tool_name}"', expanded=False):
                    st.json(tool_params)

            if answer and answer != "null" and answer is not None:
                yield f"\n\n✅ **Final Answer:**\n{answer}"

        except json.JSONDecodeError:
            yield f"\n\nFailed to parse ReAct step content:\n```json\n{current_step_content}\n```"
        except Exception as e:
            yield f"\n\nFailed to process ReAct step: {e}\n```json\n{current_step_content}\n```"

        return final_answer

    def _process_tool_execution(step_details, tool_results):
        try:
            if hasattr(step_details, "tool_responses") and step_details.tool_responses:
                for tool_response in step_details.tool_responses:
                    tool_name = tool_response.tool_name
                    content = tool_response.content
                    tool_results.append((tool_name, content))
                    with st.expander(f'⚙️ Observation (Result from "{tool_name}")', expanded=False):
                        try:
                            parsed_content = json.loads(content)
                            st.json(parsed_content)
                        except json.JSONDecodeError:
                            st.code(content, language=None)
            else:
                with st.expander("⚙️ Observation", expanded=False):
                    st.markdown(
                        ":grey[_Tool execution step completed, "
                        "but no response data found._]"
                    )
        except Exception as e:
            with st.expander("⚙️ Error in Tool Execution", expanded=False):
                st.markdown(f":red[_Error processing tool execution: {str(e)}_]")

        return tool_results

    def _format_tool_results_summary(tool_results):
        yield "\n\n**Here's what I found:**\n"
        for tool_name, content in tool_results:
            try:
                parsed_content = json.loads(content)

                if tool_name == "web_search" and "top_k" in parsed_content:
                    yield from _format_web_search_results(parsed_content)
                elif "results" in parsed_content and isinstance(parsed_content["results"], list):
                    yield from _format_results_list(parsed_content["results"])
                elif isinstance(parsed_content, dict) and len(parsed_content) > 0:
                    yield from _format_dict_results(parsed_content)
                elif isinstance(parsed_content, list) and len(parsed_content) > 0:
                    yield from _format_list_results(parsed_content)
            except json.JSONDecodeError:
                yield (
                    f"\n**{tool_name}** was used but returned complex data. "
                    "Check the observation for details.\n"
                )
            except (TypeError, AttributeError, KeyError, IndexError) as e:
                print(f"Error processing {tool_name} result: {type(e).__name__}: {e}")

    def _format_web_search_results(parsed_content):
        for i, result in enumerate(parsed_content["top_k"], 1):
            if i <= 3:
                title = result.get("title", "Untitled")
                url = result.get("url", "")
                content_text = result.get("content", "").strip()
                yield f"\n- **{title}**\n  {content_text}\n  [Source]({url})\n"

    def _format_results_list(results):
        for i, result in enumerate(results, 1):
            if i <= 3:
                if isinstance(result, dict):
                    name = result.get("name", result.get("title", "Result " + str(i)))
                    description = result.get(
                        "description",
                        result.get("content", result.get("summary", ""))
                    )
                    yield f"\n- **{name}**\n  {description}\n"
                else:
                    yield f"\n- {result}\n"

    def _format_dict_results(parsed_content):
        yield "\n```\n"
        for key, value in list(parsed_content.items())[:5]:
            if isinstance(value, str) and len(value) < 100:
                yield f"{key}: {value}\n"
            else:
                yield f"{key}: [Complex data]\n"
        yield "```\n"

    def _format_list_results(parsed_content):
        yield "\n"
        for _, item in enumerate(parsed_content[:3], 1):
            if isinstance(item, str):
                yield f"- {item}\n"
            elif isinstance(item, dict) and "text" in item:
                yield f"- {item['text']}\n"
            elif isinstance(item, dict) and len(item) > 0:
                first_value = next(iter(item.values()))
                if isinstance(first_value, str) and len(first_value) < 100:
                    yield f"- {first_value}\n"

    def _handle_regular_response(turn_response, debug_events_list):
        for chunk in turn_response:
            if hasattr(chunk, 'event') and chunk.event:
                event = chunk.event
                event_type = getattr(event, 'event_type', None)

                if event_type == 'step_progress':
                    # Handle text deltas from StepProgress events
                    if hasattr(event, 'delta') and hasattr(event.delta, 'text'):
                        yield event.delta.text

                elif event_type == 'step_completed':
                    # Handle completed steps
                    if hasattr(event, 'result'):
                        result = event.result
                        # Check for tool executions
                        if hasattr(result, 'function_calls') and result.function_calls:
                            for func_call in result.function_calls:
                                tool_name = getattr(func_call, 'tool_name', 'unknown')
                                yield f'\n\n🛠 :grey[_Using "{tool_name}" tool:_]\n\n'

                elif event_type == 'turn_completed':
                    # Log completion for debugging
                    debug_events_list.append({
                        "type": "turn_completed",
                        "turn_id": getattr(event, 'turn_id', 'unknown'),
                        "num_steps": getattr(event, 'num_steps', 0)
                    })

    def agent_process_prompt(prompt, debug_events_list):
        # Send the prompt to the agent
        turn_response = agent.create_turn(
            session_id=session_id,
            messages=[UserMessage(role="user", content=prompt)],
            stream=True,
        )
        response_content = st.write_stream(response_generator(turn_response, debug_events_list))
        st.session_state.messages.append({"role": "assistant", "content": response_content})


    def direct_process_prompt(prompt, debug_events_list):
        # Build tools list if vector stores are selected
        tools = None
        rag_info = ""

        if selected_vector_dbs:
            vector_dbs = llama_stack_api.client.vector_stores.list() or []
            vector_db_ids = [
                vector_db.id for vector_db in vector_dbs
                if get_vector_db_name(vector_db) in selected_vector_dbs
            ]

            if vector_db_ids:
                tools = [{
                    "type": "file_search",
                    "vector_store_ids": list(vector_db_ids)
                }]
                rag_info = (
                    f"\n\n🔍 *Searching {len(vector_db_ids)} document collection(s): "
                    f"{', '.join(selected_vector_dbs)}*\n\n"
                )

        with st.chat_message("assistant"):
            message_placeholder = st.empty()
            full_response = rag_info

            # Use responses API for Direct mode
            request_kwargs = {
                "model": model,
                "instructions": system_prompt,
                "input": prompt,
                "temperature": temperature,
                "max_infer_iters": max_infer_iters,
                "stream": True,
            }

            # Add tools if RAG is enabled
            if tools:
                request_kwargs["tools"] = tools

            print(f"[DEBUG] Request: {request_kwargs}", flush=True)
            response = llama_stack_api.client.responses.create(**request_kwargs)

            # Display assistant response
            tool_used = False
            for chunk in response:
                if hasattr(chunk, 'type'):
                    if chunk.type == "response.file_search_call.in_progress":
                        if not tool_used:
                            full_response += "\n\n🔧 *Using file_search tool...*\n\n"
                            message_placeholder.markdown(full_response + "▌")
                            tool_used = True
                    elif chunk.type == "response.output_text.delta":
                        if hasattr(chunk, 'delta') and chunk.delta:
                            full_response += chunk.delta
                            message_placeholder.markdown(full_response + "▌")
                    elif chunk.type == "response.done":
                        if hasattr(chunk, 'response') and hasattr(chunk.response, 'output_text'):
                            if chunk.response.output_text:
                                full_response = rag_info + chunk.response.output_text

            message_placeholder.markdown(full_response)
            print(f"[DEBUG] Final response: {full_response}", flush=True)

        response_dict = {
            "role": "assistant",
            "content": full_response,
            "stop_reason": "end_of_message"
        }
        st.session_state.messages.append(response_dict)

    def process_prompt(prompt):
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)

        # Prepare for assistant's response
        # Each assistant turn gets its own list for debug events
        st.session_state.debug_events.append([])
        current_turn_debug_events_list = st.session_state.debug_events[-1]

        if processing_mode == "Agent-based":
            agent_process_prompt(prompt, current_turn_debug_events_list)
        else:
            direct_process_prompt(prompt, current_turn_debug_events_list)
        st.rerun()

    # Handle selected question from suggestions
    if st.session_state.selected_question:
        prompt = st.session_state.selected_question
        st.session_state.selected_question = None  # Clear the selected question

        process_prompt(prompt)


    # Handle manual chat input
    if prompt := st.chat_input(placeholder="Ask a question..."):
        # Append the user message to history and display it
        process_prompt(prompt)


tool_chat_page()
