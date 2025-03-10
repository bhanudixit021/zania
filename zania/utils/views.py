from __future__ import unicode_literals
from django.shortcuts import render
from rest_framework import serializers
from rest_framework.pagination import PageNumberPagination
from rest_framework.response import Response
import math
from utils.helpers import constants


class CustomSerializer(serializers.ModelSerializer):

    def get_field_names(self, declared_fields, info):
        expanded_fields = super(CustomSerializer, self).get_field_names(declared_fields, info)

        if getattr(self.Meta, 'extra_fields', None):
            return expanded_fields + self.Meta.extra_fields
        else:
            return expanded_fields


class CustomPaginator(PageNumberPagination):
    page = constants.DEFAULT_PAGE
    page_size = constants.DEFAULT_PAGE_SIZE
    page_size_query_param = 'page_size'

    def get_paginated_response(self, data):
        return Response({
            'next': self.get_next_link(),
            'previous': self.get_previous_link(),
            'total': self.page.paginator.count,
            'total_pages': math.ceil(self.page.paginator.count/int(self.request.GET.get('page_size', self.page_size))) if self.page.paginator.count else 0,
            'page': int(self.request.GET.get('page', constants.DEFAULT_PAGE)), # can not set default = self.page
            'page_size': int(self.request.GET.get('page_size', self.page_size)),
            'results': data
        })
