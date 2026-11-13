from rest_framework import serializers
from .models import Book


class BookListSerializer(serializers.ModelSerializer):

    class Meta:
        model = Book
        fields = ('id', 'isbn', 'author', 'title', )

class BookSerializer(serializers.ModelSerializer):

    class Meta:
        model = Book
        fields = '__all__'