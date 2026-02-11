Prompt: "Đóng vai một giáo viên tiếng Anh hài hước và sáng tạo. Tôi muốn bạn trích xuất kiến thức về chủ đề [TÊN CHỦ ĐỀ] nhưng KHÔNG được viết theo kiểu sách giáo khoa khô khan.

Hãy chuyển đổi nội dung thành cấu trúc JSON với yêu cầu đặc biệt sau:

    analogy (Phép so sánh): Hãy so sánh cấu trúc ngữ pháp này với một khái niệm đời thường dễ hiểu (Ví dụ: 'Động từ to be giống như dấu bằng (=) trong toán học').

    memory_hook (Mẹo nhớ khắc cốt ghi tâm): Một câu nói ngắn gọn, vần điệu hoặc hài hước để người học nhớ quy tắc ngay lập tức.

    emotional_context (Ngữ cảnh cảm xúc): Trong ví dụ, hãy thêm tình huống cụ thể (vui, buồn, ngạc nhiên) thay vì chỉ là câu nói suông.

Trả về định dạng JSON sau (chỉ trả về JSON):

{
  "topic": "Present Continuous Tense",
  "level": "A1",
  "description": "Thì hiện tại tiếp diễn.",
  "analogy": "Thì hiện tại tiếp diễn giống như bạn đang Livestream trên Facebook vậy. Mọi thứ đang diễn ra NGAY LÚC NÀY trước mắt khán giả.",
  "rules": [
    {
      "title": "Cấu trúc khẳng định: Be + V-ing",
      "explanation": "Chủ ngữ + am/is/are + Động từ thêm đuôi ing.",
      "memory_hook": "Muốn 'tiếp diễn' thì phải có 'Be' đi kèm với cái 'Đuôi' (ing). Thiếu một trong hai là sai!",
      "examples": [
        {
          "sentence": "Look! The baby is sleeping like an angel.",
          "translation": "Nhìn kìa! Em bé đang ngủ như một thiên thần.",
          "context": "Nói khẽ thôi để không đánh thức em bé (Tình huống nhẹ nhàng).",
          "highlight": "is sleeping"
        }
      ]
    }
  ]
}
Hãy làm điều này cho chủ đề tôi yêu cầu."


from django.db import models
from django.utils.text import slugify
from django.utils.translation import gettext_lazy as _

class GrammarTopic(models.Model):
    """
    Model quản lý Chủ đề Ngữ pháp lớn (Lesson).
    Ví dụ: Thì Hiện tại đơn, Câu điều kiện loại 1...
    """
    class Level(models.TextChoices):
        A1 = 'A1', _('Beginner - A1')
        A2 = 'A2', _('Elementary - A2')
        B1 = 'B1', _('Intermediate - B1')
        B2 = 'B2', _('Upper Intermediate - B2')
        C1 = 'C1', _('Advanced - C1')

    # --- 1. ĐỊNH DANH & CẤU TRÚC ---
    title = models.CharField(max_length=200, help_text="Tên chủ đề (VD: Thì Hiện tại đơn)")
    slug = models.SlugField(unique=True, blank=True, help_text="URL thân thiện (VD: thi-hien-tai-don)")
    level = models.CharField(max_length=2, choices=Level.choices, default=Level.A1)
    order = models.PositiveIntegerField(default=0, help_text="Thứ tự hiển thị trong lộ trình học")
    is_published = models.BooleanField(default=True, help_text="Bật/Tắt hiển thị bài học này")

    # --- 2. TRẢI NGHIỆM HỌC TẬP (PSYCHOLOGY & VISUAL) ---
    icon = models.CharField(
        max_length=50, 
        default="📚", 
        help_text="Emoji hoặc mã class FontAwesome để làm icon đại diện"
    )
    illustration = models.ImageField(
        upload_to='grammar/illustrations/', 
        blank=True, 
        null=True,
        help_text="Ảnh minh họa vui nhộn cho bài học (Hero Image)"
    )
    
    # --- 3. NỘI DUNG CỐT LÕI (THE HOOK) ---
    description = models.TextField(help_text="Giới thiệu ngắn gọn (Meta description cho SEO)")
    
    # [QUAN TRỌNG] Phép so sánh/ẩn dụ giúp não bộ "móc nối" kiến thức
    analogy = models.TextField(
        blank=True, 
        verbose_name="Phép ẩn dụ (Analogy)",
        help_text="VD: 'Động từ tobe giống như dấu bằng (=) trong toán học'. Giúp học viên dễ hình dung."
    )
    
    # Ứng dụng thực tế (Tại sao tôi phải học cái này?)
    real_world_use = models.TextField(
        blank=True,
        verbose_name="Ứng dụng thực tế",
        help_text="VD: 'Dùng để giới thiệu bản thân, kể về thói quen hàng ngày'..."
    )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['level', 'order']
        verbose_name = "Chủ đề Ngữ pháp"
        verbose_name_plural = "Danh sách Chủ đề Ngữ pháp"

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.title)
        super().save(*args, **kwargs)

    def __str__(self):
        return f"[{self.level}] {self.title}"


class GrammarRule(models.Model):
    """
    Các quy tắc nhỏ trong một chủ đề.
    VD: Trong 'Hiện tại đơn' có quy tắc: 'Động từ thường', 'Động từ Tobe', 'Quy tắc thêm s/es'
    """
    topic = models.ForeignKey(GrammarTopic, on_delete=models.CASCADE, related_name='rules')
    title = models.CharField(max_length=255, help_text="Tên quy tắc (VD: Công thức khẳng định)")
    
    # Công thức (để hiển thị đóng khung nổi bật)
    formula = models.CharField(
        max_length=500, 
        blank=True, 
        help_text="VD: S + V(s/es) + Object"
    )
    
    # Giải thích chi tiết (Hỗ trợ HTML)
    explanation = models.TextField(help_text="Giải thích cặn kẽ cách dùng.")
    
    # [QUAN TRỌNG] Mẹo nhớ nhanh
    memory_hook = models.TextField(
        blank=True, 
        verbose_name="Mẹo nhớ (Sticky Note)",
        help_text="Câu thần chú ngắn gọn, hài hước để nhớ quy tắc này."
    )
    
    is_exception = models.BooleanField(
        default=False, 
        help_text="Đánh dấu nếu đây là trường hợp ngoại lệ (sẽ hiển thị cảnh báo đỏ)"
    )
    order = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ['order']
        verbose_name = "Quy tắc ngữ pháp"

    def __str__(self):
        return f"{self.topic.title} - {self.title}"


class GrammarExample(models.Model):
    """
    Ví dụ minh họa cho từng quy tắc
    """
    rule = models.ForeignKey(GrammarRule, on_delete=models.CASCADE, related_name='examples')
    
    # Câu ví dụ
    sentence = models.CharField(max_length=500, help_text="Câu tiếng Anh chuẩn")
    translation = models.CharField(max_length=500, help_text="Dịch nghĩa tiếng Việt")
    
    # [QUAN TRỌNG] Ngữ cảnh cảm xúc
    context = models.CharField(
        max_length=255, 
        blank=True, 
        help_text="Tình huống cụ thể (VD: Khi đang ngạc nhiên, Khi đang thì thầm...)"
    )
    
    # Highlight từ khóa
    highlight = models.CharField(
        max_length=100, 
        blank=True, 
        help_text="Từ/Cụm từ cần tô màu trong câu (VD: 'goes', 'is sleeping')"
    )
    
    audio_url = models.URLField(blank=True, null=True, help_text="Link file âm thanh (nếu có)")

    def __str__(self):
        return self.sentence
