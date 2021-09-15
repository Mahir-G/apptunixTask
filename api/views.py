from rest_framework.views import APIView
from django.http.response import JsonResponse
from rest_framework.response import Response
from rest_framework import status
from .serializers import UserSerializer, FoodItemSerializer, OrdersSerializer
from rest_framework.permissions import IsAuthenticated

from rest_framework.authtoken.models import Token
from .models import FoodItem, CartItems, Orders
import json


class UserCreate(APIView):
    """
    Creates a new user.
    """

    @staticmethod
    def post(request):
        serializer = UserSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            if user:
                token = Token.objects.create(user=user)
                json = serializer.data
                json['token'] = token.key
                return Response(json, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class FoodCreate(APIView):
    """
    Creates a new food item and gets list of food items
    """

    permission_classes = (IsAuthenticated,)

    @staticmethod
    def get(request):
        foodList = FoodItem.objects.filter(user=request.user)
        serialized_list = FoodItemSerializer(foodList, many=True)
        return JsonResponse(serialized_list.data, safe=False, status=status.HTTP_201_CREATED)

    @staticmethod
    def post(request):
        foodItem = FoodItemSerializer(data=request.data)
        if foodItem.is_valid():
            foodItem.validated_data["user_id"] = request.user.id
            foodItem.save()
            return JsonResponse(foodItem.data, status=status.HTTP_201_CREATED)
        return JsonResponse(foodItem.errors, status=status.HTTP_400_BAD_REQUEST)


class FoodItemUpdate(APIView):
    """
    Edit a specific food item
    View a specific food item
    Delete a specific food item
    """

    permission_classes = (IsAuthenticated,)

    @staticmethod
    def get(request, foodId):
        try:
            foodItem = FoodItem.objects.get(user=request.user, id=foodId)
        except:
            foodItem = None
        if foodItem:
            serialized_list = FoodItemSerializer(foodItem)
            return JsonResponse(serialized_list.data, status=status.HTTP_200_OK)
        return JsonResponse({"message": "No food item exists with this id"}, status=status.HTTP_404_NOT_FOUND)

    @staticmethod
    def post(request, foodId):
        try:
            foodItem = FoodItem.objects.get(user=request.user, id=foodId)
        except:
            foodItem = None
        if foodItem:
            data = json.loads(request.body)
            if data.get('cost'):
                foodItem.cost = data.get('cost')
            if data.get('name'):
                foodItem.name = data.get('name')
            foodItem.save()
            foodItem = FoodItemSerializer(foodItem)
            return JsonResponse(foodItem.data, status=status.HTTP_201_CREATED)
        return JsonResponse({"message": "No food item exists with this id"}, status=status.HTTP_404_NOT_FOUND)

    @staticmethod
    def delete(request, foodId):
        try:
            foodItem = FoodItem.objects.get(user=request.user, id=foodId)
        except:
            foodItem = None
        if foodItem:
            foodItem.delete()
            return JsonResponse({"message": "successfully deleted"}, status=status.HTTP_200_OK)
        return JsonResponse({"message": "No food item exists with this id"}, status=status.HTTP_404_NOT_FOUND)


class CartView(APIView):
    """
    Get cart of a user
    Add item to cart of a user
    """

    permission_classes = (IsAuthenticated,)

    @staticmethod
    def get(request):
        data = FoodItem.objects.filter(cartitems__user=request.user)
        foodItems = FoodItemSerializer(data, many=True)
        return JsonResponse(foodItems.data, safe=False, status=status.HTTP_200_OK)

    @staticmethod
    def post(request):
        data = json.loads(request.body)
        if data.get('foodItemId'):
            try:
                foodItem = FoodItem.objects.get(id=data.get('foodItemId'))
            except:
                foodItem = None
            if foodItem:
                cartItem = CartItems(user=request.user, item=foodItem)
                cartItem.save()
                return JsonResponse({'message': 'Item added to cart'}, status=status.HTTP_201_CREATED)
            return JsonResponse({'message': 'No food item exists with this id'}, status=status.HTTP_404_NOT_FOUND)
        return JsonResponse({'message': 'send foodItemId in body'}, status=status.HTTP_400_BAD_REQUEST)


class OrdersView(APIView):
    """
    Get orders of a user
    Create an order of a user
    """

    permission_classes = (IsAuthenticated,)

    @staticmethod
    def get(request):
        data = Orders.objects.filter(user=request.user)
        if request.GET.get('delivered'):
            data = Orders.objects.filter(user=request.user, delivered=json.loads(request.GET.get('delivered')))
        if request.GET.get('page'):
            page = json.loads(request.GET.get('page'))
            if page < 1:
                page = 1
            size = 10
            data = data[(page-1)*size: page*size]
        orderItems = OrdersSerializer(data, many=True)
        return JsonResponse(orderItems.data, safe=False, status=status.HTTP_200_OK)

    @staticmethod
    def post(request):
        itemsList = FoodItem.objects.filter(cartitems__user=request.user)
        cartItems = CartItems.objects.filter(user=request.user)
        order = Orders(user=request.user, delivered=False)
        order.save()
        order.items.add(*itemsList)
        cartItems.delete()
        orderData = OrdersSerializer(order)
        return JsonResponse(orderData.data, status=status.HTTP_200_OK)


class RateView(APIView):
    """
    rate a specific order
    """

    permission_classes = (IsAuthenticated,)

    @staticmethod
    def post(request):
        data = json.loads(request.body)
        if 'orderId' in data and 'rating' in data:
            order = Orders.objects.get(id=data.get('orderId'))
            if order.user == request.user:
                order.rating = data.get('rating')
                order.save()
                orderData = OrdersSerializer(order)
                return JsonResponse(orderData.data, status=status.HTTP_200_OK)
            return JsonResponse({"message": "not authorized to rate this order"}, status=status.HTTP_401_UNAUTHORIZED)
        return JsonResponse({"message": "invalid body sent"}, status=status.HTTP_400_BAD_REQUEST)


class ChangeStatusView(APIView):
    """
    change status of order
    """

    permission_classes = (IsAuthenticated,)

    @staticmethod
    def post(request):
        data = json.loads(request.body)
        if 'orderId' in data:
            order = Orders.objects.get(id=data.get('orderId'))
            if order.user == request.user:
                order.delivered = True
                order.save()
                orderData = OrdersSerializer(order)
                return JsonResponse(orderData.data, status=status.HTTP_200_OK)
            return JsonResponse({"message": "not authorized to update this order status"},
                                status=status.HTTP_401_UNAUTHORIZED)
        return JsonResponse({"message": "invalid orderId sent"}, status=status.HTTP_400_BAD_REQUEST)
