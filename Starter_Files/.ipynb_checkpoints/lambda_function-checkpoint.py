### Required Libraries ###
from datetime import datetime
from dateutil.relativedelta import relativedelta

### Functionality Helper Functions ###
def parse_int(n):
    """
    Securely converts a non-integer value to integer.
    """
    try:
        return int(n)
    except ValueError:
        return float("nan")


def build_validation_result(is_valid, violated_slot, message_content):
    """
    Define a result message structured as Lex response.
    """
    if message_content is None:
        return {"isValid": is_valid, "violatedSlot": violated_slot}

    return {
        "isValid": is_valid,
        "violatedSlot": violated_slot,
        "message": {"contentType": "PlainText", "content": message_content},
    }


### Dialog Actions Helper Functions ###
def get_slots(intent_request):
    """
    Fetch all the slots and their values from the current intent.
    """
    return intent_request["currentIntent"]["slots"]


def elicit_slot(session_attributes, intent_name, slots, slot_to_elicit, message):
    """
    Defines an elicit slot type response.
    """

    return {
        "sessionAttributes": session_attributes,
        "dialogAction": {
            "type": "ElicitSlot",
            "intentName": intent_name,
            "slots": slots,
            "slotToElicit": slot_to_elicit,
            "message": message,
        },
    }


def delegate(session_attributes, slots):
    """
    Defines a delegate slot type response.
    """

    return {
        "sessionAttributes": session_attributes,
        "dialogAction": {"type": "Delegate", "slots": slots},
    }


def close(session_attributes, fulfillment_state, message):
    """
    Defines a close slot type response.
    """

    response = {
        "sessionAttributes": session_attributes,
        "dialogAction": {
            "type": "Close",
            "fulfillmentState": fulfillment_state,
            "message": message,
        },
    }

    return response



def validate_data(age, amount, intent_request):
    if int(age) < 0 or int(age) > 65:
        return build_validation_result(False, 'age', 'must be between 0 and 65')
        # response = elicit_slot(intent_request['sessionAttributes'], intent_request['currentIntent']['name'], intent_request['currentIntent']['slots'], validation['violatedSlot'], validation['message'])
        
    elif int(amount) < 5000:
        return build_validation_result(False, 'investmentAmount', 'must be higher than 5000')
            
        # response = elicit_slot(intent_request['sessionAttributes'], intent_request['currentIntent']['name'], intent_request['currentIntent']['slots'], validation['violatedSlot'], validation['message'])
    else:
        return build_validation_result(True, None, None)
       

### Intents Handlers ###
def recommend_portfolio(intent_request):
    """
    Performs dialog management and fulfillment for recommending a portfolio.
    """

    first_name = get_slots(intent_request)["firstName"]
    age = get_slots(intent_request)["age"]
    investment_amount = get_slots(intent_request)["investmentAmount"]
    risk_level = get_slots(intent_request)["riskLevel"]
    source = intent_request["invocationSource"]
    try:
        if source == "DialogCodeHook":
            # Perform basic validation on the supplied input slots.
            # Use the elicitSlot dialog action to re-prompt
            # for the first violation detected.
    
            ### YOUR DATA VALIDATION CODE STARTS HERE ###
            validation_result = validate_data(age, investment_amount, intent_request)
            if not validation_result['isValid']:
                slots[validation_result["violatedSlot"]] = None
                return elicit_slot(intent_request['sessionAttributes'], intent_request['currentIntent']['name'], intent_request['currentIntent']['slots'], validation['violatedSlot'], validation['message'])
    
            ### YOUR DATA VALIDATION CODE ENDS HERE ###
    
            # Fetch current session attibutes
            output_session_attributes = intent_request["sessionAttributes"]
    
            return delegate(output_session_attributes, get_slots(intent_request))
    
        # Get the initial investment recommendation
    
        ### YOUR FINAL INVESTMENT RECOMMENDATION CODE STARTS HERE ###
        responseDict = {
            "None": "100% bonds (AGG), 0% equities (SPY)",
            "Low": "60% bonds (AGG), 40% equities (SPY)",
            "Medium": "40% bonds (AGG), 60% equities (SPY)",
            "High": "20% bonds (AGG), 80% equities (SPY)"
        }
        initial_recommendation = responseDict[risk_level]
    
        ### YOUR FINAL INVESTMENT RECOMMENDATION CODE ENDS HERE ###
    
        # Return a message with the initial recommendation based on the risk level.
    
    return close(
        intent_request["sessionAttributes"],
        "Fulfilled",
        {
            "contentType": "PlainText",
            "content": """{} thank you for your information;
            based on the risk level you defined, my recommendation is to choose an investment portfolio with {}
            """.format(
                first_name, initial_recommendation
            ),
        },
    )


### Intents Dispatcher ###
def dispatch(intent_request):
    """
    Called when the user specifies an intent for this bot.
    """

    intent_name = intent_request["currentIntent"]["name"]

    # Dispatch to bot's intent handlers
    if intent_name == "RecommendPortfolio":
        return recommend_portfolio(intent_request)

    raise Exception("Intent with name " + intent_name + " not supported")


### Main Handler ###
def lambda_handler(event, context):
    """
    Route the incoming request based on intent.
    The JSON body of the request is provided in the event slot.
    """

    return dispatch(event)
