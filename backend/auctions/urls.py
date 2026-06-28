from rest_framework.routers import DefaultRouter

from .views import AuctionViewSet

router = DefaultRouter()
router.register("", AuctionViewSet, basename="auction")

urlpatterns = router.urls
