from django.contrib.auth import get_user_model
from rest_framework import serializers

from advarisk.users.models import User as UserType
from dj_rest_auth.serializers import TokenSerializer
from rest_framework import serializers
from dj_rest_auth.registration.serializers import RegisterSerializer
from rest_framework import serializers
from django.contrib.auth import get_user_model

User = get_user_model()


class UserSerializer(serializers.ModelSerializer[UserType]):
    class Meta:
        model = User
        fields = ["name", "url"]

        extra_kwargs = {
            "url": {"view_name": "api:user-detail", "lookup_field": "pk"},
        }



class CustomTokenSerializer(TokenSerializer):
    is_superuser = serializers.SerializerMethodField()
    id = serializers.ReadOnlyField(source='user.id')
    username = serializers.ReadOnlyField(source='user.username')

    def get_is_superuser(self, obj):
        return obj.user.is_superuser

    class Meta(TokenSerializer.Meta):
        fields = TokenSerializer.Meta.fields + ('is_superuser', 'id', 'username')




class CustomRegisterSerializer(RegisterSerializer):
    User = get_user_model()


