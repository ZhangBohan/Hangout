from rest_framework import serializers
from wechat.models import *


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('id', 'username', )


class PhotoSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)
    latitude = serializers.FloatField(write_only=True, allow_null=True)
    longitude = serializers.FloatField(write_only=True, allow_null=True)

    class Meta:
        model = Photo
        exclude = ('location', )

        read_only_fields = ('user',
                            'n_total_mark',
                            'n_account_mark',
                            'n_account_comment',
                            'n_account_vote',
                            'n_total_watched',
                            'updated_at',
                            'created_at')

    def create(self, validated_data):
        latitude = validated_data.pop('latitude')
        longitude = validated_data.pop('longitude')
        location = None
        if latitude is not None and longitude is not None:
            location = Point(latitude, longitude)
        validated_data['location'] = location
        photo = super(PhotoSerializer, self).create(validated_data)
        return photo


class PhotoDetailSerializer(PhotoSerializer):
    is_marked = serializers.BooleanField(help_text="是否打分")
    is_voted = serializers.BooleanField(help_text="是否赞")

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
