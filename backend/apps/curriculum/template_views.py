"""
Template Views for Curriculum App - Pronunciation Lessons.
"""

import json
from django.views.generic import TemplateView, DetailView, ListView
from django.shortcuts import get_object_or_404
from django.http import JsonResponse
from django.db.models import Q

from apps.users.middleware import JWTRequiredMixin
from .models import (
    PronunciationLesson, Phoneme, PhonemeCategory, 
    PhonemeWord, MinimalPair, TongueTwister
)


# =============================================================================
# PUBLIC VIEWS (No auth required)
# =============================================================================

class PronunciationLibraryView(TemplateView):
    """
    Public view for browsing pronunciation lessons.
    Shows all available IPA lessons organized by category.
    """
    template_name = 'pages/pronunciation_library.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['page_title'] = 'Luyện phát âm IPA'
        
        # Get all published lessons
        context['lessons'] = PronunciationLesson.objects.filter(
            status='published'
        ).prefetch_related('phonemes').order_by('part_number', 'unit_number')
        
        # Get phoneme categories
        context['categories'] = PhonemeCategory.objects.all().prefetch_related('phonemes')
        
        return context


class PronunciationLessonView(TemplateView):
    """
    View for individual pronunciation lesson player.
    Provides JSON data for Vue.js frontend.
    """
    template_name = 'pages/pronunciation_lesson.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        slug = kwargs.get('slug')
        
        if slug:
            # Try to get lesson from database
            try:
                lesson = PronunciationLesson.objects.prefetch_related(
                    'phonemes',
                    'phonemes__example_words',
                    'tongue_twisters'
                ).get(slug=slug, status='published')
                
                context['lesson'] = lesson
                context['page_title'] = lesson.title_vi
                
                # Prepare JSON data for Vue.js
                lesson_data = {
                    'id': lesson.id,
                    'slug': lesson.slug,
                    'title': lesson.title,
                    'title_vi': lesson.title_vi,
                    'description': lesson.description,
                    'description_vi': lesson.description_vi,
                    'lesson_type': lesson.lesson_type,
                    'lesson_content': lesson.lesson_content,
                    'objectives': lesson.objectives,
                    'part_number': lesson.part_number,
                    'unit_number': lesson.unit_number,
                    'estimated_minutes': lesson.estimated_minutes,
                    'xp_reward': lesson.xp_reward,
                    'difficulty': lesson.difficulty,
                }
                
                # Get phonemes with example words
                phonemes_data = []
                for phoneme in lesson.phonemes.all():
                    words = list(phoneme.example_words.values(
                        'word', 'ipa_transcription', 'meaning_vi', 
                        'phoneme_position', 'highlight_start', 'highlight_end'
                    )[:6])
                    
                    phonemes_data.append({
                        'id': phoneme.id,
                        'ipa_symbol': phoneme.ipa_symbol,
                        'vietnamese_approx': phoneme.vietnamese_approx,
                        'phoneme_type': phoneme.phoneme_type,
                        'voicing': phoneme.voicing,
                        'mouth_position': phoneme.mouth_position,
                        'mouth_position_vi': phoneme.mouth_position_vi,
                        'tongue_position_vi': phoneme.tongue_position_vi,
                        'pronunciation_tips': phoneme.pronunciation_tips,
                        'pronunciation_tips_vi': phoneme.pronunciation_tips_vi,
                        'common_mistakes_vi': phoneme.common_mistakes_vi,
                        'example_words': words if words else self._get_default_example_words(phoneme.ipa_symbol),
                    })
                
                # Get minimal pairs
                phoneme_ids = [p['id'] for p in phonemes_data]
                minimal_pairs = list(MinimalPair.objects.filter(
                    Q(phoneme_1_id__in=phoneme_ids) | Q(phoneme_2_id__in=phoneme_ids)
                ).values(
                    'id', 'word_1', 'word_1_ipa', 'word_1_meaning',
                    'word_2', 'word_2_ipa', 'word_2_meaning',
                    'difference_note_vi', 'difficulty'
                )[:10])
                
                # Auto-generate minimal pairs from example_words if none exist
                if not minimal_pairs and len(phonemes_data) >= 2:
                    minimal_pairs = self._generate_minimal_pairs_from_phonemes(phonemes_data)
                
                # Get tongue twisters
                tongue_twisters = list(lesson.tongue_twisters.values(
                    'id', 'text', 'ipa_transcription', 'meaning_vi', 'difficulty'
                )[:3])
                
                # User progress (if authenticated)
                user_progress = None
                if hasattr(self.request, 'jwt_user') and self.request.jwt_user:
                    from apps.users.models import UserPronunciationLessonProgress
                    try:
                        progress = UserPronunciationLessonProgress.objects.get(
                            user=self.request.jwt_user,
                            pronunciation_lesson=lesson
                        )
                        user_progress = {
                            'id': progress.id,
                            'status': progress.status,
                            'current_screen': progress.current_screen,
                            'completed_screens': progress.completed_screens,
                            'xp_earned': progress.xp_earned,
                        }
                    except UserPronunciationLessonProgress.DoesNotExist:
                        pass
                
                # Set JSON context for template
                context['lesson_json'] = json.dumps(lesson_data, ensure_ascii=False)
                context['phonemes_json'] = json.dumps(phonemes_data, ensure_ascii=False)
                context['minimal_pairs_json'] = json.dumps(minimal_pairs, ensure_ascii=False)
                context['tongue_twisters_json'] = json.dumps(tongue_twisters, ensure_ascii=False)
                context['user_progress_json'] = json.dumps(user_progress, ensure_ascii=False)
                
            except PronunciationLesson.DoesNotExist:
                # Return demo lesson for development
                demo = self._get_demo_lesson()
                context['lesson'] = demo
                context['lesson_json'] = json.dumps(demo, ensure_ascii=False)
                context['phonemes_json'] = json.dumps(self._get_demo_phonemes(), ensure_ascii=False)
                context['minimal_pairs_json'] = json.dumps(self._get_demo_minimal_pairs(), ensure_ascii=False)
                context['tongue_twisters_json'] = json.dumps([], ensure_ascii=False)
                context['user_progress_json'] = json.dumps(None, ensure_ascii=False)
        else:
            demo = self._get_demo_lesson()
            context['lesson'] = demo
            context['lesson_json'] = json.dumps(demo, ensure_ascii=False)
            context['phonemes_json'] = json.dumps(self._get_demo_phonemes(), ensure_ascii=False)
            context['minimal_pairs_json'] = json.dumps(self._get_demo_minimal_pairs(), ensure_ascii=False)
            context['tongue_twisters_json'] = json.dumps([], ensure_ascii=False)
            context['user_progress_json'] = json.dumps(None, ensure_ascii=False)
        
        return context
    
    def _get_demo_lesson(self):
        """Return demo lesson data for development/testing."""
        return {
            'id': 1,
            'slug': 'demo-p-b',
            'title': 'The Popping Sounds',
            'title_vi': 'Âm bật hơi /p/ và /b/',
            'description': 'Learn to distinguish voiceless /p/ and voiced /b/',
            'description_vi': 'Học cách phân biệt âm vô thanh /p/ và hữu thanh /b/. Hai âm này có khẩu hình giống nhau nhưng khác nhau ở việc rung thanh quản.',
            'lesson_type': 'pair_contrast',
            'lesson_content': [],
            'objectives': [
                'Hiểu khẩu hình miệng giống nhau của /p/ và /b/',
                'Phân biệt được sự khác nhau giữa Vô thanh và Hữu thanh',
                'Luyện tập từ vựng chứa âm /p/ và /b/'
            ],
            'part_number': 4,
            'unit_number': 7,
            'xp_reward': 15,
            'estimated_minutes': 10,
            'difficulty': 1,
        }
    
    def _get_demo_phonemes(self):
        """Return demo phoneme data."""
        return [
            {
                'id': 1,
                'ipa_symbol': 'p',
                'vietnamese_approx': 'pờ (không có âm ờ)',
                'phoneme_type': 'plosive',
                'voicing': 'voiceless',
                'mouth_position': 'Lips pressed together, then released with a puff of air',
                'mouth_position_vi': 'Hai môi mím chặt lại, sau đó bật ra cùng luồng hơi',
                'tongue_position_vi': 'Lưỡi ở vị trí tự nhiên',
                'pronunciation_tips': 'Put a piece of paper in front of your mouth. When you say /p/, the paper should move.',
                'pronunciation_tips_vi': 'Đặt một tờ giấy mỏng trước miệng. Khi phát âm /p/, tờ giấy phải bay lên! Đọc "pờ" nhưng KHÔNG có âm "ờ". Chỉ bật hơi gió.',
                'common_mistakes_vi': 'Người Việt thường phát âm /p/ quá nhẹ hoặc thêm âm "ờ" phía sau.',
                'example_words': [
                    {'word': 'Pen', 'ipa_transcription': '/pen/', 'meaning_vi': 'Cây bút', 'phoneme_position': 'initial'},
                    {'word': 'Soup', 'ipa_transcription': '/suːp/', 'meaning_vi': 'Súp', 'phoneme_position': 'final'},
                    {'word': 'Pop', 'ipa_transcription': '/pɒp/', 'meaning_vi': 'Nổ, nhạc Pop', 'phoneme_position': 'initial'},
                    {'word': 'Apple', 'ipa_transcription': '/ˈæpəl/', 'meaning_vi': 'Quả táo', 'phoneme_position': 'medial'},
                    {'word': 'Pea', 'ipa_transcription': '/piː/', 'meaning_vi': 'Hạt đậu', 'phoneme_position': 'initial'},
                    {'word': 'Stop', 'ipa_transcription': '/stɒp/', 'meaning_vi': 'Dừng lại', 'phoneme_position': 'final'},
                ]
            },
            {
                'id': 2,
                'ipa_symbol': 'b',
                'vietnamese_approx': 'bờ (nhanh, rung)',
                'phoneme_type': 'plosive',
                'voicing': 'voiced',
                'mouth_position': 'Lips pressed together, then released with vibration',
                'mouth_position_vi': 'Hai môi mím chặt lại, sau đó bật ra cùng độ rung của thanh quản',
                'tongue_position_vi': 'Lưỡi ở vị trí tự nhiên',
                'pronunciation_tips': 'Put your fingers on your throat. When you say /b/, you should feel vibration.',
                'pronunciation_tips_vi': 'Đặt 2 ngón tay lên thanh quản (cổ họng). Nói /b/. Bạn có thấy nó rung như điện thoại không? Đọc "bờ" nhanh, dứt khoát.',
                'common_mistakes_vi': 'Người Việt có thể phát âm /b/ quá giống /p/ vì không đủ độ rung.',
                'example_words': [
                    {'word': 'Bad', 'ipa_transcription': '/bæd/', 'meaning_vi': 'Tệ', 'phoneme_position': 'initial'},
                    {'word': 'Web', 'ipa_transcription': '/web/', 'meaning_vi': 'Mạng lưới', 'phoneme_position': 'final'},
                    {'word': 'Boat', 'ipa_transcription': '/bəʊt/', 'meaning_vi': 'Con thuyền', 'phoneme_position': 'initial'},
                    {'word': 'Brother', 'ipa_transcription': '/ˈbrʌðər/', 'meaning_vi': 'Anh/em trai', 'phoneme_position': 'initial'},
                    {'word': 'Bob', 'ipa_transcription': '/bɒb/', 'meaning_vi': 'Tên Bob', 'phoneme_position': 'initial'},
                    {'word': 'Cab', 'ipa_transcription': '/kæb/', 'meaning_vi': 'Taxi', 'phoneme_position': 'final'},
                ]
            }
        ]
    
    def _get_demo_minimal_pairs(self):
        """Return demo minimal pairs data."""
        return [
            {
                'id': 1,
                'word_1': 'Pea',
                'word_1_ipa': '/piː/',
                'word_1_meaning': 'Hạt đậu',
                'word_2': 'Bee',
                'word_2_ipa': '/biː/',
                'word_2_meaning': 'Con ong',
                'difference_note_vi': '/p/ là vô thanh (chỉ bật hơi), /b/ là hữu thanh (rung cổ họng).',
                'difficulty': 1
            },
            {
                'id': 2,
                'word_1': 'Pop',
                'word_1_ipa': '/pɒp/',
                'word_1_meaning': 'Tiếng nổ',
                'word_2': 'Bob',
                'word_2_ipa': '/bɒb/',
                'word_2_meaning': 'Tên Bob',
                'difference_note_vi': 'Cả hai từ có âm đầu và cuối khác nhau. Pop có /p/ vô thanh, Bob có /b/ hữu thanh.',
                'difficulty': 1
            },
            {
                'id': 3,
                'word_1': 'Cap',
                'word_1_ipa': '/kæp/',
                'word_1_meaning': 'Cái mũ',
                'word_2': 'Cab',
                'word_2_ipa': '/kæb/',
                'word_2_meaning': 'Taxi',
                'difference_note_vi': 'Âm cuối /p/ ngắt rất nhanh. Âm cuối /b/ kéo dài hơn một chút và trầm.',
                'difficulty': 2
            },
            {
                'id': 4,
                'word_1': 'Pat',
                'word_1_ipa': '/pæt/',
                'word_1_meaning': 'Vỗ nhẹ',
                'word_2': 'Bat',
                'word_2_ipa': '/bæt/',
                'word_2_meaning': 'Con dơi/Gậy bóng chày',
                'difference_note_vi': 'Tập trung vào âm đầu: /p/ chỉ bật hơi, /b/ rung thanh quản.',
                'difficulty': 1
            },
            {
                'id': 5,
                'word_1': 'Rope',
                'word_1_ipa': '/rəʊp/',
                'word_1_meaning': 'Sợi dây',
                'word_2': 'Robe',
                'word_2_ipa': '/rəʊb/',
                'word_2_meaning': 'Áo choàng',
                'difference_note_vi': 'Chú ý âm cuối: /p/ vô thanh vs /b/ hữu thanh.',
                'difficulty': 2
            }
        ]
    
    def _generate_minimal_pairs_from_phonemes(self, phonemes_data):
        """
        Auto-generate minimal pair challenges from phoneme example words.
        Used when no MinimalPair records exist in database.
        """
        if len(phonemes_data) < 2:
            return []
        
        phoneme1 = phonemes_data[0]
        phoneme2 = phonemes_data[1]
        words1 = phoneme1.get('example_words', [])
        words2 = phoneme2.get('example_words', [])
        
        minimal_pairs = []
        
        # Create pairs by matching words from each phoneme
        max_pairs = min(5, len(words1), len(words2))
        
        for i in range(max_pairs):
            w1 = words1[i] if i < len(words1) else words1[0]
            w2 = words2[i] if i < len(words2) else words2[0]
            
            # Determine difference note based on phoneme types
            if phoneme1.get('voicing') != phoneme2.get('voicing'):
                voicing1 = 'vô thanh' if phoneme1.get('voicing') == 'voiceless' else 'hữu thanh'
                voicing2 = 'vô thanh' if phoneme2.get('voicing') == 'voiceless' else 'hữu thanh'
                diff_note = f"/{phoneme1['ipa_symbol']}/ là {voicing1}, /{phoneme2['ipa_symbol']}/ là {voicing2}."
            else:
                # For vowels - compare length
                symbol1 = phoneme1.get('ipa_symbol', '')
                symbol2 = phoneme2.get('ipa_symbol', '')
                if ':' in symbol1 or 'ː' in symbol1:
                    diff_note = f"/{symbol1}/ là âm DÀI (kéo dài), /{symbol2}/ là âm NGẮN (nhanh, dứt khoát)."
                elif ':' in symbol2 or 'ː' in symbol2:
                    diff_note = f"/{symbol1}/ là âm NGẮN (nhanh, dứt khoát), /{symbol2}/ là âm DÀI (kéo dài)."
                else:
                    diff_note = f"Phân biệt /{symbol1}/ và /{symbol2}/ qua khẩu hình miệng và độ dài."
            
            minimal_pairs.append({
                'id': i + 1,
                'word_1': w1.get('word', ''),
                'word_1_ipa': w1.get('ipa_transcription', ''),
                'word_1_meaning': w1.get('meaning_vi', ''),
                'word_2': w2.get('word', ''),
                'word_2_ipa': w2.get('ipa_transcription', ''),
                'word_2_meaning': w2.get('meaning_vi', ''),
                'difference_note_vi': diff_note,
                'difficulty': 1
            })
        
        return minimal_pairs
    
    def _get_default_example_words(self, ipa_symbol):
        """
        Return default example words for common phonemes.
        Used when database has no example_words.
        """
        # Default example words for each phoneme
        defaults = {
            # Short vowels
            'ɪ': [
                {'word': 'Sit', 'ipa_transcription': '/sɪt/', 'meaning_vi': 'Ngồi', 'phoneme_position': 'medial'},
                {'word': 'Ship', 'ipa_transcription': '/ʃɪp/', 'meaning_vi': 'Con tàu', 'phoneme_position': 'medial'},
                {'word': 'Bit', 'ipa_transcription': '/bɪt/', 'meaning_vi': 'Một chút', 'phoneme_position': 'medial'},
                {'word': 'Fish', 'ipa_transcription': '/fɪʃ/', 'meaning_vi': 'Con cá', 'phoneme_position': 'medial'},
                {'word': 'Big', 'ipa_transcription': '/bɪɡ/', 'meaning_vi': 'To lớn', 'phoneme_position': 'medial'},
            ],
            'ʊ': [
                {'word': 'Book', 'ipa_transcription': '/bʊk/', 'meaning_vi': 'Quyển sách', 'phoneme_position': 'medial'},
                {'word': 'Good', 'ipa_transcription': '/ɡʊd/', 'meaning_vi': 'Tốt', 'phoneme_position': 'medial'},
                {'word': 'Put', 'ipa_transcription': '/pʊt/', 'meaning_vi': 'Đặt', 'phoneme_position': 'medial'},
                {'word': 'Foot', 'ipa_transcription': '/fʊt/', 'meaning_vi': 'Bàn chân', 'phoneme_position': 'medial'},
                {'word': 'Look', 'ipa_transcription': '/lʊk/', 'meaning_vi': 'Nhìn', 'phoneme_position': 'medial'},
            ],
            'e': [
                {'word': 'Bed', 'ipa_transcription': '/bed/', 'meaning_vi': 'Giường', 'phoneme_position': 'medial'},
                {'word': 'Red', 'ipa_transcription': '/red/', 'meaning_vi': 'Đỏ', 'phoneme_position': 'medial'},
                {'word': 'Ten', 'ipa_transcription': '/ten/', 'meaning_vi': 'Mười', 'phoneme_position': 'medial'},
                {'word': 'Pet', 'ipa_transcription': '/pet/', 'meaning_vi': 'Thú cưng', 'phoneme_position': 'medial'},
            ],
            'æ': [
                {'word': 'Cat', 'ipa_transcription': '/kæt/', 'meaning_vi': 'Con mèo', 'phoneme_position': 'medial'},
                {'word': 'Bad', 'ipa_transcription': '/bæd/', 'meaning_vi': 'Xấu', 'phoneme_position': 'medial'},
                {'word': 'Man', 'ipa_transcription': '/mæn/', 'meaning_vi': 'Đàn ông', 'phoneme_position': 'medial'},
                {'word': 'Hat', 'ipa_transcription': '/hæt/', 'meaning_vi': 'Cái mũ', 'phoneme_position': 'medial'},
            ],
            'ʌ': [
                {'word': 'Cup', 'ipa_transcription': '/kʌp/', 'meaning_vi': 'Cái cốc', 'phoneme_position': 'medial'},
                {'word': 'Bus', 'ipa_transcription': '/bʌs/', 'meaning_vi': 'Xe buýt', 'phoneme_position': 'medial'},
                {'word': 'Run', 'ipa_transcription': '/rʌn/', 'meaning_vi': 'Chạy', 'phoneme_position': 'medial'},
                {'word': 'Sun', 'ipa_transcription': '/sʌn/', 'meaning_vi': 'Mặt trời', 'phoneme_position': 'medial'},
            ],
            'ə': [
                {'word': 'About', 'ipa_transcription': '/əˈbaʊt/', 'meaning_vi': 'Về', 'phoneme_position': 'initial'},
                {'word': 'Teacher', 'ipa_transcription': '/ˈtiːtʃər/', 'meaning_vi': 'Giáo viên', 'phoneme_position': 'final'},
                {'word': 'Banana', 'ipa_transcription': '/bəˈnænə/', 'meaning_vi': 'Quả chuối', 'phoneme_position': 'medial'},
            ],
            # Long vowels  
            'iː': [
                {'word': 'See', 'ipa_transcription': '/siː/', 'meaning_vi': 'Thấy', 'phoneme_position': 'final'},
                {'word': 'Sheep', 'ipa_transcription': '/ʃiːp/', 'meaning_vi': 'Con cừu', 'phoneme_position': 'medial'},
                {'word': 'Tea', 'ipa_transcription': '/tiː/', 'meaning_vi': 'Trà', 'phoneme_position': 'final'},
                {'word': 'Feet', 'ipa_transcription': '/fiːt/', 'meaning_vi': 'Bàn chân (số nhiều)', 'phoneme_position': 'medial'},
                {'word': 'Beach', 'ipa_transcription': '/biːtʃ/', 'meaning_vi': 'Bãi biển', 'phoneme_position': 'medial'},
            ],
            'uː': [
                {'word': 'Food', 'ipa_transcription': '/fuːd/', 'meaning_vi': 'Thức ăn', 'phoneme_position': 'medial'},
                {'word': 'Moon', 'ipa_transcription': '/muːn/', 'meaning_vi': 'Mặt trăng', 'phoneme_position': 'medial'},
                {'word': 'Blue', 'ipa_transcription': '/bluː/', 'meaning_vi': 'Màu xanh dương', 'phoneme_position': 'final'},
                {'word': 'Pool', 'ipa_transcription': '/puːl/', 'meaning_vi': 'Hồ bơi', 'phoneme_position': 'medial'},
                {'word': 'School', 'ipa_transcription': '/skuːl/', 'meaning_vi': 'Trường học', 'phoneme_position': 'medial'},
            ],
            'ɑː': [
                {'word': 'Car', 'ipa_transcription': '/kɑːr/', 'meaning_vi': 'Xe hơi', 'phoneme_position': 'medial'},
                {'word': 'Father', 'ipa_transcription': '/ˈfɑːðər/', 'meaning_vi': 'Cha', 'phoneme_position': 'medial'},
                {'word': 'Heart', 'ipa_transcription': '/hɑːrt/', 'meaning_vi': 'Trái tim', 'phoneme_position': 'medial'},
            ],
            'ɔː': [
                {'word': 'Door', 'ipa_transcription': '/dɔːr/', 'meaning_vi': 'Cửa', 'phoneme_position': 'medial'},
                {'word': 'Four', 'ipa_transcription': '/fɔːr/', 'meaning_vi': 'Bốn', 'phoneme_position': 'medial'},
                {'word': 'Call', 'ipa_transcription': '/kɔːl/', 'meaning_vi': 'Gọi', 'phoneme_position': 'medial'},
                {'word': 'Ball', 'ipa_transcription': '/bɔːl/', 'meaning_vi': 'Quả bóng', 'phoneme_position': 'medial'},
            ],
            'ɜː': [
                {'word': 'Bird', 'ipa_transcription': '/bɜːd/', 'meaning_vi': 'Con chim', 'phoneme_position': 'medial'},
                {'word': 'Work', 'ipa_transcription': '/wɜːk/', 'meaning_vi': 'Làm việc', 'phoneme_position': 'medial'},
                {'word': 'Learn', 'ipa_transcription': '/lɜːn/', 'meaning_vi': 'Học', 'phoneme_position': 'medial'},
                {'word': 'Girl', 'ipa_transcription': '/ɡɜːl/', 'meaning_vi': 'Con gái', 'phoneme_position': 'medial'},
            ],
            # Diphthongs
            'eɪ': [
                {'word': 'Day', 'ipa_transcription': '/deɪ/', 'meaning_vi': 'Ngày', 'phoneme_position': 'final'},
                {'word': 'Say', 'ipa_transcription': '/seɪ/', 'meaning_vi': 'Nói', 'phoneme_position': 'final'},
                {'word': 'Make', 'ipa_transcription': '/meɪk/', 'meaning_vi': 'Làm', 'phoneme_position': 'medial'},
            ],
            'aɪ': [
                {'word': 'My', 'ipa_transcription': '/maɪ/', 'meaning_vi': 'Của tôi', 'phoneme_position': 'final'},
                {'word': 'Five', 'ipa_transcription': '/faɪv/', 'meaning_vi': 'Năm', 'phoneme_position': 'medial'},
                {'word': 'Sky', 'ipa_transcription': '/skaɪ/', 'meaning_vi': 'Bầu trời', 'phoneme_position': 'final'},
            ],
            'ɔɪ': [
                {'word': 'Boy', 'ipa_transcription': '/bɔɪ/', 'meaning_vi': 'Con trai', 'phoneme_position': 'final'},
                {'word': 'Toy', 'ipa_transcription': '/tɔɪ/', 'meaning_vi': 'Đồ chơi', 'phoneme_position': 'final'},
                {'word': 'Voice', 'ipa_transcription': '/vɔɪs/', 'meaning_vi': 'Giọng nói', 'phoneme_position': 'medial'},
            ],
            'aʊ': [
                {'word': 'Now', 'ipa_transcription': '/naʊ/', 'meaning_vi': 'Bây giờ', 'phoneme_position': 'final'},
                {'word': 'Cow', 'ipa_transcription': '/kaʊ/', 'meaning_vi': 'Con bò', 'phoneme_position': 'final'},
                {'word': 'House', 'ipa_transcription': '/haʊs/', 'meaning_vi': 'Ngôi nhà', 'phoneme_position': 'medial'},
            ],
            'əʊ': [
                {'word': 'Go', 'ipa_transcription': '/ɡəʊ/', 'meaning_vi': 'Đi', 'phoneme_position': 'final'},
                {'word': 'Show', 'ipa_transcription': '/ʃəʊ/', 'meaning_vi': 'Chương trình', 'phoneme_position': 'final'},
                {'word': 'Home', 'ipa_transcription': '/həʊm/', 'meaning_vi': 'Nhà', 'phoneme_position': 'medial'},
            ],
            # Consonants - Plosives
            'p': [
                {'word': 'Pen', 'ipa_transcription': '/pen/', 'meaning_vi': 'Cây bút', 'phoneme_position': 'initial'},
                {'word': 'Soup', 'ipa_transcription': '/suːp/', 'meaning_vi': 'Súp', 'phoneme_position': 'final'},
                {'word': 'Pop', 'ipa_transcription': '/pɒp/', 'meaning_vi': 'Nổ, nhạc Pop', 'phoneme_position': 'initial'},
                {'word': 'Apple', 'ipa_transcription': '/ˈæpəl/', 'meaning_vi': 'Quả táo', 'phoneme_position': 'medial'},
            ],
            'b': [
                {'word': 'Bad', 'ipa_transcription': '/bæd/', 'meaning_vi': 'Xấu', 'phoneme_position': 'initial'},
                {'word': 'Web', 'ipa_transcription': '/web/', 'meaning_vi': 'Mạng lưới', 'phoneme_position': 'final'},
                {'word': 'Boat', 'ipa_transcription': '/bəʊt/', 'meaning_vi': 'Con thuyền', 'phoneme_position': 'initial'},
                {'word': 'Bob', 'ipa_transcription': '/bɒb/', 'meaning_vi': 'Tên Bob', 'phoneme_position': 'initial'},
            ],
            't': [
                {'word': 'Tea', 'ipa_transcription': '/tiː/', 'meaning_vi': 'Trà', 'phoneme_position': 'initial'},
                {'word': 'Cat', 'ipa_transcription': '/kæt/', 'meaning_vi': 'Con mèo', 'phoneme_position': 'final'},
                {'word': 'Top', 'ipa_transcription': '/tɒp/', 'meaning_vi': 'Đỉnh', 'phoneme_position': 'initial'},
            ],
            'd': [
                {'word': 'Dog', 'ipa_transcription': '/dɒɡ/', 'meaning_vi': 'Con chó', 'phoneme_position': 'initial'},
                {'word': 'Bad', 'ipa_transcription': '/bæd/', 'meaning_vi': 'Xấu', 'phoneme_position': 'final'},
                {'word': 'Day', 'ipa_transcription': '/deɪ/', 'meaning_vi': 'Ngày', 'phoneme_position': 'initial'},
            ],
            'k': [
                {'word': 'Cat', 'ipa_transcription': '/kæt/', 'meaning_vi': 'Con mèo', 'phoneme_position': 'initial'},
                {'word': 'Book', 'ipa_transcription': '/bʊk/', 'meaning_vi': 'Sách', 'phoneme_position': 'final'},
                {'word': 'Key', 'ipa_transcription': '/kiː/', 'meaning_vi': 'Chìa khóa', 'phoneme_position': 'initial'},
            ],
            'g': [
                {'word': 'Go', 'ipa_transcription': '/ɡəʊ/', 'meaning_vi': 'Đi', 'phoneme_position': 'initial'},
                {'word': 'Big', 'ipa_transcription': '/bɪɡ/', 'meaning_vi': 'To', 'phoneme_position': 'final'},
                {'word': 'Good', 'ipa_transcription': '/ɡʊd/', 'meaning_vi': 'Tốt', 'phoneme_position': 'initial'},
            ],
            # Fricatives
            'f': [
                {'word': 'Fish', 'ipa_transcription': '/fɪʃ/', 'meaning_vi': 'Con cá', 'phoneme_position': 'initial'},
                {'word': 'Off', 'ipa_transcription': '/ɒf/', 'meaning_vi': 'Tắt', 'phoneme_position': 'final'},
            ],
            'v': [
                {'word': 'Very', 'ipa_transcription': '/ˈveri/', 'meaning_vi': 'Rất', 'phoneme_position': 'initial'},
                {'word': 'Five', 'ipa_transcription': '/faɪv/', 'meaning_vi': 'Năm', 'phoneme_position': 'final'},
            ],
            'θ': [
                {'word': 'Think', 'ipa_transcription': '/θɪŋk/', 'meaning_vi': 'Nghĩ', 'phoneme_position': 'initial'},
                {'word': 'Thank', 'ipa_transcription': '/θæŋk/', 'meaning_vi': 'Cảm ơn', 'phoneme_position': 'initial'},
                {'word': 'Bath', 'ipa_transcription': '/bɑːθ/', 'meaning_vi': 'Bồn tắm', 'phoneme_position': 'final'},
            ],
            'ð': [
                {'word': 'This', 'ipa_transcription': '/ðɪs/', 'meaning_vi': 'Cái này', 'phoneme_position': 'initial'},
                {'word': 'That', 'ipa_transcription': '/ðæt/', 'meaning_vi': 'Cái đó', 'phoneme_position': 'initial'},
                {'word': 'Mother', 'ipa_transcription': '/ˈmʌðər/', 'meaning_vi': 'Mẹ', 'phoneme_position': 'medial'},
            ],
            's': [
                {'word': 'Sun', 'ipa_transcription': '/sʌn/', 'meaning_vi': 'Mặt trời', 'phoneme_position': 'initial'},
                {'word': 'Bus', 'ipa_transcription': '/bʌs/', 'meaning_vi': 'Xe buýt', 'phoneme_position': 'final'},
            ],
            'z': [
                {'word': 'Zoo', 'ipa_transcription': '/zuː/', 'meaning_vi': 'Sở thú', 'phoneme_position': 'initial'},
                {'word': 'Was', 'ipa_transcription': '/wɒz/', 'meaning_vi': 'Đã là', 'phoneme_position': 'final'},
            ],
            'ʃ': [
                {'word': 'Ship', 'ipa_transcription': '/ʃɪp/', 'meaning_vi': 'Con tàu', 'phoneme_position': 'initial'},
                {'word': 'Fish', 'ipa_transcription': '/fɪʃ/', 'meaning_vi': 'Con cá', 'phoneme_position': 'final'},
            ],
            'ʒ': [
                {'word': 'Vision', 'ipa_transcription': '/ˈvɪʒən/', 'meaning_vi': 'Tầm nhìn', 'phoneme_position': 'medial'},
                {'word': 'Measure', 'ipa_transcription': '/ˈmeʒər/', 'meaning_vi': 'Đo', 'phoneme_position': 'medial'},
            ],
        }
        
        return defaults.get(ipa_symbol, [])


