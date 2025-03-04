
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import json
from .llm_service import get_chatbot_response
from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from .forms import RegisterForm, LoginForm
from .models import ChatHistory  

@csrf_exempt
def chatbot_view(request):
    return render(request, 'chatbot.html')

@csrf_exempt
def chatbot_api(request):
    if request.method == 'POST':
        try:
            body_unicode = request.body.decode("utf-8")
            data = json.loads(body_unicode)
            question = data.get('query')
            question = str(question)
            print("Printing question from response: ", question)

            if not question:
                return JsonResponse({'error': 'Missing "query" parameter'}, status=400)

            # Get chatbot response
            response = get_chatbot_response(question, request.user)  # Pass the user object

            # Return the response as a JSON object
            return JsonResponse({'response': response})

        except json.JSONDecodeError:
            return JsonResponse({'error': 'Invalid JSON format'}, status=400)
    elif request.method == 'GET':
        return JsonResponse({'message': 'Nothing for the get method'}, status=400)

    return JsonResponse({'error': 'Invalid request method'}, status=400)



@csrf_exempt
def register_view(request):
    if request.method == 'POST':
        form = RegisterForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect('chatbot_view')  # Redirect to chatbot page after registration
    else:
        form = RegisterForm()
    return render(request, 'register.html', {'form': form})
@csrf_exempt
def login_view(request):
    if request.method == 'POST':
        form = LoginForm(request, data=request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(username=username, password=password)
            if user is not None:
                login(request, user)

                # Fetch the user's chat history
                chat_history = ChatHistory.objects.filter(user=user).order_by('timestamp')
                chat_messages = [{'role': chat.role, 'message': chat.message} for chat in chat_history]

                # Pass chat history to the chatbot template
                return render(request, 'chatbot.html', {'chat_messages': chat_messages})
    else:
        form = LoginForm()
    return render(request, 'login.html', {'form': form})




@csrf_exempt
def logout_view(request):
    if request.method == 'POST':
        logout(request)
        return JsonResponse({'status': 'success'}, status=200)
    return JsonResponse({'error': 'Invalid request method'}, status=400)