from django.urls import path
from . import views

app_name = 'quotations'
urlpatterns = [
    path('<int:quotation_id>/', views.view_quotation, name='view_quotation'),
    path('<int:event_id>/create_quotation/', views.create_quotation, name='create_quotation'),
    path('<int:quotation_id>/confirm/', views.confirm_quotation,
         name='confirm_quotation'),
    path('<int:quotation_id>/accept/', views.accept_quotation, name='accept_quotation'),
    path('<int:quotation_id>/submit_payment/', views.submit_payment,
         name='submit_payment'),
    path('<int:quotation_id>/mark_as_paid/', views.mark_as_paid, name='mark_as_paid'),
]
