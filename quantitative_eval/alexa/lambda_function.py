# -*- coding: utf-8 -*-

# Romeo & Juliet RAG Question-Answering System - Alexa Skills Kit Integration
# This is an updated version adapted for Romeo and Juliet literature questions

import logging
import ask_sdk_core.utils as ask_utils
import json
import random

from ask_sdk_core.skill_builder import SkillBuilder
from ask_sdk_core.dispatch_components import AbstractRequestHandler
from ask_sdk_core.dispatch_components import AbstractExceptionHandler
from ask_sdk_core.handler_input import HandlerInput

from ask_sdk_model import Response

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

# Load intent mapping data (in production, this would be loaded from external source)
INTENT_RESPONSES = {
    "Romeo_Metaphor_Juliet": [
        "Based on Romeo and Juliet: Romeo uses the metaphor of the sun to describe Juliet, saying 'Juliet is the sun' in the famous balcony scene.",
        "In Shakespeare's play: Romeo compares Juliet to the sun, declaring that she is the light that banishes the darkness.",
        "According to the text: Romeo employs the sun as a metaphor when he sees Juliet at her window, calling her his sun.",
        "From Romeo and Juliet: Romeo describes Juliet using the sun metaphor, showing how she illuminates his world.",
        "In the play: Romeo's most famous metaphor for Juliet is comparing her to the sun in Act II, Scene II."
    ],
    "Juliet_Name_Request": [
        "Based on Romeo and Juliet: Juliet asks Romeo to deny his father and refuse his family name, saying 'deny thy father and refuse thy name'.",
        "In Shakespeare's play: Juliet requests that Romeo renounce his Montague name for their love.",
        "According to the text: Juliet wishes Romeo would abandon his family name so they could be together.",
        "From Romeo and Juliet: Juliet asks Romeo to give up being a Montague, questioning what's in a name.",
        "In the play: Juliet's request centers on Romeo abandoning his family identity for their love."
    ],
    "Friar_Marriage_Reason": [
        "Based on Romeo and Juliet: Friar Laurence agrees to marry them hoping it will turn the households' hatred into love.",
        "In Shakespeare's play: The Friar believes their marriage might end the feud between the Montagues and Capulets.",
        "According to the text: Friar Laurence hopes the union will bring peace to the warring families.",
        "From Romeo and Juliet: The Friar sees their marriage as a way to reconcile the feuding houses.",
        "In the play: Friar Laurence agrees because he believes love can triumph over family hatred."
    ],
    "Tybalt_Insult_Romeo": [
        "Based on Romeo and Juliet: Tybalt calls Romeo a villain when they encounter each other.",
        "In Shakespeare's play: Tybalt hurls the insult 'villain' at Romeo during their confrontation.",
        "According to the text: Tybalt addresses Romeo with hostile words, calling him a villain.",
        "From Romeo and Juliet: Tybalt's main insult toward Romeo is calling him a villain.",
        "In the play: Tybalt uses 'villain' as his primary insult against Romeo."
    ],
    "Mercutio_Death_Curse": [
        "Based on Romeo and Juliet: Mercutio curses both houses, saying 'A plague on both your houses'.",
        "In Shakespeare's play: Mercutio's dying curse is 'A plague on both your houses' - meaning both Montagues and Capulets.",
        "According to the text: Mercutio utters his famous curse on both feuding families as he dies.",
        "From Romeo and Juliet: Mercutio's final words curse both the Montague and Capulet houses.",
        "In the play: Mercutio's death curse calls a plague upon both feuding families."
    ],
    "Romeo_Banishment_View": [
        "Based on Romeo and Juliet: Romeo views banishment as worse than death, saying there is no world outside Verona's walls.",
        "In Shakespeare's play: Romeo considers banishment more terrible than death itself.",
        "According to the text: Romeo believes banishment is a fate worse than death because it separates him from Juliet.",
        "From Romeo and Juliet: Romeo sees his exile as more painful than execution would be.",
        "In the play: Romeo's reaction to banishment shows he considers it the worst possible punishment."
    ]
}

