from rest_framework import serializers
from .models import Category, Book, Thread, Comment


class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ('id', 'name')


class BookListSerializer(serializers.ModelSerializer):
    class Meta:
        model = Book
        fields = ('id', 'title', 'author', 'isbn', 'cover')


class BookSerializer(serializers.ModelSerializer):
    class BookThreadSerializer(serializers.ModelSerializer):
        class Meta:
            model = Thread
            fields = ('id', 'title', 'content', 'reading_date')

    category = CategorySerializer(read_only=True)
    threads = BookThreadSerializer(source='thread_set', many=True, read_only=True)
    num_of_threads = serializers.IntegerField(source='thread_set.count', read_only=True)

    class Meta:
        model = Book
        fields = '__all__'


class ThreadListSerializer(serializers.ModelSerializer):
    class ThreadBookSerializer(serializers.ModelSerializer):
        class Meta:
            model = Book
            fields = ('title',)

    book = ThreadBookSerializer(read_only=True)

    class Meta:
        model = Thread
        fields = ('id', 'title', 'book')


class CommentSerializer(serializers.ModelSerializer):
    class CommentThreadSerializer(serializers.ModelSerializer):
        class Meta:
            model = Thread
            fields = ('title',)

    thread = CommentThreadSerializer(read_only=True)

    class Meta:
        model = Comment
        fields = '__all__'


class ThreadSerializer(serializers.ModelSerializer):
    class ThreadBookSerializer(serializers.ModelSerializer):
        class Meta:
            model = Book
            fields = ('title',)

    # 대상 도서는 이후 view에서 serializer.save(book=book)으로 지정한다.
    book = ThreadBookSerializer(read_only=True)
    comments = CommentSerializer(source='comment_set', many=True, read_only=True)
    num_of_comments = serializers.IntegerField(source='comment_set.count', read_only=True)

    class Meta:
        model = Thread
        fields = '__all__'
