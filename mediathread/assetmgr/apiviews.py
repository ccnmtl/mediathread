from django.shortcuts import get_object_or_404

from rest_framework import status
from rest_framework.generics import UpdateAPIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from mediathread.assetmgr.models import Asset
from mediathread.assetmgr.serializers import AssetSerializer
from mediathread.assetmgr.permissions import AssetIsOwnedByMe
from mediathread.sequence.apiviews import CsrfExemptSessionAuthentication


class AssetUpdate(UpdateAPIView):
    authentication_classes = [CsrfExemptSessionAuthentication]
    permission_classes = [IsAuthenticated, AssetIsOwnedByMe]
    serializer_class = AssetSerializer

    def put(self, request, *args, **kwargs):
        """
        Update an asset.
        """
        asset_id = kwargs.get('asset_id')

        asset = get_object_or_404(Asset, pk=asset_id)
        self.check_object_permissions(request, asset)

        data = request.data.copy()
        serializer = AssetSerializer(asset)

        title = data.get('title')
        transcript = data.get('transcript')

        if title is None and transcript is None:
            return Response({
                'error': 'Bad Request: missing asset data'
            }, status=status.HTTP_400_BAD_REQUEST)

        # Update title
        if title is not None:
            asset.title = title

        # Update transcript
        if transcript is not None:
            asset.transcript = transcript

        asset.save()

        return Response(serializer.data, status=status.HTTP_200_OK)
