from typing import List
import json
import re
import logging
from django.http import JsonResponse
from django.core.exceptions import PermissionDenied
from django.views.decorators.csrf import csrf_exempt
from django.shortcuts import get_object_or_404
from django.db.models.query import QuerySet
from django.db.models import Model
from rest_framework import status
from rest_framework.authentication import TokenAuthentication
from rest_framework.decorators import api_view, authentication_classes, permission_classes
from rest_framework.parsers import JSONParser
from rest_framework.permissions import IsAuthenticated
from rest_framework.request import HttpRequest
from rest_framework.response import Response
from transmission_rpc import Client
from transrss.settings import TRANSMISSION_CONFIG
from .models import FeedSource, FeedMatcher, Torrent, State
from .serializers import FeedSourceSerializer, TorrentSerializer


@api_view(['GET'])
@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated])
def api_feed_source_list(request: HttpRequest):
    if request.method == 'GET':
        feed_sources = FeedSource.objects.all()
        serializer = FeedSourceSerializer(feed_sources, many=True)
        return Response(serializer.data)
    
    return Response(status=status.HTTP_403_FORBIDDEN)


@csrf_exempt
@api_view(['GET', 'POST'])
@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated])
def api_torrent_list(request: HttpRequest):
    if request.method == 'GET':
        torrents = Torrent.objects.all()
        serializer = TorrentSerializer(torrents, many=True)
        return Response(serializer.data)

    elif request.method == 'POST':        
        data = JSONParser().parse(request)
        serializer = TorrentSerializer(data=data)
        if serializer.is_valid():
            torrent = serializer.save()
            return Response(TorrentSerializer(torrent).data, status=201)
        return Response(serializer.errors, status=400)
    
    return Response(status=status.HTTP_403_FORBIDDEN)


@csrf_exempt
@api_view(['GET'])
@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated])
def api_torrent_status(request: HttpRequest):
    torrent_ids: List[str] = json.loads(request.body)
    torrent_status = [len(Torrent.objects.filter(guid=id)) for id in torrent_ids]
    return Response(torrent_status)



@csrf_exempt
@api_view(['GET', 'PUT', 'DELETE'])
@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated])
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


@csrf_exempt
@api_view(['GET'])
@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated])
def match_download(request: HttpRequest):
    """Match torrents and add to transmission

    Parameters
    ----------
    request : HttpRequest
        Http request instance.
    """
    if not request.user.is_authenticated:
        raise PermissionDenied

    client = Client(**TRANSMISSION_CONFIG)
    feeds = FeedSource.objects.all()
    for feed in feeds:
        torrents: QuerySet[Torrent] = Torrent.objects.filter(source=feed)
        matchers: QuerySet[FeedMatcher] = FeedMatcher.objects.filter(source=feed)
        for torrent in torrents:
            if torrent.added:
                continue
            for matcher in matchers:
                if re.search(matcher.pattern, torrent.title) is not None:
                    try:
                        client.add_torrent(torrent.enclosure_url, download_dir=matcher.download_dir)
                        torrent.added = True
                    except Exception:
                        logging.error("Failed to add torrent '%s'.", torrent.title)
            torrent.save()
    return Response(status=status.HTTP_200_OK)


@csrf_exempt
@api_view(['POST'])
@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated])
def api_torrent_begin_update(request: HttpRequest):
    torrent_all = Torrent.objects.all()
    for item in torrent_all:
        item.alive = False
        item.save()
    ''' Update state
    '''
    state, _ = State.objects.get_or_create(id=0)
    state.refreshing = True
    state.save()
    return Response(status=status.HTTP_200_OK)


@csrf_exempt
@api_view(['PUT'])
@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated])
def api_torrent_keep_alive(request: HttpRequest, guid: str):
    torrent = get_object_or_404(Torrent, pk=guid)
    torrent.alive = True
    torrent.save()
    return Response(status=status.HTTP_200_OK)


@csrf_exempt
@api_view(['PUT'])
@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated])
def api_torrent_keep_alive_batch(request: HttpRequest):
    torrent_ids: List[str] = json.loads(request.body)
    active_status: List[int] = []
    for guid in torrent_ids:
        try:
            torrent = Torrent.objects.get(guid=guid)
            torrent.alive = True
            torrent.save()
            active_status.append(0)
        except Model.DoesNotExist:
            active_status.append(1)
    return Response(active_status, status=status.HTTP_200_OK)


@csrf_exempt
@api_view(['DELETE'])
@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated])
def api_torrent_end_update(request: HttpRequest):
    torrent_died = Torrent.objects.filter(alive=False).all()
    torrent_died.delete()
    ''' Update state
    '''
    state, _ = State.objects.get_or_create(id=0)
    state.refreshing = False
    state.save()
    return Response(status=status.HTTP_200_OK)