import os
from rest_framework import generics, status, permissions, filters
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.authtoken.models import Token
from rest_framework.parsers import MultiPartParser, FormParser, JSONParser
from django.contrib.auth import authenticate
from django.contrib.auth.models import User
from django.http import FileResponse, Http404
from django.shortcuts import get_object_or_404
from .models import Document, Category
from .serializers import UserSerializer, RegisterSerializer, DocumentSerializer, CategorySerializer

class CategoryListCreateView(generics.ListCreateAPIView):
    serializer_class = CategorySerializer

    def get_queryset(self):
        return Category.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

class CategoryDetailView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = CategorySerializer

    def get_queryset(self):
        return Category.objects.filter(user=self.request.user)

class DocumentListCreateView(generics.ListCreateAPIView):
    serializer_class = DocumentSerializer
    parser_classes = [MultiPartParser, FormParser, JSONParser]
    filter_backends = [filters.SearchFilter]
    search_fields = ['title']

    def get_queryset(self):
        queryset = Document.objects.filter(user=self.request.user).order_by('-created_at')
        category_param = self.request.query_params.get('category')

        if category_param == 'none':
            queryset = queryset.filter(category__isnull=True)
        elif category_param and category_param.isdigit():
            queryset = queryset.filter(category_id=int(category_param))

        return queryset

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

class DocumentDetailView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = DocumentSerializer
    parser_classes = [MultiPartParser, FormParser, JSONParser]

    def get_queryset(self):
        return Document.objects.filter(user=self.request.user)

class ProtectedDocumentFileView(APIView):
    def get(self, request, pk):
        doc = get_object_or_404(Document, pk=pk, user=request.user)
        if not doc.file or not os.path.exists(doc.file.path):
            raise Http404("Archivo PDF no encontrado")
        response = FileResponse(open(doc.file.path, 'rb'), content_type='application/pdf')
        response['Content-Disposition'] = f'inline; filename="{doc.title}.pdf"'
        return response

class RegisterView(generics.CreateAPIView):
    queryset = User.objects.all()
    serializer_class = RegisterSerializer
    permission_classes = [permissions.AllowAny]

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        token, _ = Token.objects.get_or_create(user=user)
        return Response({
            'user': UserSerializer(user).data,
            'token': token.key
        }, status=status.HTTP_201_CREATED)

class LoginView(APIView):
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        username = request.data.get('username')
        password = request.data.get('password')

        user = authenticate(username=username, password=password)
        if user:
            token, _ = Token.objects.get_or_create(user=user)
            return Response({
                'token': token.key,
                'user': UserSerializer(user).data
            })
        return Response({'error': 'Credenciales invalidas'}, status=status.HTTP_401_UNAUTHORIZED)

class LogoutView(APIView):
    def post(self, request):
        request.user.auth_token.delete()
        return Response({'detail': 'Sesion cerrada correctamente.'}, status=status.HTTP_200_OK)

class ProfileView(APIView):
    def get(self, request):
        return Response(UserSerializer(request.user).data)