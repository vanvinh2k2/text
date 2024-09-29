from rest_framework import generics, status, permissions
from rest_framework.response import Response

from app.core.serializers import HistorySerializer
from app.core.models import History
from app.users.models import User

# Create your views here.

class HistoryAPIView(generics.CreateAPIView, generics.ListAPIView):
    serializer_class = HistorySerializer
    permission_classes = [permissions.IsAuthenticated]
    queryset = History.objects.all()
    lookup_field = 'code_id'

    def post(self, request):
        serializer = self.get_serializer(data=request.data)

        if serializer.is_valid():
            serializer.save(user=request.user)
            return Response(
                {"message": "History created successfully.", "history": serializer.data},
                status=status.HTTP_201_CREATED,
            )

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    def get(self, request, code_id=None):
        if code_id:
            try:
                history_instance = History.objects.get(code_id=code_id)
            except History.DoesNotExist:
                return Response(
                    {"message": "History not found."},
                    status=status.HTTP_404_NOT_FOUND
                )
            serializer = self.serializer_class(history_instance, context={'request': request})
            return Response({'message': 'Get history successfully.',
                            'history': serializer.data
                            }, status=status.HTTP_200_OK)
        query_set = self.get_queryset()
        serializer = self.serializer_class(query_set, many=True, context={'request': request})
        return Response({'message': 'Get history successfully.',
                        'history': serializer.data
                        }, status=status.HTTP_200_OK)

    
    def put(self, request, code_id=None):
        try:
            history_instance = History.objects.get(code_id=code_id)
        except History.DoesNotExist:
            return Response(
                {"message": "History not found."},
                status=status.HTTP_404_NOT_FOUND
            )
        
        # Lấy dữ liệu từ request
        amount = request.data.get("payment", None)
        cate = request.data.get("category", None)

        # Nếu không có amount trong request, giữ nguyên giá trị từ history_instance
        if amount is None:
            amount = history_instance.payment
        if cate is None:
            cate = history_instance.category

        # Lấy thông tin người dùng
        try:
            user = User.objects.get(id=request.user.id)
        except User.DoesNotExist:
            return Response(
                {"message": "User not found."},
                status=status.HTTP_404_NOT_FOUND
            )
        
        # Kiểm tra và cập nhật số tiền
        if cate is not None:
            if cate == "nap_vnd":
                if user.category == "vn":
                    user.money += amount
                else:
                    user.money += amount / 21610
            elif cate == "rut_vnd":
                if user.category == "vn":
                    user.money -= amount
                else:
                    user.money -= amount / 21610
            elif cate == "nap_usdt":
                if user.category == "vn":
                    user.money += amount * 21610
                else:
                    user.money += amount
            else:  # Giả sử trường hợp còn lại là "rut_usdt"
                if user.category == "vn":
                    user.money -= amount * 21610
                else:
                    user.money -= amount
        
        # Sao chép request.data và giữ lại các giá trị cũ nếu không được truyền lên
        request_data = request.data.copy()
        if 'payment' not in request_data:
            request_data['payment'] = history_instance.payment
        if 'category' not in request_data:
            request_data['category'] = history_instance.category
            
        # Chỉ lưu user nếu trạng thái là "success"
        if request.data.get("status") == "success" and history_instance.status == "waiting":
            user.save()

        serializer = HistorySerializer(history_instance, data=request_data, partial=False)
        if serializer.is_valid():
            serializer.save(user=request.user)
            return Response(
                {"message": "History updated successfully.", "history": serializer.data},
                status=status.HTTP_200_OK
            )
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, code_id=None):
        try:
            history_instance = History.objects.get(code_id=code_id)
        except History.DoesNotExist:
            return Response(
                {"message": "History not found."},
                status=status.HTTP_404_NOT_FOUND
            )
        history_instance.delete()
        return Response(
            {"message": "History deleted successfully."},
            status=status.HTTP_204_NO_CONTENT
        )

from rest_framework import generics, permissions
from rest_framework.response import Response
from app.core.serializers import HistorySerializer
from app.core.models import History

class HistoryWithUser(generics.RetrieveAPIView):
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = HistorySerializer
    queryset = History.objects.all()

    def get(self, request):
        try:
            uid = request.user.id
            query_set = self.get_queryset().filter(user_id=uid)
            serializer = self.serializer_class(query_set, many=True, context={'request': request})
            return Response(
                {
                    'message': 'Get history successfully.',
                    'history': serializer.data
                },
                status=status.HTTP_200_OK
            )
        except Exception as e:
            return Response(
                {"message": "An error occurred.", "error": str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

            