# -*- coding: UTF-8 -*-
from django.contrib import admin
from .models import Title, Rank, Country, Locality, Address, OrganizationalUnit, Department, Service


admin.site.register(Title)
admin.site.register(Rank)
admin.site.register(Country)
admin.site.register(Locality)
admin.site.register(Address)
admin.site.register(OrganizationalUnit)
admin.site.register(Department)
admin.site.register(Service)