class LaunchRequestHandler(AbstractRequestHandler):
    """Handler for Skill Launch."""
    def can_handle(self, handler_input):
        return ask_utils.is_request_type("LaunchRequest")(handler_input)

    def handle(self, handler_input):
        response_variations = [
            "Welcome to the Romeo and Juliet assistant! I can answer questions about Shakespeare's tragic love story.",
            "Greetings! I'm here to help with questions about Romeo and Juliet. What would you like to know?",
            "Hello! I can assist you with questions about the characters, plot, and themes in Romeo and Juliet.",
            "Welcome! Ask me anything about Romeo and Juliet - from character motivations to famous quotes."
        ]

        speak_output = random.choice(response_variations)

        ask_variations = [
            'What would you like to know about Romeo and Juliet?',
            "Feel free to ask about any character, scene, or theme from the play.",
            "What aspect of Romeo and Juliet interests you?",
            "Ask me about the star-crossed lovers or any other element of the story."
        ]

        ask_output = random.choice(ask_variations)

        return (
            handler_input.response_builder
                .speak(speak_output)
                .ask(ask_output)
                .response
        )

class HelpIntentHandler(AbstractRequestHandler):
    """Handler for Help Intent."""
    def can_handle(self, handler_input):
        return ask_utils.is_intent_name("AMAZON.HelpIntent")(handler_input)

    def handle(self, handler_input):
        response_variations = [
            "I can answer questions about Romeo and Juliet, including character analysis, plot events, themes, and famous quotes. For example, you can ask me about Romeo's metaphors for Juliet, or what curse Mercutio utters.",
            "Ask me about any aspect of Shakespeare's Romeo and Juliet - characters like Romeo, Juliet, Mercutio, or Tybalt, plot events, themes like love and fate, or famous scenes.",
            "I'm here to help with Romeo and Juliet questions. You can ask about character motivations, plot developments, literary devices, or specific scenes from the play."
        ]

        speak_output = random.choice(response_variations)
        ask_output = "What would you like to know about Romeo and Juliet?"

        return (
            handler_input.response_builder
                .speak(speak_output)
                .ask(ask_output)
                .response
        )

class CancelOrStopIntentHandler(AbstractRequestHandler):
    """Single handler for Cancel and Stop Intent."""
    def can_handle(self, handler_input):
        return (ask_utils.is_intent_name("AMAZON.CancelIntent")(handler_input) or
                ask_utils.is_intent_name("AMAZON.StopIntent")(handler_input))

    def handle(self, handler_input):
        response_variations = [
            "Thank you for exploring Romeo and Juliet with me. May your love of literature continue to grow!",
            "Farewell! I hope I've helped illuminate the beauty of Shakespeare's Romeo and Juliet.",
            "Goodbye! Remember, 'These violent delights have violent ends.' Until next time!",
            "Thank you for your questions about Romeo and Juliet. Keep exploring the world of literature!"
        ]

        speak_output = random.choice(response_variations)

        return (
            handler_input.response_builder
                .speak(speak_output)
                .set_should_end_session(True)
                .response
        )

class FallbackIntentHandler(AbstractRequestHandler):
    """Handler for Fallback Intent - includes FAISS integration option."""
    def __init__(self):
        self.fallback_count = 0

    def can_handle(self, handler_input):
        return ask_utils.is_intent_name("AMAZON.FallbackIntent")(handler_input)

    def handle(self, handler_input):
        self.fallback_count += 1

        if self.fallback_count >= 30:
            return handler_input.response_builder.speak(
                "I'm having technical difficulties right now. Please try again later. Thank you for your patience."
            ).set_should_end_session(True).response
        else:
            # In a production system, this is where we would integrate FAISS retrieval
            # For now, we provide a helpful fallback message
            response_variations = [
                "I didn't understand that question about Romeo and Juliet. Try asking about specific characters, scenes, or themes.",
                "I'm not sure about that. You can ask me about Romeo's love for Juliet, the family feud, or specific scenes from the play.",
                "That question isn't clear to me. Try asking about character motivations, plot events, or famous quotes from Romeo and Juliet."
            ]

            speak_output = random.choice(response_variations)
            reprompt = "What would you like to know about Romeo and Juliet?"

            return handler_input.response_builder.speak(speak_output).ask(reprompt).response

