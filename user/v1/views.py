from rest_framework.authtoken.views import ObtainAuthToken
from rest_framework.settings import api_settings
from user.models import Token, User
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from user.permissions import IsAdmin, IsAdminOrSuperAdmin
from rest_framework_simplejwt.views import TokenObtainPairView
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response
from user.v1.serializers import *


class AuthViewSets(viewsets.ModelViewSet):
    queryset = get_user_model().objects.all()
    serializer_class = ListUserSerializer
    http_method_names = ['get', 'post', ]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['email', 'firstname', 'lastname', 'phone', 'role']
    ordering_fields = ['created_at', 'last_login',
                       'email', 'firstname', 'lastname', 'phone']

    def get_queryset(self):
        return super().get_queryset()

    def create(self, request, *args, **kwargs):
        return Response(status=status.HTTP_405_METHOD_NOT_ALLOWED)

    @action(methods=['POST'], detail=False, permission_classes=[IsAuthenticated, IsAdminOrSuperAdmin],
            serializer_class=EligibleUserUploadSerializer,
            url_path='upload-users')
    def upload_user(self, request, pk=None):
        serializer = EligibleUserUploadSerializer(data=request.data, context={'request': request})
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response({'success': True}, status=status.HTTP_200_OK)


class CreateTokenView(ObtainAuthToken):
    """Create a new auth token for user"""
    serializer_class = AuthTokenSerializer
    renderer_classes = api_settings.DEFAULT_RENDERER_CLASSES

    def post(self, request, *args, **kwargs):
        serializer = self.serializer_class(data=request.data,
                                           context={'request': request})
        serializer.is_valid(raise_exception=True)
        user = serializer.validated_data['user']
        try:
            token, created = Token.objects.get_or_create(user=user)
            return Response({
                'token': token.key,
                'created': created,
                'roles': user.roles
            }, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({'message': str(e)}, status.HTTP_500_INTERNAL_SERVER_ERROR)


class CustomObtainTokenPairView(TokenObtainPairView):
    """Login with email and password"""
    serializer_class = TokenObtainPairSerializer
