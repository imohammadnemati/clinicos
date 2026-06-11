INTENT_SCORES = {
    'booking_request': 10,
    'price_check': 7,
    'inquiry': 5,
    'content_question': 3,
    'complaint': 2,
    'small_talk': 0
}

URGENCY_SCORES = {'high': 5, 'medium': 3, 'low': 1, 'none': 0}

WEIGHTS = {
    'intent': 0.35,
    'service_interest': 0.15,
    'price_interest': 0.10,
    'urgency': 0.10,
    'appointment_request': 0.15,
    'conversation_depth': 0.05,
    'engagement': 0.05,
    'recency': 0.05
}

def normalize_score(raw, min_score=0, max_score=10):
    return max(min_score, min(max_score, raw))

def get_intent_score(intent_type):
    return INTENT_SCORES.get(intent_type, 2)

def get_service_interest_score(service_interest):
    return 5 if service_interest else 0

def get_price_interest_score(price_interest):
    return 4 if price_interest else 0

def get_urgency_score(urgency):
    return URGENCY_SCORES.get(urgency, 0)

def get_appointment_request_score(appointment_request):
    return 8 if appointment_request else 0

def get_conversation_depth_score(depth):
    return min(depth, 5)

def calculate_lead_score(intent, service_interest, price_interest, urgency, appointment_request, conversation_depth, patient_id=None):
    intent_raw = get_intent_score(intent)
    service_raw = get_service_interest_score(service_interest)
    price_raw = get_price_interest_score(price_interest)
    urgency_raw = get_urgency_score(urgency)
    appt_raw = get_appointment_request_score(appointment_request)
    depth_raw = get_conversation_depth_score(conversation_depth)
    
    weighted = (intent_raw * WEIGHTS['intent'] +
                service_raw * WEIGHTS['service_interest'] +
                price_raw * WEIGHTS['price_interest'] +
                urgency_raw * WEIGHTS['urgency'] +
                appt_raw * WEIGHTS['appointment_request'] +
                depth_raw * WEIGHTS['conversation_depth'])
    
    return normalize_score(weighted, 0, 10)