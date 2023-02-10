from rest_framework import serializers
from .models import Profile
from django.contrib.auth import authenticate



class ChangePasswordSerializer(serializers.Serializer):
    current_password = serializers.CharField()
    new_password = serializers.CharField()

    def validate(self, data):
        if data["current_password"]==data["new_password"]:
            raise serializers.ValidationError({"message":"Please enter a new password that is different from your current password"})
        user = self.context["request"].user
        is_pass=user.check_password(data["current_password"])
        print(is_pass)
        if is_pass is True:
            print(is_pass)
            user.set_password(data["new_password"])
            user.save()
            return user
        raise serializers.ValidationError({"message":'Incorrect Current Password'},code=400)




class RegisterSerializer(serializers.ModelSerializer):
    class Meta:
        model = Profile
        fields = (
            'username',
            'email',
            'first_name',
            'last_name',
            'password'
        )
        extra_kwargs = {'password': {'write_only': True}}
    def create(self, validated_data):
        password = validated_data.pop('password')
        profile = Profile.objects.create(**validated_data)
        profile.set_password(password)
        profile.save()
        return profile


class LoginSerializer(serializers.Serializer):
    username = serializers.CharField()
    password = serializers.CharField()

    def validate(self, data):
        user = authenticate(**data)
        if user is not None:
            return user
        else:
            raise serializers.ValidationError('Incorrect Credentials')


class ProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = Profile
        fields = (
            'username',
            'email',
            'first_name',
            'last_name'
        )
    