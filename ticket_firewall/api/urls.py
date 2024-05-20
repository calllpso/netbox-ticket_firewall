from netbox.api.routers import NetBoxRouter
from . import views

app_name = 'ticket_firewall'

router = NetBoxRouter()
router.register('tickets', views.TicketViewSet)
router.register('rules', views.RuleViewSet)
urlpatterns = router.urls
