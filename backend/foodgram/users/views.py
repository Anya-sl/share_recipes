from djoser.views import UserViewSet
from rest_framework import status
from rest_framework.decorators import action
from rest_framework.generics import get_object_or_404
from rest_framework.pagination import PageNumberPagination
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from .models import Subscription, User
from .serializers import SubscribeSerializer, SubscriptionSerializer


class UserViewSet(UserViewSet):
    """Отображение действий с пользователями."""

    queryset = User.objects.all()
    pagination_class = PageNumberPagination

    @action(
        detail=False,
        permission_classes=(IsAuthenticated,),
    )
    def subscriptions(self, request):
        """Получить список подписок текущего пользователя."""
        user = get_object_or_404(
            User,
            id=request.user.id
        )
        queryset = User.objects.filter(following__user=user)
        serializer = SubscriptionSerializer(
            queryset,
            many=True,
            context={'request': request}
        )
        return Response(serializer.data)

    @action(
        detail=True,
        methods=['POST', 'DELETE'],
        permission_classes=(IsAuthenticated,),
    )
    def subscribe(self, request, id):
        user = request.user
        following = get_object_or_404(User, id=id)
        if request.method == 'POST':
            serializer = SubscribeSerializer(
                data={'user': user.id, 'following': id},
                context={'request': request},
            )
            serializer.is_valid(raise_exception=True)
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        follow = get_object_or_404(
            Subscription,
            user=user,
            following=following,
        )
        follow.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
