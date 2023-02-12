from django.db import models
from user.models import Profile
from product.models import Product
from django.core.validators import MaxValueValidator, MinValueValidator
from django.core.exceptions import ValidationError
from django_extensions.db.models import TimeStampedModel
# Create your models here.


class Cart(models.Model):
    profile = models.OneToOneField(Profile,related_name='cart',on_delete=models.CASCADE)

    def __str__(self):
        return self.profile.username



class CartItem(models.Model):
    cart = models.ForeignKey(Cart,related_name='items',on_delete=models.CASCADE)
    product = models.ForeignKey(Product,on_delete=models.CASCADE)
    quantity = models.IntegerField()

    def save(self, *args, **kwargs):
        if self.quantity > self.product.in_stock:
            self.quantity = self.product.in_stock
        return super().save(*args, **kwargs)


class Order(TimeStampedModel,models.Model):
    payment_choices = [
        ('paymob','paymob'),
        ('stripe','stripe'),
    ]
    payment_status_choices = [
        ('Pending','Pending'),
        ('Success','Success'),
        ('Voided','Voided'),
        ('Refunded','Refunded')
    ]
    order_id = models.CharField(max_length=100,null=True,blank=True)
    profile = models.ForeignKey(Profile,related_name='orders',on_delete=models.CASCADE)
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    email = models.CharField(max_length=100)
    address = models.CharField(max_length=100)
    zipcode = models.CharField(max_length=100)
    place = models.CharField(max_length=100)
    phone = models.CharField(max_length=100)
    created_at = models.DateTimeField(auto_now_add=True)
    payment_status = models.CharField(choices=payment_status_choices,default="Pending",max_length=10)
    status = models.CharField(choices=[("Pending","Pending"),("Success","Success"),("Cancelled","Cancelled")],default="Pending",max_length=10)
    paid_amount = models.DecimalField(max_digits=8,decimal_places=2,blank=True,null=True)
    payment_choice = models.CharField(choices=payment_choices,max_length=6)
    stripe_token = models.CharField(max_length=100,null=True)

    class Meta:
        ordering = (
            '-created_at',
        )
    def __str__(self):
        return self.first_name


class OrderItem(models.Model):
    order = models.ForeignKey(Order,related_name='items',on_delete=models.CASCADE)
    product = models.ForeignKey(Product,related_name='items',on_delete=models.CASCADE,unique=False)
    price = models.DecimalField(max_digits=8,decimal_places=2)
    quantity = models.IntegerField(default=1)


    def __str__(self):
        return '%s' % self.id
    

            

    def save(self, *args, **kwargs):
        if self.quantity > self.product.in_stock:
            self.quantity = self.product.in_stock
        return super().save(*args, **kwargs)
    