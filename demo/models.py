from django.db import models
from django.conf import settings
from django.shortcuts import reverse
from django_countries.fields import CountryField
from django_countries.widgets import CountrySelectWidget


# Create your models here.
CATEGORY_CHOICES=(
    ('M','Male'),
    ('F','Female'),
    ('K','Kids')
)
LABEL_CHOICES=(
    ('P','primary'),
    ('S','secondary'),
    ('D','danger')
)
ADDRESS_CHOICES = (
    ('B', 'Billing'),
    ('S', 'Shipping'),
)

class Product(models.Model):
    title=models.CharField(max_length=100)
    price= models.FloatField()
    discount_price= models.FloatField(blank=True, null=True)
    category=models.CharField(choices=CATEGORY_CHOICES,max_length=2)
    label=models.CharField(choices=LABEL_CHOICES,max_length=1)
    description=models.TextField()
    slug=models.SlugField()
    image=models.ImageField()

    def __str__(self):
        return self.title
    
    def get_to_cart_url(self):
        return reverse("product",kwargs={
            'slug':self.slug 
        })

    
    

class Cart(models.Model):
    user=models.ForeignKey(settings.AUTH_USER_MODEL,on_delete=models.CASCADE)
    ordered = models.BooleanField(default=False)   
    item= models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity= models.IntegerField(default=1)

    def __str__(self):
        return f"{self.quantity} of {self.item.title}"

    
    def get_total_item_price(self):
        return self.quantity * self.item.price

    def get_total_discount_item_price(self):
        return self.quantity * self.item.discount_price

    def get_amount_saved(self):
        return self.get_total_item_price() - self.get_total_discount_item_price()

    def get_final_price(self):
        if self.item.discount_price:
            return self.get_total_discount_item_price()
        return self.get_total_item_price()



class Order(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL,on_delete=models.CASCADE)
    items = models.ManyToManyField(Cart)
    start_date=models.DateTimeField(auto_now_add=True)
    orderd_date=models.DateTimeField()
    ordered = models.BooleanField(default=False)
    billing_address=models.ForeignKey('Address',on_delete=models.SET_NULL, blank=True, null= True)
    payment=models.ForeignKey('Payment',on_delete=models.SET_NULL, blank=True, null= True)

    def __str__(self):
        return self.user.username
    
class Address(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL,
                             on_delete=models.CASCADE)
    shipping_address = models.CharField(max_length=100)
    shipping_address2 = models.CharField(max_length=100,blank=True,null=True)
    shipping_country = CountryField(multiple=False,blank=True,null=True)
    shipping_zip= models.CharField(max_length=100)
    # address_type = models.CharField(max_length=1, choices=ADDRESS_CHOICES)
    # default = models.BooleanField(default=False)

    def __str__(self):
        return self.user.username

    # class Meta:
    #     verbose_name_plural = 'Addresses'  
     
class Payment(models.Model):
    stripe_charge_id = models.CharField(max_length=50)
    user = models.ForeignKey(settings.AUTH_USER_MODEL,
                             on_delete=models.SET_NULL, blank=True, null=True)
    amount = models.FloatField()
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.user.username




