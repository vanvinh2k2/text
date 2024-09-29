from rest_framework import serializers

from app.users.models import User, VerificationCode
from django.contrib.auth import get_user_model

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ("id", "username", "email", "money", "category")

class VerifyCodeSerializer(serializers.ModelSerializer):
    email = serializers.EmailField()
    class Meta:
        model = VerificationCode
        fields = "__all__"
    
    def validate(self, args):
        code = args.get("code", None)
        email = args.get("email", None)
        if not User.objects.filter(email=email).exists():
            raise serializers.ValidationError({"email": "Email không tồn tại!"})
        
        try:
            verification_record = VerificationCode.objects.get(email=email)
        except VerificationCode.DoesNotExist:
            raise serializers.ValidationError({"code": "Mã xác nhận không tồn tại cho email này!"})

        if verification_record.code != code:
            raise serializers.ValidationError({"code": "Mã xác nhận không chính xác!"})

        if verification_record.is_expired():
            raise serializers.ValidationError({"code": "Mã xác nhận đã hết hạn!"})

        return super().validate(args)

class RegistrationSerializer(serializers.ModelSerializer):
    username = serializers.CharField(max_length=50, min_length=6)
    password = serializers.CharField(max_length=150, write_only=True)
    money = serializers.DecimalField(max_digits=30, decimal_places=2, read_only=True)
    category = serializers.CharField(read_only=True)

    class Meta:
        model = User
        fields = ("id", "username", "email", "password", "money", "category")

    def validate(self, args):
        username = args.get("username", None)
        email = args.get("email", None)
        if User.objects.filter(username__icontains=username).exists():
            raise serializers.ValidationError({"username": "Tên người dùng đã tồn tại!"})
        if User.objects.filter(email__icontains=email).exists():
            raise serializers.ValidationError({"email": "Email này đã tồn tại!"})

        return super().validate(args)

    def create(self, validated_data):
        return User.objects.create_user(**validated_data)
