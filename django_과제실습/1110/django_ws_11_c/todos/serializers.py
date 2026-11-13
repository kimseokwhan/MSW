from rest_framework import serializers
from .models import Todo, Recommend


class RecommendSerializer(serializers.ModelSerializer):
    class TodoWorkSerializer(serializers.ModelSerializer):
        class Meta:
            model = Todo
            fields = ('work',)
    todo = TodoWorkSerializer(read_only=True)
    class Meta:
        model: Recommend
        fields = '__all__'
        # read_only_fields = ('todo', )

class TodoSerializer(serializers.ModelSerializer):
    class RecommendSerializerForTodoDetail(serializers.ModelSerializer):
        class Meta:
            model = Recommend
            exclude = ('todo', )

    recommned_set = RecommendSerializerForTodoDetail(many=True)
    recommend_count = serializers.SerializerMethodField()
    class Meta:
        model = Todo
        fields = '__all__'
    def get_recommend_count(self, obj):
        if hasattr(obj, 'recommend_count'):
            return obj.recommend_count
        return obj.recommned_set.count()

class TodoListSerializer(serializers.ModelSerializer):
    class Meta:
        model = Todo
        fields = ('work', 'is_completed', )
