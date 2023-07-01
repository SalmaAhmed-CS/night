from django.db import models
from django.contrib.auth.models import User



class Ingredients(models.Model):
    name = models.CharField(max_length=50, unique=True)
    ing1 = models.CharField(max_length=20 , unique=False)
    ing2 = models.CharField(max_length=20, unique=False)
    ing3 = models.CharField(max_length=20, unique=False)
    ing4 = models.CharField(max_length=20, unique=False)
    ing5 = models.CharField(max_length=20, unique=False)
    ing6 = models.CharField(max_length=20, unique=False)
    ing7 = models.CharField(max_length=20, unique=False)
    ing8 = models.CharField(max_length=20, unique=False)
    ing9 = models.CharField(max_length=20, unique=False)
    ing10 = models.CharField(max_length=20, unique=False)
    ing11 = models.CharField(max_length=20, unique=False)
    ing12 = models.CharField(max_length=20, unique=False)
    ing13 = models.CharField(max_length=20, unique=False)
    ing14 = models.CharField(max_length=20, unique=False)
    ing15 = models.CharField(max_length=20, unique=False)
    ing16 = models.CharField(max_length=20, unique=False)
class steps(models.Model):
    name = models.CharField(max_length=50, unique=True)
    step1 = models.CharField(max_length=20 , unique=False)
    step2 = models.CharField(max_length=20, unique=False)
    step3 = models.CharField(max_length=20, unique=False)
    step4 = models.CharField(max_length=20, unique=False)
    step5 = models.CharField(max_length=20, unique=False)
    step6 = models.CharField(max_length=20, unique=False)
    step7 = models.CharField(max_length=20, unique=False)
    step8 = models.CharField(max_length=20, unique=False)
    step9 = models.CharField(max_length=20, unique=False)
    step10 = models.CharField(max_length=20, unique=False)
    step11 = models.CharField(max_length=20, unique=False)
    step12 = models.CharField(max_length=20, unique=False)
    step13 = models.CharField(max_length=20, unique=False)
    step14 = models.CharField(max_length=20, unique=False)
    step15 = models.CharField(max_length=20, unique=False)
    step16 = models.CharField(max_length=20, unique=False)


class recipes(models.Model):
    name = models.CharField(max_length=50, unique=True)
    image = models.ImageField(upload_to="recipes_image")
    sections = models.CharField(max_length=70)
    description = models.CharField(max_length=1000)
    Ingredients_id = models.ForeignKey(Ingredients, related_name="Ingredients", on_delete=models.CASCADE)
    Ingredients = models.CharField(max_length=1000)
    recipesduration = models.CharField(max_length=70)
    def __str__(self):
        return str(self.pk)


class Rating(models.Model):
    user=models.ForeignKey(User,on_delete=models.CASCADE,default=None)
    recipe=models.ForeignKey(recipes,on_delete=models.CASCADE,default=None)
    rating=models.CharField(max_length=70)
    rated_date=models.DateTimeField(auto_now_add=True)

class Preferences(models.Model):
    user =models.OneToOneField(User,null=True , on_delete=models.CASCADE,)
    type = models.CharField(max_length=70)
    allergy = models.CharField(max_length=70)
    def __str__(self):
        return str(self.user)