class SessionEndedRequestHandler(AbstractRequestHandler):
    """Handler for Session End."""
    def can_handle(self, handler_input):
        return ask_utils.is_request_type("SessionEndedRequest")(handler_input)

    def handle(self, handler_input):
        return handler_input.response_builder.response

# Romeo & Juliet Specific Intent Handlers

class RomeoMetaphorJulietIntentHandler(AbstractRequestHandler):
    """Handler for Romeo's metaphor about Juliet."""
    def can_handle(self, handler_input):
        return ask_utils.is_intent_name("Romeo_Metaphor_Juliet")(handler_input)

    def handle(self, handler_input):
        speak_output = random.choice(INTENT_RESPONSES["Romeo_Metaphor_Juliet"])

        ask_variations = [
            'Would you like to know more about Romeo and Juliet?',
            "What else would you like to explore about the play?",
            "Is there another aspect of Romeo and Juliet you'd like to discuss?"
        ]
        ask_output = random.choice(ask_variations)

        return (
            handler_input.response_builder
                .speak(speak_output)
                .ask(ask_output)
                .response
        )

class JulietNameRequestIntentHandler(AbstractRequestHandler):
    """Handler for Juliet's request about Romeo's name."""
    def can_handle(self, handler_input):
        return ask_utils.is_intent_name("Juliet_Name_Request")(handler_input)

    def handle(self, handler_input):
        speak_output = random.choice(INTENT_RESPONSES["Juliet_Name_Request"])

        ask_variations = [
            'Would you like to know more about Romeo and Juliet?',
            "What else would you like to explore about the play?",
            "Is there another aspect of Romeo and Juliet you'd like to discuss?"
        ]
        ask_output = random.choice(ask_variations)

        return (
            handler_input.response_builder
                .speak(speak_output)
                .ask(ask_output)
                .response
        )

class FriarMarriageReasonIntentHandler(AbstractRequestHandler):
    """Handler for Friar Laurence's reason for helping with marriage."""
    def can_handle(self, handler_input):
        return ask_utils.is_intent_name("Friar_Marriage_Reason")(handler_input)

    def handle(self, handler_input):
        speak_output = random.choice(INTENT_RESPONSES["Friar_Marriage_Reason"])

        ask_variations = [
            'Would you like to know more about Romeo and Juliet?',
            "What else would you like to explore about the play?",
            "Is there another aspect of Romeo and Juliet you'd like to discuss?"
        ]
        ask_output = random.choice(ask_variations)

        return (
            handler_input.response_builder
                .speak(speak_output)
                .ask(ask_output)
                .response
        )

class TybaltInsultRomeoIntentHandler(AbstractRequestHandler):
    """Handler for Tybalt's insult to Romeo."""
    def can_handle(self, handler_input):
        return ask_utils.is_intent_name("Tybalt_Insult_Romeo")(handler_input)

    def handle(self, handler_input):
        speak_output = random.choice(INTENT_RESPONSES["Tybalt_Insult_Romeo"])

        ask_variations = [
            'Would you like to know more about Romeo and Juliet?',
            "What else would you like to explore about the play?",
            "Is there another aspect of Romeo and Juliet you'd like to discuss?"
        ]
        ask_output = random.choice(ask_variations)

        return (
            handler_input.response_builder
                .speak(speak_output)
                .ask(ask_output)
                .response
        )

class MercutioDeathCurseIntentHandler(AbstractRequestHandler):
    """Handler for Mercutio's death curse."""
    def can_handle(self, handler_input):
        return ask_utils.is_intent_name("Mercutio_Death_Curse")(handler_input)

    def handle(self, handler_input):
        speak_output = random.choice(INTENT_RESPONSES["Mercutio_Death_Curse"])

        ask_variations = [
            'Would you like to know more about Romeo and Juliet?',
            "What else would you like to explore about the play?",
            "Is there another aspect of Romeo and Juliet you'd like to discuss?"
        ]
        ask_output = random.choice(ask_variations)

        return (
            handler_input.response_builder
                .speak(speak_output)
                .ask(ask_output)
                .response
        )

