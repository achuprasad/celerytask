from django.shortcuts import get_object_or_404
import pyotp
from rest_framework import serializers
from django.contrib.auth.models import User
from rest_framework.validators import UniqueValidator
from django.contrib.auth.password_validation import validate_password
from django.contrib.auth.hashers import make_password

from ecomapp.models import Category, Customer, Item

'''register'''
class RegisterSerializer(serializers.ModelSerializer):
    email = serializers.EmailField(
        required=True,
        validators=[UniqueValidator(queryset=Customer.objects.all())]
    )
    password = serializers.CharField(write_only=True, required=True, validators=[validate_password])
    first_name =  serializers.CharField(required=True)
    last_name = serializers.CharField(required=True)
    username = serializers.CharField(required=True)
    class Meta:
        model = Customer
        fields = ('first_name','last_name','email', 'password','username')
    def create(self, validated_data):
        validated_data['password'] = make_password(validated_data.get('password'))
        return super(RegisterSerializer, self).create(validated_data)


'''login'''
class LoginSerializer(serializers.Serializer):
    email = serializers.EmailField(required =True)
    password = serializers.CharField(max_length=128, write_only=True, required=True)


'''View customers --- pending to list in view'''
class CustomerSerializer(serializers.ModelSerializer):
    class Meta:
        model = Customer
        fields = ('id','first_name','last_name','email')





class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ['id', 'name']




class OTPResetSerializer(serializers.Serializer):

    email = serializers.EmailField(required=True)






class OTPverifySerializer(serializers.Serializer):

    email = serializers.EmailField()
    otp = serializers.CharField(max_length=10)
    # new_password = serializers.CharField(max_length=128, min_length=8)



class PasswordSetSerializer(serializers.Serializer):
    new_password = serializers.CharField(max_length=12, write_only=True)

    def validate_new_password(self, value):
        
        if not any(char.isdigit() for char in value):
            raise serializers.ValidationError("The password must contain at least one digit.")
        return value


# class ItemSerializer(serializers.ModelSerializer):
#     class Meta:
#         model = Item
#         fields = ('id', 'item_name', 'price', 'on_discount', 'discount_price', 'category', 'stock', 'description')

#     def validate(self, data):
#         if data.get('on_discount') and data.get('discount_price') and data['discount_price'] > data['price']:
#             raise serializers.ValidationError("Discount price cannot be greater than the original price.")
#         return data





# class OTPverifySerializer(serializers.Serializer):
    
#     email = serializers.EmailField()
#     otp = serializers.CharField(max_length=10)
#     new_password = serializers.CharField(max_length=128, min_length=8)

#     def validate(self, data):
#         email = data.get('email')
#         otp = data.get('otp')
#         new_password = data.get('new_password')

#         user = get_object_or_404(Customer, email=email)
#         print('---user-----',user)
#         if user:
#             secret_key = user.secret_key
#             print('---secret_key----',secret_key)
#             totp = pyotp.TOTP(secret_key)
#             print('totp--------',totp)

#             try:
#                 is_valid_otp = totp.verify(str(otp))
#                 print('is_valid_otp----',is_valid_otp)
#             except Exception as e:
#                 print('----e-------',e)
#                 raise serializers.ValidationError({'error': 'Invalid OTP format'})

#             if is_valid_otp:
#                     print(is_valid_otp)
#                     user.set_password(new_password)
#                     user.save()
#             else:
#                 raise serializers.ValidationError({'error': 'Invalid OTP'})
#         else:
#             raise serializers.ValidationError({'error': 'User with this email does not exist'})

#         return data