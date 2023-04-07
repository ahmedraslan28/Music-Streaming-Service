from rest_framework import serializers
from django.contrib.auth import get_user_model


User = get_user_model()


class LoginSerializer(serializers.Serializer):
    email = serializers.CharField(max_length=255)
    password = serializers.CharField(max_length=255)


class RegisterSerializer(serializers.ModelSerializer):
    confirm_password = serializers.CharField(write_only=True)
    password = serializers.CharField(write_only=True)
    profile_image = serializers.ImageField(max_length=None,
                                           allow_empty_file=True, use_url=True)

    class Meta:
        model = User
        fields = ['id', 'email', 'username', 'first_name',
                  'last_name', 'birth_date', 'is_male', 'is_artist', 'password', 'confirm_password', 'profile_image']

    def validate(self, data):
        if data['password'] != data['confirm_password']:
            raise serializers.ValidationError("password do not match")
        return data

    def create(self, validated_data):
        password = validated_data.pop('password')
        validated_data.pop('confirm_password')
        user = User.objects.create(is_active=False, **validated_data)
        user.set_password(password)
        user.save()
        return user


class ForgotPasswordSerializer(serializers.Serializer):
    email = serializers.EmailField()


class ResetPasswordSerializer(serializers.Serializer):
    password = serializers.CharField()
    confirm_password = serializers.CharField()

    def validate(self, data):
        super().validate(data)
        if data['password'] != data['confirm_password']:
            raise serializers.ValidationError(
                "the two passwords doesn't match!")
        return data


class UpdatePasswordSerializer(serializers.Serializer):
    old_password = serializers.CharField()
    new_password = serializers.CharField()
    confirm_new_password = serializers.CharField()

    def validate(self, data):
        super().validate(data)
        user = self.context['user']
        old_password = data['old_password']
        new_password = data['new_password']
        confirm_new_password = data['confirm_new_password']

        if new_password != confirm_new_password:
            raise serializers.ValidationError("The two passwords do not match")

        if len(old_password) > 0 and not user.check_password(old_password):
            raise serializers.ValidationError("old password is invalid")

        if not (all(len(v) > 0 for v in [old_password, new_password, confirm_new_password])
                or all(len(v) == 0 for v in [old_password, new_password, confirm_new_password])):
            raise serializers.ValidationError(
                "please check your passwords fields")

        return data

    def update(self, instance, validated_data):
        old_password = validated_data.pop('old_password')
        new_password = validated_data.pop('new_password')
        repeat_password = validated_data.pop('confirm_new_password')
        instance.set_password(new_password)
        print("instance is ", instance)
        return instance
