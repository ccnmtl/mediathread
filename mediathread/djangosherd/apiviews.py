from django.shortcuts import get_object_or_404
from rest_framework import status
from rest_framework.generics import CreateAPIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from mediathread.assetmgr.models import Asset
from mediathread.djangosherd.serializers import SherdNoteSerializer
from mediathread.djangosherd.permissions import AssetIsVisible, AssetInMyCourse
from mediathread.sequence.apiviews import CsrfExemptSessionAuthentication


class SherdNoteCreate(CreateAPIView):
    authentication_classes = [CsrfExemptSessionAuthentication]
    permission_classes = [IsAuthenticated, AssetIsVisible, AssetInMyCourse]
    serializer_class = SherdNoteSerializer

    def post(self, request, *args, **kwargs):
        """
        Create a new annotation.
        """
        asset_id = kwargs.get('asset_id')

        # Need to explicitly check permissions of the asset being
        # annotated. Permission may be denied depending on
        # request.user, course configuration, and the asset in
        # question.
        asset = get_object_or_404(Asset, pk=asset_id)
        self.check_object_permissions(request, asset)

        data = request.data.copy()
        data['asset'] = asset
        data['author'] = request.user
        serializer = SherdNoteSerializer(data=data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
