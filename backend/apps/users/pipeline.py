"""
Custom Social Auth Pipeline for English Learning Platform.

This module contains custom pipeline steps for social authentication,
including saving user avatars from Google and Facebook.
"""

import requests
from django.core.files.base import ContentFile


def save_avatar(backend, user, response, *args, **kwargs):
    """
    Save user avatar from social provider.
    
    This pipeline step downloads and saves the user's profile picture
    from Google or Facebook during the social auth process.
    """
    avatar_url = None
    
    if backend.name == 'google-oauth2':
        # Google provides picture URL directly
        avatar_url = response.get('picture')
        
    elif backend.name == 'facebook':
        # Facebook provides picture in nested structure
        picture_data = response.get('picture', {}).get('data', {})
        avatar_url = picture_data.get('url')
        
        # Alternative: construct URL directly
        if not avatar_url:
            fb_id = response.get('id')
            if fb_id:
                avatar_url = f'https://graph.facebook.com/{fb_id}/picture?type=large'
    
    if avatar_url and not user.avatar:
        try:
            # Download avatar
            avatar_response = requests.get(avatar_url, timeout=10)
            if avatar_response.status_code == 200:
                # Determine file extension
                content_type = avatar_response.headers.get('content-type', '')
                if 'png' in content_type:
                    ext = 'png'
                elif 'gif' in content_type:
                    ext = 'gif'
                else:
                    ext = 'jpg'
                
                # Save avatar
                filename = f'avatar_{user.id}_{backend.name}.{ext}'
                user.avatar.save(
                    filename,
                    ContentFile(avatar_response.content),
                    save=True
                )
        except Exception as e:
            # Don't fail authentication if avatar download fails
            print(f'Failed to save avatar for user {user.id}: {e}')
    
    return None


def save_user_details(backend, user, response, *args, **kwargs):
    """
    Save additional user details from social provider.
    
    Updates user's first_name, last_name from social profile.
    """
    changed = False
    
    if backend.name == 'google-oauth2':
        if not user.first_name and response.get('given_name'):
            user.first_name = response.get('given_name')
            changed = True
        if not user.last_name and response.get('family_name'):
            user.last_name = response.get('family_name')
            changed = True
            
    elif backend.name == 'facebook':
        name = response.get('name', '')
        if name and not user.first_name:
            parts = name.split(' ', 1)
            user.first_name = parts[0]
            if len(parts) > 1:
                user.last_name = parts[1]
            changed = True
    
    if changed:
        user.save()
    
    return None
