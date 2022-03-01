from django.contrib import messages
from django.contrib.auth import authenticate, login
from django.contrib.auth.models import User,auth
from django.http.response import JsonResponse, HttpResponse
from django.shortcuts import render, redirect
from django.views.decorators.csrf import csrf_exempt
from rest_framework.parsers import JSONParser
from.models import Message
from.Serializer import MessageSerializer, UserSerializer



def login(request):
    if request.session.has_key('logged-in'):
        return render(request,'all.html')
    if request.method=='POST':
        first=request.POST['uname']
        second=request.POST['pass']
        ab=auth.authenticate(username=first,password=second)
        if ab is not None:
            auth.login(request,ab)
            request.session['logged-in'] = True
            return redirect('all')
        else:
            messages.error(request,"register first")
            return redirect('login')
    else:
        return render(request,"login.html")
def signup(request):
    if request.session.has_key('logged-in'):
        return render(request, "all.html")
    if request.method == 'POST':
        first_nam = request.POST['first_name']
        sname = request.POST['last_name']
        username = request.POST['username']
        email = request.POST['email']
        password = request.POST['password']
        passw = request.POST['passw']
        if (password == passw):
            if User.objects.filter(email=email).exists():
                messages.info(request, "check email")
                return redirect('/')
            elif User.objects.filter(username=username).exists():
                messages.info(request, "check username")
                return redirect('/')
            else:
                ab = User.objects.create_user(first_name=first_nam, last_name=sname, username=username, email=email,
                                              password=password)
                ab.save()
                messages.success(request, "work properly")
                return render(request, "login.html")

        else:
            messages.info(request, "check password")
            return redirect('signup')
    else:
        return render(request, "signup.html")

def chat(request):
    if not request.user.is_authenticated:
        return redirect('login')
    if request.method == "GET":
        return render(request, 'chat.html',{'users': User.objects.all})

def logout(request):
    auth.logout(request)
    return redirect('login')
def message_view(request, sender, receiver):
    if not request.user.is_authenticated:
        return redirect('/')
    if request.method == "GET":
        return render(request, "messages.html",
                      {'users': User.objects.exclude(username=request.user.username),
                       'receiver': User.objects.get(id=receiver),
                       'messages': Message.objects.filter(sender_id=sender, receiver_id=receiver) |
                                   Message.objects.filter(sender_id=receiver, receiver_id=sender)})
@csrf_exempt
def message_list(request, sender=None, receiver=None):
    """
    List all required messages, or create a new message.
    """
    if request.method == 'GET':
        messages = Message.objects.filter(sender_id=sender, receiver_id=receiver, is_read=False)
        serializer = MessageSerializer(messages, many=True, context={'request': request})
        for message in messages:
            message.is_read = True
            message.save()
        return JsonResponse(serializer.data, safe=False)

    elif request.method == 'POST':
        data = JSONParser().parse(request)
        serializer = MessageSerializer(data=data)
        if serializer.is_valid():
            serializer.save()
            return JsonResponse(serializer.data, status=201)
        return JsonResponse(serializer.errors, status=400)

def allusers(request):
    if not request.user.is_authenticated:
        return redirect('login')
    if request.method == "GET":
        return render(request, 'all.html', {'users': User.objects.all})