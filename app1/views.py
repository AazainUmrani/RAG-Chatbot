
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import json
from .llm_service import get_chatbot_response
from django.shortcuts import render


@csrf_exempt
def chatbot_view(request):
    return render(request, 'chatbot.html')

def chatbot_api(request):
    if request.method == 'POST':
        try:
 
            body_unicode = request.body.decode("utf-8") 
            data = json.loads(body_unicode)  
            question = data.get('query') 
            question=str(question)
            print("Printing question from response: ",question)
            if not question:
                return JsonResponse({'error': 'Missing "query" parameter'}, status=400)
            
            # Get chatbot response based on the question
            response = get_chatbot_response(question)
            
            # Return the response as a JSON object
            return JsonResponse({'response': response})

        except json.JSONDecodeError:
            return JsonResponse({'error': 'Invalid JSON format'}, status=400)
    elif request.method == 'GET':
        return JsonResponse({'message': 'Nothing for the get method'}, status=400)


    return JsonResponse({'error': 'Invalid request method'}, status=400)





