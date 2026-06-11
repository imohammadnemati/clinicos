def calculate_lead_score(intent, service_interest, price_interest, urgency, appointment_request, conversation_depth):
    score = 0
    if intent == 'booking_request':
        score += 5
    elif intent == 'price_check':
        score += 3
    elif intent == 'inquiry':
        score += 1
    if service_interest:
        score += 2
    if price_interest:
        score += 2
    if urgency == 'high':
        score += 2
    if appointment_request:
        score += 4
    if conversation_depth >= 3:
        score += 1
    return min(score, 10)