from django.urls import path



from . import views

urlpatterns = [path('',views.index,name='index'),
               path('view/<int:page>', views.viewComplaints, name='view'),
               path('getcomp/<int:id>', views.getComplaint, name='getcomp'),
               path('create', views.crComplaint, name='create'),
               path('update/<int:id>', views.updComplaint, name='update'),
               path('delete/<int:id>', views.delComplaint, name='delete'),
               path('suggest', views.complaintHelp, name='suggest'),
               ]
