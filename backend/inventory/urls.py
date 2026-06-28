from rest_framework.routers import DefaultRouter

from .views import CardCopyViewSet

router = DefaultRouter()
router.register("", CardCopyViewSet, basename="cardcopy")

urlpatterns = router.urls
