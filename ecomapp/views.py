from django.http import HttpResponse
from rest_framework.response import Response
from rest_framework import status
from django.shortcuts import get_object_or_404, render
from django.views import View
from rest_framework.views import APIView
from ecomapp.decorators import logout_after_10_minutes
from ecomapp.forms import CustomUserCreationForm
from ecomapp.mixins import EmailSendingMixin
from ecomapp.models import Category, Customer, Message, MessageHistory
from django.contrib.auth import authenticate,login,logout
from rest_framework.authtoken.models import Token
from ecomapp.serializers import CategorySerializer, CustomerSerializer, LoginSerializer, OTPResetSerializer, OTPverifySerializer, PasswordSetSerializer, RegisterSerializer
from rest_framework.permissions import IsAuthenticated
from rest_framework.authentication import TokenAuthentication
    
import pyotp
from django.conf import settings
from django.contrib.auth.hashers import make_password
import requests
import json
from django.http import JsonResponse
from ecomapp.tasks import delete_all_secret_keys
# Create your views here.


class RegisterView(APIView):

    def post(self, request):
        serializer = RegisterSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        

class ListView(APIView):
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]
    def get(self,request):
        customers = Customer.objects.filter(is_superuser=False)
        serializer = CustomerSerializer(customers, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
    


class CustomLoginView(APIView):
    
    def post(self, request):
        serializer = LoginSerializer(data=request.data)
        if serializer.is_valid():
            email = request.data.get('email')
            password = request.data.get('password')
            print(request.data,'...........data')
            user = authenticate(username=email, password=password)
            print(user,'.......user')
            if user is not None:
                login(request,user)
                token, _ = Token.objects.get_or_create(user=user)
                return Response({'token': token.key, 'email': user.email}, status=status.HTTP_200_OK)
            else:
                return Response({'error': 'Invalid credentials'}, status=status.HTTP_401_UNAUTHORIZED)
            
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class LogoutView(APIView):
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]

    def get(self, request, format=None):
        logout(request,request.user)
        request.user.auth_token.delete()
        return Response({'data':'Success'},status=status.HTTP_200_OK)
    

