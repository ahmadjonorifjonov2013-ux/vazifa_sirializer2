from django.db import models


class Category(models.Model):
    name = models.CharField(max_length=100, unique=True)
    city = models.CharField(max_length=100)

    def __str__(self):
        return self.name


class Product(models.Model):
    category = models.ForeignKey(
        Category, on_delete=models.CASCADE, related_name="products"
    )
    title = models.CharField(max_length=150)
    price = models.IntegerField()
    sale_price = models.IntegerField()
    year = models.IntegerField()
    secret_code = models.CharField(max_length=50, blank=True, null=True)
    created = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title
