from django.urls import path
from django.conf.urls.static import static
from django.conf import settings
from  . import views

urlpatterns = [
    path('', views.home ,name= 'index'),
    path("profile/", views.profile, name="profile"),
    path("recipes_page/", views.recipes_page, name="recipes_page"),
    path('Recipe_page/<int:recipe_id>/', views.Recipe_page, name="Recipe_page"),
    path('recipe_page2/<int:recipe_id>/', views.Recipe_information, name= "recipe_page2"),



    ]+static(settings.MEDIA_URL,document_root=settings.MEDIA_ROOT)