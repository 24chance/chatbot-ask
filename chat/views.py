from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from chat.translator import translate_text
from chatbot.ai.qa_model import ask_model
from .models import Conversation, Message
from django.shortcuts import render, redirect, get_object_or_404
from django.http import JsonResponse
import json
from .hf_inference import ask_model_via_api



def chatbot_reply(message):
    message = message.lower()

    if "hello" in message:
        return "Hi human."
    elif "how are you" in message:
        return "I am code. I feel nothing."
    elif "bye" in message:
        return "Goodbye."
    else:
        return "I don't understand. Classic human-AI conversation."


@login_required(login_url='login')
def home(request):
    conversation = Conversation.objects.filter(user=request.user).last()
    conversations = Conversation.objects.filter(user=request.user).order_by("-created_at")

    if conversation:
        return redirect('chat', conversation_id=conversation.id)
    return render(request, "chat.html", {
        "conversations": conversations,
        "messages": [],
        "active_convo": None
    })

@login_required(login_url='login')
def new_chat(request):
    conversation = Conversation.objects.create(
        user=request.user,
        title="New Conversation"
    )
    return redirect('chat', conversation_id=conversation.id)


@login_required(login_url='login')
def chat_page(request, conversation_id):
    conversation = get_object_or_404(
        Conversation, id=conversation_id, user=request.user
    )

    messages = conversation.messages.all().order_by("created_at")
    conversations = Conversation.objects.filter(user=request.user).order_by("-created_at")

    return render(request, "chat.html", {
        "messages": messages,
        "conversations": conversations,
        "active_convo": conversation
    })




@login_required
def send_message(request, conversation_id):
    conversation = get_object_or_404(
        Conversation, id=conversation_id, user=request.user
    )

    data = json.loads(request.body)
    user_message = data["message"]

    bot_reply = ask_model_via_api(user_message)

    Message.objects.create(conversation=conversation, sender="user", text=user_message)
    Message.objects.create(conversation=conversation, sender="bot", text=bot_reply)

    if conversation.title == "New Conversation":
        conversation.title = user_message[:30]
        conversation.save()

    return JsonResponse({"reply": bot_reply})

@login_required(login_url='login')
def rename_chat(request, conversation_id):
    if request.method == "POST":
        conversation = get_object_or_404(
            Conversation, id=conversation_id, user=request.user
        )
        new_title = request.POST.get("title")
        conversation.title = new_title
        conversation.save()
        return JsonResponse({"status": "ok"})

@login_required(login_url='login')
def delete_chat(request, conversation_id):
    if request.method == "POST":
        conversation = get_object_or_404(
            Conversation, id=conversation_id, user=request.user
        )
        conversation.delete()
        return JsonResponse({"status": "ok"})

def login_page(request):
    message = ""
    if request.method == "POST":
        username = request.POST.get("username")
        password = request.POST.get("password")
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            return redirect('home')
        else:
            message = "Invalid username or password"
    return render(request, "login.html", {"message": message})

def logout_page(request):
    logout(request)
    return redirect('login')
