from rest_framework import serializers
from wechat.models import *


class PhotoSerializer(serializers.ModelSerializer):
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


class PhotoDetailSerializer(serializers.ModelSerializer):
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
