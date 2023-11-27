from rest_framework.response import Response
from rest_framework import status
from django.shortcuts import get_object_or_404, render
from django.views import View
from rest_framework.views import APIView
from ecomapp.mixins import EmailSendingMixin
from ecomapp.models import Category, Customer, Item
from django.contrib.auth import authenticate,login,logout
from rest_framework.authtoken.models import Token
from ecomapp.serializers import CategorySerializer, CustomerSerializer, LoginSerializer, OTPResetSerializer, OTPverifySerializer, PasswordSetSerializer, RegisterSerializer
from rest_framework.permissions import IsAuthenticated
from rest_framework.authentication import TokenAuthentication
    
import pyotp
from django.conf import settings
from django.contrib.auth.hashers import make_password

from ecomapp.tasks import delete_all_secret_keys
# Create your views here.


class RegisterView(APIView):

    def post(self, request):
        print(request.data,'......data')
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
    