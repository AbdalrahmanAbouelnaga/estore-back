from django.db import models
from django_extensions.db.models import AutoSlugField,TimeStampedModel
from django.core.files import File
from PIL import Image
from io import BytesIO
from uuid import uuid4
from django.core.validators import MaxValueValidator, MinValueValidator

# Create your models here.



class Category(models.Model):
    title = models.CharField(max_length=150,unique=True)
    slug = AutoSlugField(populate_from=['title'])
    def __str__(self):
        return self.title
    class Meta:
        verbose_name_plural='Categories'

class SubCategory(models.Model):
    title = models.CharField(max_length=150)
    slug = AutoSlugField(populate_from=['title'])
    category = models.ForeignKey(Category,related_name='sub_categories',on_delete=models.CASCADE)
    def __str__(self):
        return self.title
    class Meta:
        verbose_name_plural='Sub Categories'

class Product(TimeStampedModel,models.Model):
    id = models.UUIDField(default=uuid4,primary_key=True,editable=False)
    title = models.CharField(max_length=150)
    slug = AutoSlugField(populate_from=['title'])
    in_stock = models.IntegerField(validators=[MinValueValidator(0)])
    price = models.DecimalField(max_digits=6,decimal_places=2)
    sub_category = models.ForeignKey(SubCategory,related_name='products',on_delete=models.CASCADE)


    def __str__(self):
        return self.title


class ProductSpec(models.Model):
    product = models.ForeignKey(Product,related_name='specs',on_delete=models.CASCADE)
    title = models.CharField(max_length=50)
    desc = models.CharField(max_length=150)



class ProductImages(models.Model):
    product = models.ForeignKey(Product,related_name='images',on_delete=models.CASCADE)
    image = models.ImageField(upload_to='uploads/',null=True,blank=True)
    thumbnail = models.ImageField(upload_to='uploads/',null=True,blank=True)


    def make_thumbnail(self,size=(300,200)):
        img = Image.open(self.image)
        img.convert('RGB')
        img.thumbnail(size)

        thumb_io = BytesIO()
        img.save(thumb_io,'JPEG',quality=90,optimize=True)

        thumbnail = File(thumb_io,name=self.image.name)
        self.thumbnail = thumbnail



    def save(self,*args):
        if self.image.url:
            if not self.thumbnail:
                self.make_thumbnail()
        return super().save(args)