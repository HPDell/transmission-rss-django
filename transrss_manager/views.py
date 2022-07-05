from multiprocessing import Process
from this import d
from django.http import HttpResponseForbidden, HttpResponseServerError
from django.shortcuts import get_object_or_404, redirect, render
from django.contrib.auth import authenticate, login, logout, get_user
from django.core.exceptions import PermissionDenied, BadRequest
from django.http.request import HttpRequest
from transrss_manager.models import FeedSource, FeedMatcher, Torrent
from transrss_manager.forms import FeedAddForm, MatcherAddForm
from transrss_manager.subscriber import feed_load


def index(request: HttpRequest):
    feeds = FeedSource.objects.all()
    torrents = Torrent.objects.order_by('-pub_date').all()
    return render(request, "index.html", {
        'feeds': feeds,
        'torrents': torrents
    })


def feed_list(request: HttpRequest):
    if request.method == 'GET':
        return redirect('home')
    
    elif request.method == 'POST':
        if not request.user.is_authenticated:
            raise PermissionDenied

        form = FeedAddForm(request.POST)
        if form.is_valid():
            feed = FeedSource(**form.cleaned_data)
            feed.save()
        return redirect('home')
    
    return HttpResponseForbidden()


def feed_detail(request: HttpRequest, id: int):
    feed = get_object_or_404(FeedSource, pk=id)
    
    if request.method == 'GET':
        return render(request, 'feed.html', {
            'feed': feed,
            'feeds': FeedSource.objects.all(),
            'matchers': FeedMatcher.objects.filter(source=feed).all()
        })
    
    elif request.method == 'POST':
        if not request.user.is_authenticated:
            raise PermissionDenied

        form = FeedAddForm(request.POST)
        if form.is_valid():
            feed.title = form.cleaned_data['title']
            feed.url = form.cleaned_data['url']
            feed.save()
            return redirect('feed_detail', id=id)
        else:
            return HttpResponseServerError()

    return HttpResponseForbidden()


def feed_delete(request: HttpRequest, id: int):
    feed = get_object_or_404(FeedSource, pk=id)

    if request.method == 'POST':
        if not request.user.is_authenticated:
            raise PermissionDenied

        feed.delete()
        return redirect('home')

    return HttpResponseForbidden()


def matcher_list(request: HttpRequest, feed_id: int):
    feed = get_object_or_404(FeedSource, pk=feed_id)

    if request.method == 'GET':
        return redirect('home')
    
    elif request.method == 'POST':
        if not request.user.is_authenticated:
            raise PermissionDenied

        form = MatcherAddForm(request.POST)
        if form.is_valid():
            matcher = FeedMatcher(source=feed, **form.cleaned_data)
            matcher.save()
            return redirect('feed_detail', id=feed_id)
        else:
            return HttpResponseServerError()

    return HttpResponseForbidden()


def matcher_delete(request: HttpRequest, feed_id: int, matcher_id: int):
    if request.method == 'POST':
        if not request.user.is_authenticated:
            raise PermissionDenied

        matcher = get_object_or_404(FeedMatcher, pk=matcher_id)
        matcher.delete()
        return redirect('feed_detail', id=feed_id)

    return HttpResponseForbidden()


def torrent_refresh(request: HttpRequest):
    if not request.user.is_authenticated:
        raise PermissionDenied
        
    suber = Process(target=feed_load)
    suber.daemon = True
    suber.start()
    suber.join()
    return redirect(to="/")


def user_login(request: HttpRequest):
    if request.method == 'GET':
        redirect_to = request.GET.get('redirect') or 'home'
        if get_user(request).is_authenticated:
            return redirect(to=redirect_to)
        else:
            return render(request, 'login.html', {
                'redirect': redirect_to
            })
    
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            redirect_to = request.POST.get('redirect') or 'home'
            return redirect(to=redirect_to)
        else:
            raise PermissionDenied


def user_logout(request: HttpRequest):
    if get_user(request).is_authenticated:
        logout(request)
    redirect_to = request.GET.get('redirect') or 'home'
    return redirect(to=redirect_to)

