from rest_framework.routers import DefaultRouter

from .views import CategoryViewSet, ProductViewSet

router = DefaultRouter()
router.register(r"categories", CategoryViewSet, basename="category")
router.register(r"products", ProductViewSet, basename="product")

urlpatterns = router.urls

# Loyihaning asosiy urls.py fayliga qo'shing:
#
# from django.urls import path, include
#
# urlpatterns = [
#     path("admin/", admin.site.urls),
#     path("api/", include("catalog.urls")),
# ]
