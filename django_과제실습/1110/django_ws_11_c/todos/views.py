from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.response import Response
from django.shortcuts import render, get_list_or_404, get_object_or_404
from django.db.models import Count
from .models import Todo, Recommend
from .serializers import TodoSerializer, TodoListSerializer, RecommendSerializer

# Create your views here.
@api_view(['GET', 'POST'])
def todo_list(request):
    if request.method == 'GET':
        todos = Todo.objects.all()
        serializer = TodoListSerializer(todos, many=True)
        return Response(serializer.data)
    
    elif request.method == 'POST':
        serializer = TodoSerializer(data=request.data)
        if serializer.is_valid(raise_exception=True):
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
    
@api_view(['DELETE', 'GET'])
def todo_detail(request, todo_pk):
    todo = Todo.objects.annotate(recommend_count=Count('recommend')).get(pk=todo_pk)
    if request.method == 'DELETE':
        todo.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
    elif request.method == 'GET':
        serializer = TodoSerializer(todo)
        return Response(serializer.data)

@api_view(['POST'])
def recommend_create(request, todo_pk):
    todo = get_object_or_404(Todo, pk=todo_pk)
    if request.method == 'POST':
        serializer = RecommendSerializer(data=request.data)
        if serializer.is_valid(raise_exception=True):
            serializer.save(todo=todo)
            # recommend = form.save(commit=False)
            # recommend.todo = todo
            # recommend.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)

@api_view(['GET'])
def recommend_list(request):
    recommends = get_list_or_404(Recommend)
    serializer = RecommendSerializer(recommends, many=True)
    return Response(serializer.data)