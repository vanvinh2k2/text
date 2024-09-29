from rest_framework import serializers
from app.users.serializers import UserSerializer
from app.core.models import History


class HistorySerializer(serializers.ModelSerializer):
    payment = serializers.DecimalField(decimal_places=2, max_digits=30, default=2)
    user = UserSerializer(read_only=True)

    class Meta:
        model = History
        fields = '__all__'
