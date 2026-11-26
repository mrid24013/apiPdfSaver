from rest_framework import serializers
from django.contrib.auth.models import User
from .models import Document

from rest_framework import serializers
from rest_framework.validators import UniqueValidator
from django.contrib.auth.models import User

from rest_framework import serializers
from django.urls import reverse
from .models import Document, Category

class CategorySerializer(serializers.ModelSerializer):
    document_count = serializers.IntegerField(source='documents.count', read_only=True)

    class Meta:
        model = Category
        fields = ['id', 'name', 'color', 'document_count', 'created_at']
        read_only_fields = ['id', 'document_count', 'created_at']

    def validate_name(self, value):
        user = self.context['request'].user
        qs = Category.objects.filter(user=user, name__iexact=value.strip())
        if self.instance:
            qs = qs.exclude(pk=self.instance.pk)
        if qs.exists():
            raise serializers.ValidationError("Ya tienes una categoría con este nombre.")
        return value.strip()


class DocumentSerializer(serializers.ModelSerializer):
    protected_file_url = serializers.SerializerMethodField()
    file_size_kb = serializers.SerializerMethodField()
    category_detail = CategorySerializer(source='category', read_only=True)

    class Meta:
        model = Document
        fields = [
            'id',
            'title',
            'category',
            'category_detail',
            'file',
            'protected_file_url',
            'file_size_kb',
            'page_count',
            'created_at',
            'updated_at',
        ]
        read_only_fields = ['id', 'protected_file_url', 'file_size_kb', 'created_at', 'updated_at']
        extra_kwargs = {
            'file': {'write_only': True}
        }

    def validate_category(self, value):
        if value and value.user != self.context['request'].user:
            raise serializers.ValidationError("Categoría no válida.")
        return value

    def validate_file(self, value):
        if not value.name.lower().endswith('.pdf'):
            raise serializers.ValidationError("Solo se permiten archivos en formato PDF.")
        if value.size > 15 * 1024 * 1024:
            raise serializers.ValidationError("El archivo PDF no debe superar los 15 MB.")
        return value

    def get_protected_file_url(self, obj):
        request = self.context.get('request')
        if request:
            url = reverse('document-file', kwargs={'pk': obj.pk})
            return request.build_absolute_uri(url)
        return None

    def get_file_size_kb(self, obj):
        if obj.file and obj.file.size:
            return round(obj.file.size / 1024, 1)
        return 0

class RegisterSerializer(serializers.ModelSerializer):
    email = serializers.EmailField(
        required=True,
        validators=[UniqueValidator(queryset=User.objects.all(), message="Este correo ya está registrado.")]
    )
    password = serializers.CharField(write_only=True, min_length=6)
    first_name = serializers.CharField(required=False, allow_blank=True)
    last_name = serializers.CharField(required=False, allow_blank=True)

    class Meta:
        model = User
        fields = ['username', 'email', 'password', 'first_name', 'last_name']

    def create(self, validated_data):
        user = User.objects.create_user(
            username=validated_data['username'],
            email=validated_data['email'],
            password=validated_data['password'],
            first_name=validated_data.get('first_name', ''),
            last_name=validated_data.get('last_name', '')
        )
        return user

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'first_name', 'last_name']

class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, min_length=6)

    class Meta:
        model = User
        fields = ['username', 'email', 'password', 'first_name', 'last_name']

    def create(self, validated_data):
        user = User.objects.create_user(
            username=validated_data['username'],
            email=validated_data.get('email', ''),
            password=validated_data['password'],
            first_name=validated_data.get('first_name', ''),
            last_name=validated_data.get('last_name', '')
        )
        return user

class DocumentSerializer(serializers.ModelSerializer):
    file_url = serializers.SerializerMethodField()

    class Meta:
        model = Document
        fields = ['id', 'title', 'file', 'file_url', 'created_at']
        read_only_fields = ['id', 'file_url', 'created_at']

    def get_file_url(self, obj):
        request = self.context.get('request')
        if obj.file and request:
            return request.build_absolute_uri(obj.file.url)
        return None