from .serializers import (
                        CartSerializer,
                        AddToCartSerializer,
                        RemoveFromCartSerializer,
                        CartItemQuantitySerializer,
                        PaymobOrderSerializer,
                        OrderDetailSerializer,
                        OrderListSerializer,
                        OrderSerializer
                        )

from django.conf import settings
import requests
import stripe
from knox.auth import TokenAuthentication
from rest_framework import permissions,status,parsers
from rest_framework.response import Response
from rest_framework.generics import GenericAPIView
from rest_framework.viewsets import ModelViewSet
from rest_framework.decorators import api_view,authentication_classes,permission_classes,parser_classes

from .models import Cart,Order


class CartAPI(GenericAPIView):
    authentication_classes = [TokenAuthentication]
    permission_classes = [permissions.IsAuthenticated]
    def get(self,request):
        try:
            data = Cart.objects.get(profile = request.user)
        except Cart.DoesNotExist:
            data = Cart.objects.create(profile = request.user)
        serializer = CartSerializer(data,context={"request":request})
        return Response(serializer.data,status=200)


class RemoveFromCartAPI(GenericAPIView):
    permission_classes = [permissions.IsAuthenticated,]
    authentication_classes = [TokenAuthentication,]
    serializer_class = RemoveFromCartSerializer
    def get_serializer_context(self):
        context= super().get_serializer_context()
        context.update({"request":self.request})
        return context

    
    def post(self,request):
        data = request.data
        serializer = self.get_serializer(data=data)
        serializer.is_valid(raise_exception=True)
        return Response({"message":"Item Removed From Cart"},status=200)


class ItemQuantityAPI(GenericAPIView):
    permission_classes = [permissions.IsAuthenticated,]
    authentication_classes = [TokenAuthentication,]
    serializer_class = CartItemQuantitySerializer

    def get_serializer_context(self):
        context= super().get_serializer_context()
        context.update({"request":self.request})
        return context


    def post(self,request):
        data = request.data
        serializer = self.get_serializer(data=data)
        serializer.is_valid(raise_exception=True)
        item = serializer.validated_data
        if item.quantity < int(data["quantity"]):
            return Response({"message":f"Sorry, there is only {item.quantity} of this product in stock.","item":serializer.data},
                            status=status.HTTP_202_ACCEPTED)
        return Response({"item":serializer.data},status=200)


class AddToCartAPI(GenericAPIView):
    permission_classes = [permissions.IsAuthenticated]
    authentication_classes = [TokenAuthentication]

    serializer_class = AddToCartSerializer
    def get_serializer_context(self):
        context= super().get_serializer_context()
        context.update({"request":self.request})
        return context

    

    def post(self,request):
        data = request.data
        serializer = self.get_serializer(data=data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response({"cart":serializer.data},status=200)


@api_view(['POST'])
@authentication_classes([TokenAuthentication])
@permission_classes([permissions.IsAuthenticated])
def paymob_payment(request):
    data = request.data
    serializer = PaymobOrderSerializer(data=data,context={"request":request})
    serializer.is_valid(raise_exception=True)
    order_data = serializer.create(serializer.validated_data)
    order  = Order.objects.get(pk=order_data.pk)
    serializer2 = OrderSerializer(order)


    first_response = requests.post('https://accept.paymob.com/api/auth/tokens',
                                    json={"api_key":settings.PAYMOB_SECRET})
    first_json = first_response.json()
    auth_token = first_json["token"]
    items = []
    for item in serializer2.data["items"]:
        items.append({
            "name":str(item.get('product')),
            "amount_cents":int(float(item.get("price"))*100),
            "quantity":item.get('quantity')
        })
    second_data = {
        "auth_token":auth_token,
        "delivery_needed":"false",
        "amount_cents":int(float(serializer2.data["paid_amount"])*100),
        "currency":"EGP",
        "items":items
    }
    second_response = requests.post('https://accept.paymob.com/api/ecommerce/orders',
                                    json=second_data,
                                    headers={'Content-Type':'application/json'})
    second_json = second_response.json()
    order_id= second_json["id"]
    order.order_id = order_id
    order.save()


    third_data = {
        "auth_token": auth_token,
        "amount_cents": int(float(serializer2.data["paid_amount"])*100), 
        "expiration": 3600, 
        "order_id": order_id,
        "billing_data": {
            "apartment": "NA",
            "floor": "NA", 
            "street": "NA", 
            "building": "NA", 
            "city": "NA", 
            "country": "NA",
            "email": serializer2.data["email"], 
            "first_name": serializer2.data["first_name"], 
            "phone_number": serializer2.data["phone"], 
            "last_name": serializer2.data["last_name"], 
        }, 
        "currency": "EGP", 
        "integration_id": 3317273
    }

    third_response = requests.post('https://accept.paymob.com/api/acceptance/payment_keys',
                                    headers={'Content-Type':'application/json'},
                                    json=third_data)
    third_json = third_response.json()
    payment_token = third_json["token"]
    return Response({"payment_token":payment_token},status=200)



class OrderViewset(ModelViewSet):
    permission_classes = [permissions.IsAuthenticated]
    authentication_classes = [TokenAuthentication]

    def get_serializer_class(self):
        if self.action == 'list':
            return OrderListSerializer
        return OrderDetailSerializer
    def get_queryset(self):
        return Order.objects.filter(profile=self.request.user)
    
    def get_object(self):
        return Order.objects.get(profile=self.request.user,order_id=self.kwargs["order_id"])


@api_view(["POST"])
@parser_classes([parsers.JSONParser])
def paymob_callback(request):
    data = request.data
    order = Order.objects.get(order_id=data["obj"]["order"]["id"])
    if data["obj"]["success"] == True:
        order.payment_status = "Success"
    if data["obj"]["is_voided"] == True:
        order.payment_status = "Voided"
        order.status = "Cancelled"
    if data["obj"]["is_refunded"] == True:
        order.payment_status = "Refunded"
        order.status = "Cancelled"
    order.save()
    return Response(status=200)