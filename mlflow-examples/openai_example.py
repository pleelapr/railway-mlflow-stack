import json
from os import getenv
from typing import Dict, List, Union

import mlflow
from mlflow.entities import SpanType

try:
	import openai
except ImportError:
	print("OpenAI package not found. Install with: uv add openai")
	exit(1)


@mlflow.trace(span_type=SpanType.TOOL)
def get_weather(city: str) -> str:
	"""Mock weather API function.

	Args:
		city: Name of the city to get weather for

	Returns:
		Weather description for the city
	"""
	weather_data = {
		"Tokyo": "sunny",
		"Paris": "rainy",
		"New York": "cloudy",
		"London": "foggy",
		"San Francisco": "windy",
	}
	return weather_data.get(city, "unknown")


@mlflow.trace(span_type=SpanType.AGENT)
def run_openai_chat_example() -> str:
	"""Run a simple OpenAI chat completion example.

	Returns:
		Response content from the OpenAI API
	"""
	client = openai.OpenAI()

	messages: List[Dict[str, str]] = [
		{
			"role": "system",
			"content": "You are a helpful assistant that provides concise answers.",
		},
		{
			"role": "user",
			"content": "What is MLflow and why is it useful for machine learning?",
		},
	]

	try:
		response = client.chat.completions.create(
			model="gpt-4o-mini", 
			messages=messages,  # type: ignore
			max_tokens=150, 
			temperature=0.7
		)

		return response.choices[0].message.content or ""
	except Exception as e:
		print(f"Error calling OpenAI API: {e}")
		raise


@mlflow.trace(span_type=SpanType.AGENT)
def run_function_calling_example(question: str) -> str:
	"""Run OpenAI function calling example with weather tool.

	Args:
		question: User question about weather

	Returns:
		Final response from the assistant after tool use
	"""
	client = openai.OpenAI()

	tools = [
		{
			"type": "function",
			"function": {
				"name": "get_weather",
				"description": "Get current weather for a city",
				"parameters": {
					"type": "object",
					"properties": {"city": {"type": "string"}},
					"required": ["city"],
				},
			},
		}
	]

	tool_functions = {"get_weather": get_weather}

	messages: List[Dict[str, Union[str, List]]] = [{"role": "user", "content": question}]

	try:
		# Initial request with tools
		response = client.chat.completions.create(
			model="gpt-4o-mini", 
			messages=messages,  # type: ignore
			tools=tools  # type: ignore
		)

		ai_msg = response.choices[0].message
		messages.append(ai_msg.model_dump())  # type: ignore

		# Handle tool calls if present
		if tool_calls := ai_msg.tool_calls:
			for tool_call in tool_calls:
				if hasattr(tool_call, 'function'):
					function_name = tool_call.function.name
					if tool_func := tool_functions.get(function_name):
						args = json.loads(tool_call.function.arguments)
						tool_result = tool_func(**args)
					else:
						raise RuntimeError(f"Unknown tool function: {function_name}")

					messages.append({
						"role": "tool",
						"tool_call_id": tool_call.id,
						"content": tool_result,
					})

			# Send tool results back to get final response
			response = client.chat.completions.create(
				model="gpt-4o-mini", 
				messages=messages  # type: ignore
			)

		return response.choices[0].message.content or ""
	except Exception as e:
		print(f"Error in function calling example: {e}")
		raise


def openai_example(tracking_url: str | None) -> None:
	"""Run OpenAI examples with MLflow autologging.

	Args:
		tracking_url: MLflow tracking server URL, None for local tracking
	"""
	api_key = getenv("OPENAI_API_KEY")
	if not api_key:
		print("OPENAI_API_KEY not found in environment variables")
		print("Skipping OpenAI examples")
		return

	# Set tracking URL if provided
	if tracking_url:
		mlflow.set_tracking_uri(tracking_url)
		try:
			current_uri = mlflow.get_tracking_uri()
			print(f"Connected to MLflow tracking server: {current_uri}")
		except Exception as e:
			print(f"Warning: Could not verify connection to MLflow server: {e}")
			print("Continuing with local tracking...")
			mlflow.set_tracking_uri("")
	else:
		print("Using local MLflow tracking (mlruns/ directory)")

	# Enable OpenAI autologging
	mlflow.openai.autolog()

	# Set experiment
	experiment_name = "OpenAI Examples"
	print(f"Setting up experiment: {experiment_name}")
	mlflow.set_experiment(experiment_name)

	print("\n=== Running OpenAI Chat Completion Example ===")
	try:
		chat_response = run_openai_chat_example()
		print(f"Chat response: {chat_response}")
	except Exception as e:
		print(f"Chat example failed: {e}")

	print("\n=== Running OpenAI Function Calling Example ===")
	try:
		weather_question = "What's the weather like in Paris today?"
		function_response = run_function_calling_example(weather_question)
		print(f"Question: {weather_question}")
		print(f"Function calling response: {function_response}")
	except Exception as e:
		print(f"Function calling example failed: {e}")

	# Print trace information
	try:
		last_trace_id = mlflow.get_last_active_trace_id()
		if last_trace_id:
			trace = mlflow.get_trace(trace_id=last_trace_id)
			print("\n=== Trace Information ===")
			print(f"Trace ID: {last_trace_id}")
			print(f"Number of spans: {len(trace.data.spans)}")

			# Print token usage if available
			if hasattr(trace.info, "token_usage") and trace.info.token_usage:
				total_usage = trace.info.token_usage
				print(f"Total tokens used: {total_usage.get('total_tokens', 'N/A')}")
	except Exception as e:
		print(f"Could not retrieve trace information: {e}")
