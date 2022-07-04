from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.shortcuts import get_object_or_404
from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.parsers import JSONParser
from rest_framework.request import HttpRequest
from rest_framework.response import Response
from .models import FeedSource, Torrent
from .serializers import FeedSourceSerializer, TorrentSerializer


@api_view(['GET'])
def api_feed_source_list(request: HttpRequest):
    if request.method == 'GET':
        feed_sources = FeedSource.objects.all()
        serializer = FeedSourceSerializer(feed_sources, many=True)
        return Response(serializer.data)
    
    return Response(status=status.HTTP_403_FORBIDDEN)


@csrf_exempt
@api_view(['GET', 'POST'])
def api_torrent_list(request: HttpRequest):
    if request.method == 'GET':
        torrents = Torrent.objects.all()
        serializer = TorrentSerializer(torrents, many=True)
        return Response(serializer.data)

    elif request.method == 'POST':
        data = JSONParser().parse(request)
        serializer = TorrentSerializer(data=data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=201)
        return Response(serializer.errors, status=400)
    
    return Response(status=status.HTTP_403_FORBIDDEN)


@csrf_exempt
@api_view(['GET', 'PUT', 'DELETE'])
def api_torrent_detail(request: HttpRequest, id: str):
    torrent = get_object_or_404(Torrent, pk=id)

    if request.method == 'GET':
        serializer = TorrentSerializer(torrent)
        return Response(serializer.data)

    elif request.method == 'PUT':
        data = JSONParser().parse(request)
        serializer = TorrentSerializer(torrent, data=data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=201)
        return JsonResponse(serializer.errors, status=400)
    
    elif request.method == 'DELETE':
        torrent.delete()
        return Response(status=204)
    
    return Response(status=status.HTTP_403_FORBIDDEN)