class RomeoBanishmentViewIntentHandler(AbstractRequestHandler):
    """Handler for Romeo's view on banishment."""
    def can_handle(self, handler_input):
        return ask_utils.is_intent_name("Romeo_Banishment_View")(handler_input)

    def handle(self, handler_input):
        speak_output = random.choice(INTENT_RESPONSES["Romeo_Banishment_View"])

        ask_variations = [
            'Would you like to know more about Romeo and Juliet?',
            "What else would you like to explore about the play?",
            "Is there another aspect of Romeo and Juliet you'd like to discuss?"
        ]
        ask_output = random.choice(ask_variations)

        return (
            handler_input.response_builder
                .speak(speak_output)
                .ask(ask_output)
                .response
        )

class GeneralQuestionIntentHandler(AbstractRequestHandler):
    """Handler for general questions - could integrate with FAISS in production."""
    def can_handle(self, handler_input):
        return ask_utils.is_intent_name("General_Question")(handler_input)

    def handle(self, handler_input):
        # In production, this would call our FAISS retrieval system
        # For now, provide a general helpful response

        general_responses = [
            "That's an interesting question about Romeo and Juliet. The play explores themes of love, fate, family conflict, and youth versus age.",
            "Romeo and Juliet contains many complex elements. The story shows how family feuds can destroy young love and lead to tragedy.",
            "Shakespeare's Romeo and Juliet is rich with literary devices, character development, and timeless themes about love and conflict.",
            "The play Romeo and Juliet demonstrates how miscommunication and family hatred can lead to devastating consequences.",
            "Romeo and Juliet explores the power of love to both unite and destroy, set against the backdrop of an ancient family feud."
        ]

        speak_output = random.choice(general_responses)

        ask_output = "Would you like to ask about a specific character or scene?"

        return (
            handler_input.response_builder
                .speak(speak_output)
                .ask(ask_output)
                .response
        )

class IntentReflectorHandler(AbstractRequestHandler):
    """The intent reflector for debugging."""
    def can_handle(self, handler_input):
        return ask_utils.is_request_type("IntentRequest")(handler_input)

    def handle(self, handler_input):
        intent_name = ask_utils.get_intent_name(handler_input)
        speak_output = f"You just triggered the {intent_name} intent."

        return (
            handler_input.response_builder
                .speak(speak_output)
                .response
        )

class CatchAllExceptionHandler(AbstractExceptionHandler):
    """Generic error handling."""
    def can_handle(self, handler_input, exception):
        return True

    def handle(self, handler_input, exception):
        logger.error(exception, exc_info=True)

        speak_output = "Sorry, I had trouble answering your question about Romeo and Juliet. Please try again."

        return (
            handler_input.response_builder
                .speak(speak_output)
                .ask(speak_output)
                .response
        )

# The SkillBuilder object acts as the entry point for your skill
sb = SkillBuilder()

sb.add_request_handler(LaunchRequestHandler())
sb.add_request_handler(HelpIntentHandler())
sb.add_request_handler(CancelOrStopIntentHandler())
sb.add_request_handler(FallbackIntentHandler())
sb.add_request_handler(SessionEndedRequestHandler())

# Romeo & Juliet specific handlers
sb.add_request_handler(RomeoMetaphorJulietIntentHandler())
sb.add_request_handler(JulietNameRequestIntentHandler())
sb.add_request_handler(FriarMarriageReasonIntentHandler())
sb.add_request_handler(TybaltInsultRomeoIntentHandler())
sb.add_request_handler(MercutioDeathCurseIntentHandler())
sb.add_request_handler(RomeoBanishmentViewIntentHandler())
sb.add_request_handler(GeneralQuestionIntentHandler())

sb.add_request_handler(IntentReflectorHandler()) # make sure IntentReflectorHandler is last
sb.add_exception_handler(CatchAllExceptionHandler())

lambda_handler = sb.lambda_handler()