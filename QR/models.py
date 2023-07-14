from django.utils import timezone
from django.db import models
from .helpers import generate_slug

# Create your models here.

MEMBERSHIP_CHOICES = [
        ('B', 'Basic'),
        ('P', 'Premium'),
        ('V', 'VIP'),
    ]


class Store(models.Model):
    name = models.CharField(max_length=30)
    slug = models.SlugField(max_length=300, unique=True)
    membership = models.CharField(max_length=1, choices=MEMBERSHIP_CHOICES, default='B')
    subscription = models.OneToOneField('Subscription', on_delete=models.SET_NULL, null=True, blank=True, related_name='store_subscription')

    def __str__(self):
        return f"{self.name} - {self.membership}"
    
    def save(self , *args, **kwargs): 
        self.slug = generate_slug(self.name)
        super(Store, self).save(*args, **kwargs)

    def is_active(self):
        if self.subscription and self.subscription.end_date >= timezone.now().date():
            return True
        return False


class Table(models.Model):
    store = models.ForeignKey(Store, on_delete=models.CASCADE)
    table_no = models.IntegerField()

    def __str__(self):
        return f"{self.store.name} - {self.table_no}"
    

class Item(models.Model):
    store = models.ManyToManyField(Store)
    name = models.CharField(max_length=30)
    price = models.IntegerField()
    image = models.ImageField(null=True, blank=True)
    categorie = models.CharField(max_length=30)
    description = models.TextField()

    def __str__(self):
        return self.name

    @property
    def imageURL(self):
        try:
            url = self.image.url
        except:
            url = ''
        return url
    

class OrderItem(models.Model):
    table = models.ForeignKey(Table, on_delete=models.CASCADE, related_name='items')
    name = models.CharField(max_length=100, null=True)
    price = models.CharField(max_length=100,null=True,blank=True)
    quantity = models.PositiveIntegerField(default=1)
    total_amount = models.DecimalField(max_digits=10, decimal_places=0)


    def save(self, *args, **kwargs):
        self.total_amount = int(self.price) * int(self.quantity)
        super().save(*args, **kwargs)

    def __str__(self):
        return str(self.id)


class Subscription(models.Model):
    store = models.ForeignKey(Store, on_delete=models.CASCADE, related_name='store_subscription')
    start_date = models.DateField()
    end_date = models.DateField()

    def __str__(self):
        return f"Subscription #{self.id} - {self.store.name}"