class PhonemeChartView(TemplateView):
    """
    View for IPA phoneme chart reference.
    """
    template_name = 'pages/ipa_chart.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['page_title'] = 'Bảng IPA - Phiên âm Quốc tế'
        
        # Get all phonemes grouped by category
        context['vowels'] = Phoneme.objects.filter(
            category__category_type='vowel',
            is_active=True
        ).select_related('category')
        
        context['diphthongs'] = Phoneme.objects.filter(
            category__category_type='diphthong',
            is_active=True
        ).select_related('category')
        
        context['consonants'] = Phoneme.objects.filter(
            category__category_type='consonant',
            is_active=True
        ).select_related('category')
        
        return context



# =============================================================================
# PROTECTED VIEWS (Auth required)
# =============================================================================

class PronunciationProgressView(JWTRequiredMixin, TemplateView):
    """
    View for user's pronunciation learning progress.
    Requires authentication.
    """
    template_name = 'pages/pronunciation_progress.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['page_title'] = 'Tiến độ phát âm'
        context['user'] = self.request.jwt_user
        
        # TODO: Get user's pronunciation progress from database
        
        return context


# =============================================================================
# LESSON LIBRARY VIEWS (General lessons A1-C1)
# =============================================================================

class LessonLibraryView(TemplateView):
    """
    View for browsing all lessons (grammar, vocabulary, etc.).
    """
    template_name = 'pages/lesson_library.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['page_title'] = 'Thư viện bài học'
        
        from .models import Course, Lesson
        
        # Get all published courses
        context['courses'] = Course.objects.filter(
            status='published'
        ).order_by('cefr_level', 'order')
        
        return context


class LessonPlayerView(TemplateView):
    """
    View for lesson player (grammar, vocabulary lessons).
    """
    template_name = 'pages/lesson_player.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        from .models import Lesson
        
        lesson_slug = kwargs.get('slug')
        
        if lesson_slug:
            try:
                lesson = Lesson.objects.select_related(
                    'unit', 'unit__course'
                ).prefetch_related(
                    'sentences', 'flashcards'
                ).get(slug=lesson_slug, status='published')
                
                context['lesson'] = lesson
                context['page_title'] = lesson.title
                
            except Lesson.DoesNotExist:
                context['lesson'] = None
        
        return context
