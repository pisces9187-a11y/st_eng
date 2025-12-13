# backend/apps/curriculum/views_tts.py

import edge_tts
import logging
from asgiref.sync import async_to_sync
from django.http import HttpResponse, JsonResponse
from django.views.decorators.http import require_http_methods
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny

logger = logging.getLogger(__name__)

# Hàm nội bộ (Async): Tương tác trực tiếp với thư viện edge-tts
async def _generate_audio_async(text, voice):
    communicate = edge_tts.Communicate(text, voice)
    audio_data = b""
    # Lặp qua stream để gom dữ liệu audio
    async for chunk in communicate.stream():
        if chunk["type"] == "audio":
            audio_data += chunk["data"]
    return audio_data

# Hàm Wrapper (Sync): Được bọc bởi async_to_sync để gọi trong View
def generate_audio_sync(text, voice="en-US-ChristopherNeural"):
    try:
        # Gọi hàm async trong môi trường sync
        audio_content = async_to_sync(_generate_audio_async)(text, voice)
        return audio_content
    except Exception as e:
        logger.error(f"TTS Error: {str(e)}")
        return None

@api_view(['GET'])
@permission_classes([AllowAny]) # Hoặc IsAuthenticated tùy bạn
def tts_view(request):
    """
    API Endpoint: /api/v1/tts/speak/?text=Hello&voice=en-US-ChristopherNeural
    """
    text = request.GET.get('text', '').strip()
    voice = request.GET.get('voice', 'en-US-ChristopherNeural')

    if not text:
        return JsonResponse({'status': 'error', 'message': 'Missing text parameter'}, status=400)

    # 1. (Optional) Kiểm tra Cache/DB ở đây nếu cần tiết kiệm request
    
    # 2. Sinh audio trực tiếp
    audio_data = generate_audio_sync(text, voice)

    if audio_data:
        response = HttpResponse(audio_data, content_type="audio/mpeg")
        response['Content-Disposition'] = 'inline; filename="tts_audio.mp3"'
        return response
    else:
        return JsonResponse({'status': 'error', 'message': 'Failed to generate audio'}, status=500)
