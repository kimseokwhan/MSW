from rest_framework import serializers
from .models import Book, Review


class BookListSerializer(serializers.ModelSerializer):

    class Meta:
        model = Book
        fields = ('title', )

class BookSerializer(serializers.ModelSerializer):
    class ReviewDetailSerializer(serializers.ModelSerializer):
        class Meta:
            model = Review
            fields = ('content', 'score', )

    review_set = ReviewDetailSerializer(many=True, read_only=True)

    num_of_reviews = serializers.SerializerMethodField()

    class Meta:
        model = Book
        fields = '__all__'

    def get_num_of_reviews(self, obj):
        if hasattr(obj, 'num_of_reviews'):
            return obj.num_of_reviews
        return obj.review_set.count()

class ReviewListSerializer(serializers.ModelSerializer):
    class BookIsbnSerializer(serializers.ModelSerializer):
        class Meta:
            model = Book
            fields = ('isbn',)

    book = BookIsbnSerializer(read_only=True)

    class Meta:
        model = Review
        fields = ('book', 'content', 'score')

class ReviewSerializer(serializers.ModelSerializer):
    class BookIsbnSerializer(serializers.ModelSerializer):
        class Meta:
            model = Book
            fields = ('isbn', )

    book = BookIsbnSerializer(read_only=True)

    class Meta:
        model = Review
        fields = ('book', 'content', 'score')
        # read_only_fields = ('book',)