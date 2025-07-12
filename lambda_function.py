import logging
import os
import google.generativeai as genai
from ask_sdk_core.skill_builder import SkillBuilder
from ask_sdk_core.dispatch_components import AbstractRequestHandler
from ask_sdk_core.dispatch_components import AbstractExceptionHandler
from ask_sdk_core.utils import is_request_type, is_intent_name
from ask_sdk_core.handler_input import HandlerInput
from ask_sdk_model import Response

# --- IMPORTANT ---
# 1. Set your API Key as an Environment Variable in the Lambda Console.
# Name the variable 'GEMINI_API_KEY'
# You can also replace this with any other LLM you have an API key for
genai.configure(api_key=os.environ.get("GEMINI_API_KEY"))
llm = genai.GenerativeModel('gemini-2.5-flash') # Or 'gemini-1.5-flash' for speed/cost

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)
logger.info("Lambda function reached.")

class LaunchRequestHandler(AbstractRequestHandler):
    """Handler for Skill Launch."""
    def can_handle(self, handler_input):
        return is_request_type("LaunchRequest")(handler_input)

    def handle(self, handler_input):
        speech_text = "Welcome to your AI helper. What can I help you with?"
        handler_input.response_builder.speak(speech_text).set_should_end_session(False)
        return handler_input.response_builder.response

class AskLlmIntentHandler(AbstractRequestHandler):
    """Handler for the AskLlmIntent."""
    def can_handle(self, handler_input):
        logger.info(f"Received Intent to ask AI...")
        return is_intent_name("AskLlmIntent")(handler_input)

    def handle(self, handler_input):
        # Extract the user's query from the slot
        query = handler_input.request_envelope.request.intent.slots["query"].value

        if not query:
            speech_text = "I didn't catch that. What would you like to ask?"
            handler_input.response_builder.speak(speech_text).set_should_end_session(False)
            return handler_input.response_builder.response

        logger.info(f"Received query: {query}")
        speech_text = "One moment..."
        handler_input.response_builder.speak(speech_text)

        try:
            # Call the LLM API
            logger.info(f"Calling LLM API...")
            response = llm.generate_content(query)
            llm_response_text = response.text
            logger.info(f"LLM Response: {llm_response_text}")

            # Send the LLM's response back to the user
            handler_input.response_builder.speak(llm_response_text).set_should_end_session(False)

        except Exception as e:
            logger.error(f"Error calling LLM: {e}")
            error_speech = "I'm sorry, Gemini had trouble getting an answer. Please try again."
            handler_input.response_builder.speak(error_speech).set_should_end_session(False)

        return handler_input.response_builder.response

# Other default handlers (Help, Cancel/Stop, etc.)
class HelpIntentHandler(AbstractRequestHandler):
    def can_handle(self, handler_input):
        return is_intent_name("AMAZON.HelpIntent")(handler_input)
    def handle(self, handler_input):
        speech_text = "You can ask me anything, for example, what is the capital of France?"
        handler_input.response_builder.speak(speech_text).ask(speech_text)
        return handler_input.response_builder.response

class CancelOrStopIntentHandler(AbstractRequestHandler):
    def can_handle(self, handler_input):
        return (is_intent_name("AMAZON.CancelIntent")(handler_input) or
                is_intent_name("AMAZON.StopIntent")(handler_input))
    def handle(self, handler_input):
        speech_text = "Goodbye!"
        handler_input.response_builder.speak(speech_text)
        return handler_input.response_builder.response

class SessionEndedRequestHandler(AbstractRequestHandler):
    def can_handle(self, handler_input):
        return is_request_type("SessionEndedRequest")(handler_input)
    def handle(self, handler_input):
        return handler_input.response_builder.response

class CatchAllExceptionHandler(AbstractExceptionHandler):
    def can_handle(self, handler_input, exception):
        return True
    def handle(self, handler_input, exception):
        logger.error(exception, exc_info=True)
        speech = "Sorry, I had trouble doing what you asked. Please try again."
        handler_input.response_builder.speak(speech).ask(speech)
        return handler_input.response_builder.response

# Skill Builder setup
sb = SkillBuilder()
sb.add_request_handler(LaunchRequestHandler())
sb.add_request_handler(AskLlmIntentHandler())
sb.add_request_handler(HelpIntentHandler())
sb.add_request_handler(CancelOrStopIntentHandler())
sb.add_request_handler(SessionEndedRequestHandler())
sb.add_exception_handler(CatchAllExceptionHandler())

lambda_handler = sb.lambda_handler()