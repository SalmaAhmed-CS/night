from django.contrib import admin
from import_export.admin import ImportExportModelAdmin

# Register your models here.
from django.contrib import admin
from .models import Ingredients
from .models import recipes
from .models import Rating, Preferences,steps
# Register your models here.
#admin.site.register(Ingredients)
#admin.site.register(recipes)
admin.site.register(Rating)
admin.site.register(Preferences)

@admin.register(recipes)
class recipesAdmin (ImportExportModelAdmin):
    pass

@admin.register(Ingredients)
class recipesAdmin (ImportExportModelAdmin):
    pass

@admin.register(steps)
class recipesAdmin (ImportExportModelAdmin):
    pass
