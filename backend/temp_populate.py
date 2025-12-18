import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from apps.curriculum.models import Phoneme, MinimalPair

pairs_data = [
    ('/b/', '/v/', 'bat', 'vat', '/bæt/', '/væt/', 'chim con', 'bể'),
    ('/p/', '/b/', 'pat', 'bat', '/pæt/', '/bæt/', 'vuốt', 'chim con'),
    ('/t/', '/d/', 'tap', 'dab', '/tæp/', '/dæb/', 'gõ', 'chạm lẹ'),
    ('/k/', '/g/', 'cap', 'gap', '/kæp/', '/gæp/', 'mũ', 'khoảng trống'),
    ('/s/', '/z/', 'seal', 'zeal', '/siːl/', '/ziːl/', 'con hải cẩu', 'nhiệt tình'),
    ('/ʃ/', '/tʃ/', 'share', 'chair', '/ʃeə/', '/tʃeə/', 'chia sẻ', 'ghế'),
    ('/ð/', '/θ/', 'this', 'thin', '/ðɪs/', '/θɪn/', 'cái này', 'mỏng'),
    ('/l/', '/r/', 'light', 'right', '/laɪt/', '/raɪt/', 'ánh sáng', 'đúng'),
    ('/w/', '/v/', 'wine', 'vine', '/waɪn/', '/vaɪn/', 'rượu vang', 'cây nho'),
    ('/ɪ/', '/iː/', 'bit', 'beat', '/bɪt/', '/biːt/', 'miếng nhỏ', 'nhịp đập'),
    ('/ʊ/', '/uː/', 'book', 'boot', '/bʊk/', '/buːt/', 'sách', 'ủng'),
    ('/æ/', '/ʌ/', 'cat', 'cut', '/kæt/', '/kʌt/', 'mèo', 'cắt'),
    ('/ɔː/', '/ʌ/', 'got', 'gut', '/gɔːt/', '/gʌt/', 'có', 'ruột'),
    ('/e/', '/æ/', 'bed', 'bad', '/bed/', '/bæd/', 'giường', 'xấu'),
    ('/aɪ/', '/ɔɪ/', 'price', 'choice', '/praɪs/', '/tʃɔɪs/', 'giá', 'lựa chọn'),
]

created = 0
for p1_sym, p2_sym, w1, w2, w1_ipa, w2_ipa, w1_m, w2_m in pairs_data:
    try:
        p1 = Phoneme.objects.get(ipa_symbol=p1_sym)
        p2 = Phoneme.objects.get(ipa_symbol=p2_sym)
        MinimalPair.objects.create(
            phoneme_1=p1, phoneme_2=p2,
            word_1=w1, word_2=w2,
            word_1_ipa=w1_ipa, word_2_ipa=w2_ipa,
            word_1_meaning=w1_m, word_2_meaning=w2_m,
            difference_note_vi=f"Contrast: {p1_sym} vs {p2_sym}"
        )
        created += 1
        print(f'[OK] {p1_sym} vs {p2_sym}: {w1} vs {w2}')
    except Exception as e:
        print(f'[ERROR] {p1_sym} vs {p2_sym}: {e}')

print(f'\nComplete! Created: {created}')
