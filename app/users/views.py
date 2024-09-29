from rest_framework import generics, status, permissions
from rest_framework.response import Response

from app.users.serializers import RegistrationSerializer, UserSerializer, VerifyCodeSerializer
from rest_framework.exceptions import NotFound
import random
from app.users.models import VerificationCode, User
from app.users.helper import send_email_verify


def send_verification_email(email):
    code = str(random.randint(100000, 999999))
    VerificationCode.objects.update_or_create(email=email, defaults={'code': code})
    # send email
    send_email_verify(email, code)

class RegistrationAPIView(generics.GenericAPIView):
    serializer_class = RegistrationSerializer

    def post(self, request):
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            send_verification_email(request.data.get("email"))
            serializer.save()
            return Response(
                {"message": "Tạo tài khoản thành công.", "user": serializer.data},
                status=status.HTTP_201_CREATED,
            )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class UserAPIView(generics.RetrieveAPIView):
    serializer_class = UserSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request, *args, **kwargs):
        user = request.user
        if not user or not user.is_authenticated:
            raise NotFound({"message": "Không tìm thấy người dùng."})
        
        serializer = self.get_serializer(user)
        return Response(
            {"message": "Lấy tài khoản thành công.", "user": serializer.data},
            status=status.HTTP_200_OK
        )
    
class VerifyRegistrationCodeView(generics.UpdateAPIView):
    serializer_class = VerifyCodeSerializer
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        email = serializer.validated_data.get('email')

        try:
            user = User.objects.get(email=email)
            if not user.is_verified:
                user.is_verified = True
                user.save()
                VerificationCode.objects.filter(email=email).delete()
                return Response({'message': 'Tài khoản đã được xác thực thành công!'}, status=status.HTTP_200_OK)
            else:
                return Response({'error': 'Tài khoản đã được xác thực trước đó.'}, status=status.HTTP_400_BAD_REQUEST)
        except User.DoesNotExist:
            return Response({'error': 'Người dùng không tồn tại.'}, status=status.HTTP_404_NOT_FOUND)