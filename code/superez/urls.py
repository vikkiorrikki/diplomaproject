from django.conf.urls import url
from django.urls import path
from django.conf.urls.static import static
from django.conf import settings

import os
from . import views

urlpatterns = [
    url(r'^$', views.index, name='index'),
    path('list/', views.list, name='list')
] + static('images/', document_root=os.path.join(settings.BASE_DIR, "superez", "images"))