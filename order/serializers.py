from .models import Cart,CartItem,Order,OrderItem
from rest_framework import serializers
from user.models import Profile
from product.models import Product
from product.serializers import ProductListSerializer

class OrderItemSerializer(serializers.ModelSerializer):
    product = serializers.SlugRelatedField('title',read_only=True)
    class Meta:
        model = OrderItem
        fields = (
            'price',
            'product',
            'quantity',
        )

class OrderSerializer(serializers.ModelSerializer):
    items = OrderItemSerializer(many=True)

    class Meta:
        model = Order
        fields = (
            'order_id',
            'first_name',
            'last_name',
            'email',
            'phone',
            'paid_amount',
            'items'
        )


class StripeOrderSerializer(serializers.ModelSerializer):
    items = OrderItemSerializer(many=True)
    class Meta:
        model = Order
        fields = (
            'first_name',
            'last_name',
            'email',
            'address',
            'zipcode',
            'place',
            'phone',
            'stripe_token',
            'items'
        )

    def create(self, validated_data):
        profile = self.context["request"].user
        items_data = validated_data.pop('items')
        order = Order.objects.create(profile=profile,payment_choice='stripe',**validated_data)

        for item_data in items_data:    
            OrderItem.objects.create(order=order,**item_data)
        
        return order



class PaymobOrderSerializer(serializers.ModelSerializer):
    class Meta:
        model = Order
        fields = (
            'first_name',
            'last_name',
            'email',
            'address',
            'zipcode',
            'place',
            'phone',
        )

    def create(self, validated_data):
        profile = self.context["request"].user
        items_data = Cart.objects.get(profile=profile).items.all()
        if len(items_data)<=0:
            raise serializers.ValidationError("Cart is empty.")
        order = Order.objects.create(profile=profile,status='Pending',payment_choice='paymob',**validated_data)
        paid_amount = 0
        errors=[]
        items = []
        for item_data in items_data:   
            product = Product.objects.get(id = item_data.product.id) 
            if product.in_stock == 0:
                errors.append(f"Sorry, We're out of {product.title} products. Please try again later")
            item =  OrderItem.objects.create(order=order,product=item_data.product,price=item_data.product.price*item_data.quantity,quantity=item_data.quantity)
            if item.quantity < item_data.quantity:
                errors.append(f'Sorry we only have {item.quantity} of {item.product.title} left. Please change the quantity in the cart before Procceding to checkout.')
            paid_amount+=item.price
            items.append(item)
        if len(errors)>0:
            order.delete()
            raise serializers.ValidationError(errors)
        for item in items:
            product = Product.objects.get(id = item.product.id)
            product.in_stock -= item.quantity
            product.save()
        order.paid_amount = paid_amount
        order.save()
        items_data.delete()
        return order



class AddToCartSerializer(serializers.Serializer):
    product = serializers.CharField()
    quantity = serializers.IntegerField()

    def create(self, validated_data):
        user = Profile.objects.get(pk=self.context["request"].user.pk)
        print(user)
        try:
            cart = Cart.objects.get(profile=user)
        except Cart.DoesNotExist:
            cart = Cart.objects.create(profile=user)
        print(cart)
        product = Product.objects.get(title=validated_data.pop("product"))
        try:
            item = CartItem.objects.get(cart=cart,product=product)
            if (item.quantity+validated_data["quantity"])>=product.in_stock:
                item.quantity = product.in_stock
            else:
                item.quantity += validated_data["quantity"]
            item.save()
        except CartItem.DoesNotExist:
            item = CartItem(cart=cart,product=product,quantity = validated_data["quantity"])
            item.save()
        return cart


class RemoveFromCartSerializer(serializers.Serializer):
    product = serializers.CharField()

    def validate(self, data):
        cart = Cart.objects.get(profile=self.context["request"].user)
        try:
            item = CartItem.objects.get(cart = cart, product__title = data["product"])
            item.delete()
            return cart
        except CartItem.DoesNotExist:
            raise serializers.ValidationError("Item is not in cart")


class CartItemQuantitySerializer(serializers.Serializer):
    product = serializers.CharField()
    quantity = serializers.IntegerField()

    def validate(self, attrs):
        cart = Cart.objects.get(profile=self.context["request"].user)
        try:
            product = Product.objects.get(title = attrs["product"])
        except Product.DoesNotExist:
            raise serializers.ValidationError("Product does not exist.")
        try:
            item = CartItem.objects.get(cart = cart, product=product)
            if (attrs["quantity"])>=product.in_stock:
                item.quantity = product.in_stock
            else:
                item.quantity = attrs["quantity"]
            item.save()
            return item
        except CartItem.DoesNotExist:
            raise serializers.ValidationError("Item is not in cart")


class CartItemSerializer(serializers.ModelSerializer):
    product = ProductListSerializer()
    class Meta:
        model = CartItem
        fields = (
            'quantity',
            'product'
        )

class CartSerializer(serializers.ModelSerializer):
    number_of_items = serializers.SerializerMethodField()
    total_price = serializers.SerializerMethodField()
    items = CartItemSerializer(many=True)

    def get_number_of_items(self,obj):
        number = 0
        for item in obj.items.all():
            number += item.quantity
        return number
    
    def get_total_price(self,obj):
        price = 0
        for item in obj.items.all():
            price += item.quantity*item.product.price
        return price
    class Meta:
        model = Cart
        fields = (
            'number_of_items',
            'total_price',
            'items',
        )