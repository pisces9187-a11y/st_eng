"""
TTS API Views for generating pronunciation audio.

Endpoints:
- POST /api/v1/tts/speak/ - Generate audio from text
- POST /api/v1/tts/phoneme/ - Generate audio for IPA phoneme
- GET /api/v1/tts/voices/ - List available voices
"""

import logging
from asgiref.sync import async_to_sync
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import AllowAny
from django.conf import settings

from utils.tts import TTSService, TTSVoice, EDGE_TTS_AVAILABLE

logger = logging.getLogger(__name__)


class TTSSpeakView(APIView):
    """
    Generate speech audio from text.
    
    POST /api/v1/tts/speak/
    {
        "text": "Hello, how are you?",
        "voice": "en-US-AriaNeural",  // optional
        "rate": "+0%",  // optional
        "slow": false  // optional, for learners
    }
    
    Returns:
    {
        "success": true,
        "audio_url": "/media/tts/en-US-AriaNeural/abc123.mp3"
    }
    """
    permission_classes = [AllowAny]
    
    def post(self, request):
        if not EDGE_TTS_AVAILABLE:
            return Response({
                'success': False,
                'error': 'TTS service not available'
            }, status=status.HTTP_503_SERVICE_UNAVAILABLE)
        
        text = request.data.get('text', '').strip()
        
        if not text:
            return Response({
                'success': False,
                'error': 'Text is required'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        if len(text) > 1000:
            return Response({
                'success': False,
                'error': 'Text too long (max 1000 characters)'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        voice = request.data.get('voice', TTSVoice.DEFAULT)
        rate = request.data.get('rate')
        slow = request.data.get('slow', False)
        
        if slow:
            rate = "-25%"
        
        try:
            # Sử dụng async_to_sync thay vì asyncio.new_event_loop()
            audio_path = async_to_sync(TTSService.speak_async)(
                text, 
                voice=voice, 
                rate=rate
            )
            
            if audio_path:
                # Convert to URL
                audio_url = audio_path.replace(
                    str(settings.MEDIA_ROOT), 
                    settings.MEDIA_URL.rstrip('/')
                ).replace('\\', '/')
                
                return Response({
                    'success': True,
                    'audio_url': audio_url,
                    'text': text,
                    'voice': voice
                })
            else:
                logger.error(f"Failed to generate audio for text: {text[:50]}...")
                return Response({
                    'success': False,
                    'error': 'Failed to generate audio'
                }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
                
        except Exception as e:
            logger.error(f"TTS Error in TTSSpeakView: {str(e)}", exc_info=True)
            return Response({
                'success': False,
                'error': str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class TTSPhonemeView(APIView):
    """
    Generate audio for IPA phoneme practice.
    
    POST /api/v1/tts/phoneme/
    {
        "ipa_symbol": "æ",
        "example_word": "cat",  // optional
        "voice": "en-US-AriaNeural"  // optional
    }
    
    Returns:
    {
        "success": true,
        "phoneme_audio": "/media/tts/.../abc.mp3",
        "word_audio": "/media/tts/.../def.mp3",
        "slow_audio": "/media/tts/.../ghi.mp3"
    }
    """
    permission_classes = [AllowAny]
    
    def post(self, request):
        if not EDGE_TTS_AVAILABLE:
            return Response({
                'success': False,
                'error': 'TTS service not available'
            }, status=status.HTTP_503_SERVICE_UNAVAILABLE)
        
        ipa_symbol = request.data.get('ipa_symbol', '').strip()
        
        if not ipa_symbol:
            return Response({
                'success': False,
                'error': 'IPA symbol is required'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        example_word = request.data.get('example_word', '').strip()
        voice = request.data.get('voice', TTSVoice.DEFAULT)
        
        try:
            # Sử dụng async_to_sync thay vì asyncio.new_event_loop()
            result = async_to_sync(TTSService.speak_phoneme_async)(
                ipa_symbol, 
                example_word=example_word,
                voice=voice
            )
            
            # Convert paths to URLs
            response_data = {'success': True, 'ipa_symbol': ipa_symbol}
            
            for key, path in result.items():
                if path:
                    url = path.replace(
                        str(settings.MEDIA_ROOT),
                        settings.MEDIA_URL.rstrip('/')
                    ).replace('\\', '/')
                    response_data[key] = url
            
            return Response(response_data)
            
        except Exception as e:
            logger.error(f"TTS Error in TTSPhonemeView: {str(e)}", exc_info=True)
            return Response({
                'success': False,
                'error': str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class TTSVoicesView(APIView):
    """
    List available TTS voices.
    
    GET /api/v1/tts/voices/
    
    Returns list of voices with accent info.
    """
    permission_classes = [AllowAny]
    
    def get(self, request):
        voices = TTSVoice.get_all()
        
        return Response({
            'success': True,
            'default_voice': TTSVoice.DEFAULT,
            'voices': voices,
            'available': EDGE_TTS_AVAILABLE
        })


class TTSStatusView(APIView):
    """
    Check TTS service status.
    
    GET /api/v1/tts/status/
    """
    permission_classes = [AllowAny]
    
    def get(self, request):
        return Response({
            'available': EDGE_TTS_AVAILABLE,
            'default_voice': TTSVoice.DEFAULT,
            'cache_dir': str(TTSService.AUDIO_DIR),
            'supported_features': [
                'neural_voices',
                'multiple_accents',
                'rate_control',
                'pitch_control',
                'audio_caching'
            ]
<<<<<<< HEAD
        })
=======
        })
>>>>>>> 621f4d9814ab309da5f8bca35aa76c59a1c9c355
