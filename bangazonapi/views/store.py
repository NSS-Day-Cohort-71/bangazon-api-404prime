from rest_framework import viewsets, status
from rest_framework.response import Response
from rest_framework import serializers, permissions
from bangazonapi.models import Store, Customer
from django.contrib.auth.models import User
from .user import UserSerializer


class StoreSerializer(serializers.ModelSerializer):
    seller = UserSerializer(source='seller.user')

    class Meta:
        model = Store
        fields = ['id', 'name', 'description', 'seller', 'items_for_sale']


class StoreViewSet(viewsets.ModelViewSet):
    queryset = Store.objects.all()
    serializer_class = StoreSerializer

    pagination_class = None

    def create(self, request):
        new_store = Store()
        new_store.name = request.data['name']
        new_store.description = request.data['description']
        seller = Customer.objects.get(user=request.auth.user)
        new_store.seller = seller
        new_store.save()

        serializer = self.get_serializer(new_store)

        return Response(serializer.data, status=status.HTTP_201_CREATED)
