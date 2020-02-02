# 3rd Party
from django.http import HttpResponse
from rest_framework import viewsets, mixins
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework.status import HTTP_201_CREATED, HTTP_400_BAD_REQUEST

# Internal
from .upload_serializers import RecordsFileUploadSerializer
# from .serializers import TotalsSerializer
from .models import RecordsFile


# @api_view(['GET'])
# def totals(request):
#     data = TotalsFile.objects.all()
#     serializer = TotalsSerializer(data, many=True)
#     return Response(serializer.data)


class RecordsFileUpload(viewsets.ModelViewSet, mixins.CreateModelMixin):
    queryset = RecordsFile.objects.all()

    def get_serializer(self, *args, **kwargs):
        serializer_class = RecordsFileUploadSerializer
        kwargs['context'] = self.get_serializer_context()
        return serializer_class(*args, **kwargs)

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        try:
            self.perform_create(serializer)
        except Exception as e:
            return Response(serializer.data, status=HTTP_400_BAD_REQUEST)
        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data, status=HTTP_201_CREATED, headers=headers)

