from rest_framework import serializers
from wechat.models import *


class UserSerializer(serializers.ModelSerializer):
    nickname = serializers.CharField(source='userinfo.nickname', help_text="昵称")
    avatar_url = serializers.URLField(source='userinfo.avatar_url', help_text="头像")

    class Meta:
        model = User
        fields = ('id', 'avatar_url', 'nickname', )


class PhotoSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True, help_text="所有者")

    class Meta:
        model = Photo
        exclude = ('location', 'status', 'n_avg_mark',)

        read_only_fields = ('user',
                            'n_total_mark',
                            'n_account_mark',
                            'n_account_comment',
                            'n_account_vote',
                            'n_avg_mark',
                            'n_total_watched',
                            'n_favorite',
                            'city',
                            'country',
                            'province',
                            'updated_at',
                            'created_at',)

    def create(self, validated_data):
        photo = super(PhotoSerializer, self).create(validated_data)
        return photo


class PhotoDetailSerializer(PhotoSerializer):
    is_marked = serializers.BooleanField(help_text="是否打分")
    is_voted = serializers.BooleanField(help_text="是否赞")
    is_favorited = serializers.BooleanField(help_text="是否收藏")

    class Meta:
        model = Photo
        fields = '__all__'

        read_only_fields = ('user',
                            'n_total_mark',
                            'n_account_mark',
                            'n_account_comment',
                            'n_account_vote',
                            'n_total_watched',
                            'updated_at',
                            'created_at')


class CommentSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)

    class Meta:
        model = Comment
        fields = '__all__'

        read_only_fields = ('user',
                            'photo',
                            'updated_at',
                            'created_at')


class MarkSerializer(serializers.Serializer):
    mark = serializers.IntegerField(min_value=1, max_value=100, help_text="分数")

    def create(self, validated_data):
        mark, created = Mark.objects.get_or_create(**validated_data, defaults=dict(mark=validated_data.pop('mark')))
        return mark

    def update(self, instance, validated_data):
        pass


class PositionSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True, help_text="所有者")
    latitude = serializers.FloatField(write_only=True, allow_null=True)
    longitude = serializers.FloatField(write_only=True, allow_null=True)

    class Meta:
        model = UserLocation

        read_only_fields = ('province',
                            'district',
                            'city',
                            'created_at')

    def create(self, validated_data):
        latitude = validated_data.pop('latitude')
        longitude = validated_data.pop('longitude')
        location = None
        if latitude is not None and longitude is not None:
            location = Point(latitude, longitude)
        validated_data['location'] = location
        user_location, created = UserLocation.objects.get_or_create(user=validated_data['user'], defaults={
            'location': location
        })

        if not created:
            user_location.location = location
            user_location.save()
        return user_location