class CreateCategory(APIView):
    
    def get(self,request):
        category = Category.objects.all()
        serializer = CategorySerializer(category, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
    


        
class PasswordResetRequestView(APIView,EmailSendingMixin):
    def post(self, request):
        email = request.data.get('email')
        serializer = OTPResetSerializer(data=request.data)

        if serializer.is_valid():
            try:
                user = Customer.objects.get(email=email)
            except Customer.DoesNotExist:
                return Response({'error': 'User with this email does not exist'}, status=status.HTTP_404_NOT_FOUND)

            secret_key = pyotp.random_base32()
            user.secret_key = secret_key 
            print(user.created_at,'------created_at------')
            user.save() 
            
            # Generate an OTP based on the secret key
            totp = pyotp.TOTP(secret_key,digits=8,interval=40)
            token = totp.now()  # Generate the OTP
            
            # # Send the OTP to the user's email
            # send_mail(
            #     'Password Reset OTP',
            #     f'Your OTP for password reset is: {token}',
            #     settings.EMAIL_HOST_USER,  # Sender's email
            #     [email],  # List of recipients
            #     fail_silently=False,
            # )

            sent = self.send_custom_mail(
                'Password Reset OTP',
                f'Your OTP for password reset is: {token}',
                settings.EMAIL_HOST_USER,  # Sender's email
                email,  # Recipient's email
            )

            if sent:
                return Response({'message': 'OTP sent to your email'}, status=status.HTTP_200_OK)
            else:
                return Response({'error': 'Failed to send OTP'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
            
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class OTPVerificationView(APIView):
    def post(self, request):
        serializer = OTPverifySerializer(data=request.data)

        if serializer.is_valid():
            email = serializer.validated_data.get('email')

            # Retrieve the user by email
            try:
                user = Customer.objects.get(email=email)
            except Customer.DoesNotExist:
                return Response({'error': 'User with this email does not exist'}, status=status.HTTP_400_BAD_REQUEST)

            # Retrieve the secret_key from the user object
            secret_key = user.secret_key  # Ensure 'secret_key' is a field in your 'Customer' model
            print('------secret_key-------------------',secret_key)
            if secret_key:
                otp = request.data.get('otp')
                
                new_password = request.data.get('new_password')

                serializer = PasswordSetSerializer(data ={'new_password':new_password})
                if serializer.is_valid():
                    totp = pyotp.TOTP(secret_key,digits=8,interval=40)

                    try:
                        is_valid_otp = totp.verify(str(otp))
                    except Exception as e:
                        return Response({'error': 'Invalid OTP format'}, status=status.HTTP_400_BAD_REQUEST)

                    if is_valid_otp:
                        user.set_password(new_password)
                        user.save()
                        return Response({'message': 'Password changed successfully'}, status=status.HTTP_200_OK)
                    else:
                        return Response({'error': 'Invalid OTP'}, status=status.HTTP_400_BAD_REQUEST)
                else:
                    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
            else:
                return Response({'error': 'Secret key not found'}, status=status.HTTP_400_BAD_REQUEST)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)




'''FROM HERE CHAT APPLICATIONS '''


from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from django.db.models import Q
from django.views.generic.edit import FormView
from django.urls import reverse_lazy
from django.views.generic.edit import CreateView
from django.http import JsonResponse
from django.views.decorators.http import require_GET

class UserRegisterView(CreateView):
    form_class = CustomUserCreationForm
    template_name = 'register.html'
    success_url = reverse_lazy('log_template')
    



class LoginTemView(View):

    def get(self,request):
        context = {}
        return render(request, "login.html", context)
    
    def post(self,request):
        print(request.POST.dict())
        context = {} 
        if request.POST.get('email') and request.POST.get('password'):
            try:
                user = authenticate(username=request.POST.get('email'), password=request.POST.get('password'))
                if user is not None:
                    login(request, user)
                    return redirect('/home/')
                else:
                    return redirect('/')
            except Exception as e:
                print()
                return redirect('/')
        else:
            return render(request, "login.html", context)

@method_decorator(logout_after_10_minutes, name='dispatch')     
@method_decorator(login_required, name='dispatch')     
class HomeView(View):

    def get(self, request):
        context = {}
        # print('request---data----',request.META)
        return render(request, "home.html", context)


def logout_view(request):
    logout(request)
    # print('request.user.is_authenticated:',request.user.is_authenticated)
    return redirect('/')

@logout_after_10_minutes
@login_required(login_url='/') 
def chat_list(request):
    receiver_users = Customer.objects.exclude(is_superuser=True).exclude(id=request.user.id)
    context = {'receiver_users': receiver_users}
    return render(request, 'chat/chat_list.html', context)


def save_fcm_token(request):
    if request.method == 'POST':
        
        fcm_token = request.POST.get('fcm_token')
        print('---fcm_token----:::----',fcm_token)

        print('------here------',request.user)
        try:
            user = Customer.objects.get(id=request.user.id)
            user.fcm_token = fcm_token
            user.save()
        except:
            ...
        
        return JsonResponse({'message': 'FCM token saved successfully'})
    else:
        return JsonResponse({'error': 'Invalid request method'}, status=400)



@login_required(login_url='/') 
@require_GET
def get_message_history(request):
    sender_username = request.GET.get('sender')
    receiver_username = request.GET.get('receiver')
    print(request.GET.dict(),'---------------------HERE')

    try:
        sender = Customer.objects.get(email=sender_username)
        receiver = Customer.objects.get(email=receiver_username)

        message_history = MessageHistory.objects.filter(
            Q(message__sender=sender, message__receiver=receiver) |
            Q(message__sender=receiver, message__receiver=sender)
        ).order_by('timestamp')  # Order the messages by timestamp, adjust as needed

        history_data = []
        for history_item in message_history:
            history_data.append({
                'sender_username': history_item.message.sender.email,
                'receiver_email': history_item.message.receiver.email,
                'message': history_item.content,
                'created_by': history_item.created_by.email if history_item.created_by else None,
            })

    except Customer.DoesNotExist:
        return JsonResponse({'error': 'User not found'}, status=404)
    except MessageHistory.DoesNotExist:
        return JsonResponse({'error': 'Message history not found'}, status=404)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)

    return JsonResponse(history_data, safe=False)









































#no needed

# def send_notification(registration_ids , message_title , message_desc):
#     fcm_api = "BK3Q4ZdEKTgW3ifVufVCGvnh-22E2JAnYw3L6Uqsonv9EvKg8p7RA6zYUwIIooKNiUX6DxgRcS8P33jp-3Ev2X4"
#     url = "https://fcm.googleapis.com/fcm/send"
    
#     headers = {
#     "Content-Type":"application/json",
#     "Authorization": 'key='+fcm_api}

#     payload = {
#         "registration_ids" :registration_ids,
#         "priority" : "high",
#         "notification" : {
#             "body" : message_desc,
#             "title" : message_title,
#             "image" : "https://i.ytimg.com/vi/m5WUPHRgdOA/hqdefault.jpg?sqp=-oaymwEXCOADEI4CSFryq4qpAwkIARUAAIhCGAE=&rs=AOn4CLDwz-yjKEdwxvKjwMANGk5BedCOXQ",
#             "icon": "https://yt3.ggpht.com/ytc/AKedOLSMvoy4DeAVkMSAuiuaBdIGKC7a5Ib75bKzKO3jHg=s900-c-k-c0x00ffffff-no-rj",
            
#         }
#     }

#     result = requests.post(url,  data=json.dumps(payload), headers=headers )
#     print(result.json())



# def send(request):
#     resgistration  = [
#     ]
#     send_notification(resgistration , 'Code Keen added a new video' , 'Code Keen new video alert')
#     return HttpResponse("sent")


# def showFirebaseJS(request):
#     data='importScripts("https://www.gstatic.com/firebasejs/8.2.0/firebase-app.js");' \
#          'importScripts("https://www.gstatic.com/firebasejs/8.2.0/firebase-messaging.js"); ' \
#          'var firebaseConfig = {' \
#          '        apiKey: "AIzaSyBgnd6Y8jYStTkltENO2uzNgO1EOZW30X8",' \
#          '        authDomain: "chat-d6eb2.firebaseapp.com",' \
#          '        databaseURL: "https://chat-d6eb2-default-rtdb.firebaseio.com",' \
#          '        projectId: "chat-d6eb2",' \
#          '        storageBucket: "chat-d6eb2.appspot.com",' \
#          '        messagingSenderId: "119893492348",' \
#          '        appId: "1:119893492348:web:9c850df4dee73f27f6fff9",' \
#          '        measurementId: "G-3FESXB4DBN"' \
#          ' };' \
#          'firebase.initializeApp(firebaseConfig);' \
#          'const messaging=firebase.messaging();' \
#          'messaging.setBackgroundMessageHandler(function (payload) {' \
#          '    console.log(payload);' \
#          '    const notification=JSON.parse(payload);' \
#          '    const notificationOption={' \
#          '        body:notification.body,' \
#          '        icon:notification.icon' \
#          '    };' \
#          '    return self.registration.showNotification(payload.notification.title,notificationOption);' \
#          '});'

#     return HttpResponse(data,content_type="text/javascript")


# @require_GET
# def get_message_history(request):
#     sender_username = request.GET.get('sender')
#     receiver_username = request.GET.get('receiver')

#     try:
#         sender = Customer.objects.get(email=sender_username)
#         receiver = Customer.objects.get(email=receiver_username)

#         message_history = MessageHistory.objects.filter(
#             Q(message__sender=sender, message__receiver=receiver) |
#             Q(message__sender=receiver, message__receiver=sender)
#         ).order_by('timestamp')  # Order the messages by timestamp, adjust as needed

#         history_data = []
#         for history_item in message_history:
#             sender_email = history_item.message.sender.email
#             receiver_email = history_item.message.receiver.email

#             if sender_email == sender_username:
#                 sender_email = sender_username
#                 receiver_email = receiver_username
#             else:
#                 sender_email = receiver_username
#                 receiver_email = sender_username

#             history_data.append({
#                 'sender_username': sender_email,
#                 'receiver_email': receiver_email,
#                 'message': history_item.content,
#                 'created_by': history_item.created_by.email if history_item.created_by else None,
#             })

#     except Customer.DoesNotExist:
#         return JsonResponse({'error': 'User not found'}, status=404)
#     except MessageHistory.DoesNotExist:
#         return JsonResponse({'error': 'Message history not found'}, status=404)
#     except Exception as e:
#         return JsonResponse({'error': str(e)}, status=500)

#     return JsonResponse(history_data, safe=False)





















# class OTPVerificationView(APIView):
#     def post(self, request):
#         serializer = OTPverifySerializer(data=request.data)

        
#         if serializer.is_valid():
#             email = serializer.validated_data.get('email')

#             user = get_object_or_404(Customer, email=email)
#             print('user---------',user)

#             if user:
#                 otp = request.data.get('otp')
#                 new_password = request.data.get('new_password')

#                 secret_key = user.secret_key  
#                 print('secret_key-------',secret_key)
#                 if secret_key:
#                     totp = pyotp.TOTP(secret_key)

#                     try:
#                         is_valid_otp = totp.verify(str(otp))
#                     except Exception as e:
#                         return Response({'error': 'Invalid OTP format'}, status=status.HTTP_400_BAD_REQUEST)

#                     if is_valid_otp:
                        
#                         user.set_password(new_password)
#                         user.save()
#                         return Response({'message': 'Password changed successfully'}, status=status.HTTP_200_OK)
#                     else:
#                         return Response({'error': 'Invalid OTP'}, status=status.HTTP_400_BAD_REQUEST)
#                 else:
#                     return Response({'error': 'Secret key not found'}, status=status.HTTP_400_BAD_REQUEST)
#             else:
#                 return Response({'error': 'User with this email does not exist'}, status=status.HTTP_400_BAD_REQUEST)
#         else:
#             return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        


# class OTPVerificationView(APIView):
#     def post(self, request):
#         serializer = OTPverifySerializer(data=request.data)
#         if serializer.is_valid():
#             serializer.save()  # This will handle OTP verification and password setting
#             return Response({'message': 'Password changed successfully'}, status=status.HTTP_200_OK)
#         else:
#             return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)










































































# class ItemsViews(APIView):
#     authentication_classes = [TokenAuthentication]
#     permission_classes = [IsAuthenticated]

#     def get(self, request):
#         items = Item.objects.all()
#         serializer = ItemSerializer(items, many=True)
#         return Response(serializer.data, status=status.HTTP_200_OK)

#     def post(self, request):
#         serializer = ItemSerializer(data=request.data)
#         if serializer.is_valid():
#             serializer.save()
#             return Response(serializer.data, status=status.HTTP_201_CREATED)
#         return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)



# class EachItemsView(APIView):

#     authentication_classes = [TokenAuthentication]
#     permission_classes = [IsAuthenticated]

#     def post(self, request, item_id):
#         try:
#             item = Item.objects.get(pk=item_id)
#         except Item.DoesNotExist:
#             return Response({'error': 'Item not found'}, status=status.HTTP_404_NOT_FOUND)

#         serializer = ItemSerializer(item, data=request.data)
#         if serializer.is_valid():
#             serializer.save()
#             return Response(serializer.data, status=status.HTTP_200_OK)
#         return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    