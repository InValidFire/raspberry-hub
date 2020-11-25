from fastapi import APIRouter, Request
from fastapi.responses import RedirectResponse
from spotipy.oauth2 import SpotifyOAuth
from functools import wraps
from modules.system import get_site, token_required
import spotipy

router = APIRouter()

cache = ".spotifycache"
scope = "user-modify-playback-state user-read-playback-state"
oauth = SpotifyOAuth(scope=scope, client_id="722dffa39f654b83a12e92868565b502", client_secret="a07514990cec47c08c37b81e405efc8e", redirect_uri=f"{get_site()}/spotify/callback", open_browser=False, cache_path=cache)

def get_token() -> str:
    """returns Spotify access token."""
    token_info = oauth.get_cached_token()
    if token_info and not oauth.is_token_expired(token_info):
        access_token = token_info['access_token']
        return access_token

@router.get("/spotify/login")
@token_required
def login(request: Request, token=None):
    token_info = oauth.get_cached_token()
    if token_info and not oauth.is_token_expired(token_info):
        return RedirectResponse("/spotify")
    return RedirectResponse(oauth.get_authorize_url())

@router.get("/spotify/callback")
def set_token(code, request: Request):
    return RedirectResponse(f"{get_site()}/spotify")

@router.get("/spotify")
def spotify(request: Request, token = None):
    access_token = get_token()
    api = spotipy.Spotify(access_token)
    return api.me()

@router.get("/spotify/pause")
@token_required
def pause(request: Request, token = None):
    access_token = get_token()
    api = spotipy.Spotify(access_token)
    try:
        api.pause_playback()
        return {"message": "Playback paused"}
    except spotipy.exceptions.SpotifyException:
        return {"message": "Error! Is it paused already?"}

@router.get("/spotify/play")
@token_required
def play(request: Request, token = None):
    access_token = get_token()
    api = spotipy.Spotify(access_token)
    try:
        api.start_playback()
        return {"message": "Playback started"}
    except spotipy.exceptions.SpotifyException:
        return {"message": "Error! Is it playing already?"}