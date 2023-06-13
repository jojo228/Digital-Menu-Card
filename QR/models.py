from django.db import models
from .helpers import generate_slug

# Create your models here.


class Store(models.Model):
    name = models.CharField(max_length=30)
    slug = models.SlugField(max_length=300, unique=True)

    def __str__(self):
        return self.name
    
    def save(self , *args, **kwargs): 
        self.slug = generate_slug(self.name)
        super(Store, self).save(*args, **kwargs)


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
    

    def __str__(self):
        return f"Order #{self.id}"
    

class OrderItem(models.Model):
    table = models.ForeignKey(Table, on_delete=models.CASCADE, related_name='items')
    name = models.CharField(max_length=20, null=True)
    price = models.CharField(max_length=100,null=True,blank=True)
    quantity = models.PositiveIntegerField(default=1)

    def __str__(self):
        return str(self.id)
