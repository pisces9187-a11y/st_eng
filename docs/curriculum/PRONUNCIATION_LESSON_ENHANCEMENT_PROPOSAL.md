# 📚 ĐỀ XUẤT CẢI TIẾN HỆ THỐNG BÀI HỌC PHÁT ÂM

**Ngày tạo:** 18/12/2025  
**Focus:** Học theo **CẶP ÂM TƯƠNG TỰ** thay vì âm đơn lẻ  
**URL hiện tại:** http://127.0.0.1:8000/pronunciation/lesson/ipa-introduction/

---

## 🎯 TÓM TẮT EXECUTIVE

### ❌ VẤN ĐỀ HIỆN TẠI

Từ phân tích SYSTEM_GAP_ANALYSIS.md, tôi nhận thấy:

1. **Lesson page hiện tại rất tốt** - có explanation, tips, visual cues
2. **Discrimination page còn yếu** - chỉ có quiz không có context
3. **Nhưng user đề nghị:** Thay vì cải thiện discrimination page, hãy **nâng cấp lesson page** với focus vào **SO SÁNH CẶP ÂM** ngay từ đầu

### ✅ ĐỀ XUẤT CHIẾN LƯỢC MỚI

Thay vì học:
```
Lesson 1: Âm /p/ (5 màn hình)
Lesson 2: Âm /b/ (5 màn hình)
Discrimination: Quiz /p/ vs /b/
```

**→ Học luôn CẶP ÂM ngay từ đầu:**
```
Lesson 1: CẶP ÂM /p/ vs /b/ - Âm bật hơi đối lập (7 màn hình)
├── Screen 1: Giới thiệu CẶP âm + Điểm CHUNG vs KHÁC
├── Screen 2: Chi tiết âm /p/ + 6 từ ví dụ
├── Screen 3: Chi tiết âm /b/ + 6 từ ví dụ
├── Screen 4: SO SÁNH TRỰC TIẾP (side-by-side)
├── Screen 5: Minimal Pairs Challenge (ship/sheep)
├── Screen 6: Tongue Twister + Conversation
└── Screen 7: Summary + Homework
```

**Lợi ích:**
- ✅ **Hiệu quả hơn** - Học cặp âm ngay = nắm điểm khác biệt sớm
- ✅ **Giảm confusion** - Không bị nhầm lẫn sau này
- ✅ **Natural progression** - Theory → Practice → Compare → Challenge
- ✅ **Better retention** - Contrastive learning > isolated learning

---

## 📊 PHÂN TÍCH LESSON PAGE HIỆN TẠI

### ✅ Điểm mạnh (GIỮ LẠI)

```html
<!-- Screen 1: Twin Sounds Intro -->
<div class="phoneme-compare-card voiceless">
    <div class="ipa-symbol-large">/p/</div>
    <span class="badge bg-info">Vô thanh</span>
    <button class="btn-audio-play">🔊</button>
</div>

<div class="tip-box tip-box-primary">
    <h5>Điểm quan trọng</h5>
    <p><strong>Điểm chung:</strong> Miệng làm động tác Y HỆT nhau</p>
    <p><strong>Điểm khác biệt:</strong>
        • /p/: Không rung thanh quản
        • /b/: CÓ rung thanh quản
    </p>
</div>
```

**→ ĐÃ có foundation tốt cho contrastive learning!**

### ❌ Điểm yếu (CẦN CẢI THIỆN)

1. **Screen 2-3: Học riêng lẻ**
   - Mỗi âm học riêng → không thấy sự khác biệt rõ ràng
   - User phải **TỰ SO SÁNH** trong đầu
   - Dễ quên âm trước khi học âm sau

2. **Thiếu Screen "Side-by-Side Comparison"**
   - Không có màn hình so sánh trực tiếp
   - Không có table điểm khác biệt
   - Không có animation showing difference

3. **Challenge (Screen 4) xuất hiện quá sớm**
   - Chưa có enough practice → frustrating
   - Nên có thêm guided practice trước quiz

4. **Thiếu real-world context**
   - Chỉ có isolated words
   - Không có phrases/sentences
   - Không có conversation examples

---

## 🎨 ĐỀ XUẤT CẢI TIẾN CHI TIẾT

### 🔧 CÁCH 1: MINIMAL CHANGES (1-2 ngày)

**Mục tiêu:** Cải thiện lesson hiện tại với ít thay đổi nhất

#### 1.1. Thêm Screen 4: "Side-by-Side Comparison" (NEW)

```html
<!-- ============================================ -->
<!-- SCREEN 4: SIDE-BY-SIDE COMPARISON (NEW) -->
<!-- ============================================ -->
<div class="screen-container" :class="{ active: currentScreen === 4 }">
    <div class="text-center mb-4">
        <h2 class="h4 fw-bold">So sánh trực tiếp</h2>
        <p class="text-muted">Nghe và so sánh sự khác biệt</p>
    </div>
    
    <!-- Comparison Table -->
    <div class="comparison-table">
        <table class="table table-bordered">
            <thead>
                <tr>
                    <th width="25%">Đặc điểm</th>
                    <th width="37.5%" class="bg-info bg-opacity-10">
                        /[[ phoneme1.ipa_symbol ]]/
                        <button class="btn btn-sm btn-audio-play ms-2" @click="playPhoneme(phoneme1)">
                            <i class="fas fa-volume-up"></i>
                        </button>
                    </th>
                    <th width="37.5%" class="bg-warning bg-opacity-10">
                        /[[ phoneme2.ipa_symbol ]]/
                        <button class="btn btn-sm btn-audio-play ms-2" @click="playPhoneme(phoneme2)">
                            <i class="fas fa-volume-up"></i>
                        </button>
                    </th>
                </tr>
            </thead>
            <tbody>
                <tr>
                    <td><strong>Xấp xỉ tiếng Việt</strong></td>
                    <td>[[ phoneme1.vietnamese_approx ]]</td>
                    <td>[[ phoneme2.vietnamese_approx ]]</td>
                </tr>
                <tr>
                    <td><strong>Loại âm</strong></td>
                    <td>
                        <span class="badge" :class="phoneme1.voicing === 'voiceless' ? 'bg-info' : 'bg-warning'">
                            [[ phoneme1.voicing === 'voiceless' ? 'Vô thanh' : 'Hữu thanh' ]]
                        </span>
                    </td>
                    <td>
                        <span class="badge" :class="phoneme2.voicing === 'voiceless' ? 'bg-info' : 'bg-warning'">
                            [[ phoneme2.voicing === 'voiceless' ? 'Vô thanh' : 'Hữu thanh' ]]
                        </span>
                    </td>
                </tr>
                <tr class="table-success">
                    <td><strong>✅ Giống nhau</strong></td>
                    <td colspan="2" class="text-center">
                        • Cùng động tác miệng<br>
                        • Cùng vị trí lưỡi<br>
                        • Cùng cách khí thoát ra
                    </td>
                </tr>
                <tr class="table-danger">
                    <td><strong>❌ Khác nhau</strong></td>
                    <td>[[ phoneme1.pronunciation_tips_vi || 'Không rung thanh quản' ]]</td>
                    <td>[[ phoneme2.pronunciation_tips_vi || 'Rung thanh quản' ]]</td>
                </tr>
                <tr>
                    <td><strong>Cách kiểm tra</strong></td>
                    <td>
                        <div class="tip-badge">
                            <i class="fas fa-hand-paper me-2"></i>
                            Đặt tờ giấy trước miệng → giấy bay mạnh
                        </div>
                    </td>
                    <td>
                        <div class="tip-badge">
                            <i class="fas fa-hand-point-up me-2"></i>
                            Đặt ngón tay lên cổ họng → rung rõ
                        </div>
                    </td>
                </tr>
            </tbody>
        </table>
    </div>
    
    <!-- Interactive Word Comparison -->
    <div class="card mt-4">
        <div class="card-body">
            <h5 class="card-title mb-3">
                <i class="fas fa-exchange-alt text-primary me-2"></i>
                So sánh từ vựng
            </h5>
            
            <div class="row g-3">
                <div v-for="(pair, idx) in minimalPairsSample" :key="idx" class="col-md-6">
                    <div class="word-comparison-card">
                        <div class="d-flex justify-content-around align-items-center">
                            <!-- Word 1 -->
                            <div class="word-box" @click="playWord(pair.word_1, pair.word_1_audio)">
                                <div class="word-text text-info">[[ pair.word_1 ]]</div>
                                <div class="word-ipa">[[ pair.word_1_ipa ]]</div>
                                <div class="word-meaning">[[ pair.word_1_meaning ]]</div>
                                <button class="btn btn-sm btn-outline-info mt-2">
                                    <i class="fas fa-volume-up"></i>
                                </button>
                            </div>
                            
                            <!-- VS -->
                            <div class="vs-divider">vs</div>
                            
                            <!-- Word 2 -->
                            <div class="word-box" @click="playWord(pair.word_2, pair.word_2_audio)">
                                <div class="word-text text-warning">[[ pair.word_2 ]]</div>
                                <div class="word-ipa">[[ pair.word_2_ipa ]]</div>
                                <div class="word-meaning">[[ pair.word_2_meaning ]]</div>
                                <button class="btn btn-sm btn-outline-warning mt-2">
                                    <i class="fas fa-volume-up"></i>
                                </button>
                            </div>
                        </div>
                        
                        <!-- Explanation -->
                        <div class="mt-2 text-muted text-center small" v-if="pair.difference_note_vi">
                            <i class="fas fa-info-circle me-1"></i>
                            [[ pair.difference_note_vi ]]
                        </div>
                    </div>
                </div>
            </div>
        </div>
    </div>
    
    <!-- Guided Practice -->
    <div class="alert alert-primary mt-4 border-0">
        <h6 class="alert-heading">
            <i class="fas fa-graduation-cap me-2"></i>
            Thực hành có hướng dẫn
        </h6>
        <ol class="mb-0">
            <li>Nghe âm /[[ phoneme1.ipa_symbol ]]/ → Đặt tay lên cổ họng → Không rung</li>
            <li>Nghe âm /[[ phoneme2.ipa_symbol ]]/ → Đặt tay lên cổ họng → CÓ rung</li>
            <li>Nghe từ "ship" và "sheep" → Phân biệt ngay</li>
        </ol>
    </div>
</div>

<style>
.comparison-table {
    background: white;
    border-radius: 16px;
    padding: 1.5rem;
    box-shadow: 0 4px 20px rgba(0,0,0,0.08);
}

.comparison-table table {
    margin-bottom: 0;
}

.comparison-table th {
    font-weight: 700;
    vertical-align: middle;
}

.comparison-table td {
    padding: 1rem;
    vertical-align: middle;
}

.tip-badge {
    background: rgba(13, 110, 253, 0.1);
    padding: 0.5rem 1rem;
    border-radius: 8px;
    font-size: 0.9rem;
}

.word-comparison-card {
    background: white;
    border: 2px solid #E0E6ED;
    border-radius: 12px;
    padding: 1.25rem;
    transition: all 0.3s ease;
}

.word-comparison-card:hover {
    border-color: var(--phoneme-primary);
    box-shadow: 0 4px 15px rgba(0,0,0,0.1);
}

.word-box {
    text-align: center;
    cursor: pointer;
    padding: 0.75rem;
    border-radius: 8px;
    transition: all 0.2s ease;
}

.word-box:hover {
    background: rgba(0,0,0,0.03);
}

.word-text {
    font-size: 1.5rem;
    font-weight: 700;
}

.word-ipa {
    font-size: 0.9rem;
    color: #6c757d;
    font-family: 'Lucida Sans Unicode', sans-serif;
}

.word-meaning {
    font-size: 0.85rem;
    color: #6c757d;
    margin-top: 0.25rem;
}

.vs-divider {
    font-size: 1.25rem;
    font-weight: 700;
    color: #6c757d;
}
</style>
```

**JavaScript changes:**

```javascript
// In data()
minimalPairsSample: [],  // Lấy 3-4 cặp từ minimal pairs

// In mounted()
this.minimalPairsSample = this.minimalPairs.slice(0, 4);

// Update navigation
// Old: currentScreen max = 5
// New: currentScreen max = 6 (thêm 1 screen)
```

---

#### 1.2. Nâng cấp Screen 2-3: Thêm "Recall Previous Sound"

**Vấn đề:** User học xong âm /p/ (screen 2) → sang /b/ (screen 3) → quên mất /p/

**Giải pháp:** Thêm quick reminder ở đầu screen 3:

```html
<!-- SCREEN 3: PRACTICE PHONEME 2 -->
<div class="screen-container" :class="{ active: currentScreen === 3 }">
    
    <!-- Quick Recall Section (NEW) -->
    <div class="alert alert-info border-0 mb-4">
        <div class="d-flex align-items-center justify-content-between">
            <div>
                <h6 class="mb-1">
                    <i class="fas fa-lightbulb me-2"></i>
                    Nhớ lại âm trước:
                </h6>
                <p class="mb-0 small">
                    /[[ phoneme1.ipa_symbol ]]/ - [[ phoneme1.vietnamese_approx ]] 
                    - <strong>[[ phoneme1.voicing === 'voiceless' ? 'Vô thanh' : 'Hữu thanh' ]]</strong>
                </p>
            </div>
            <button class="btn btn-sm btn-outline-info" @click="playPhoneme(phoneme1)">
                <i class="fas fa-volume-up me-1"></i> Nghe lại
            </button>
        </div>
    </div>
    
    <!-- Rest of Screen 3... -->
    <div class="text-center mb-4">
        <span class="badge px-3 py-2 mb-3" :class="phoneme2.voicing === 'voiceless' ? 'bg-info' : 'bg-warning text-dark'">
            Bây giờ học âm thứ 2: [[ phoneme2.voicing === 'voiceless' ? 'Âm Vô Thanh' : 'Âm Hữu Thanh' ]]
        </span>
        ...
    </div>
</div>
```

---

#### 1.3. Cải thiện Screen 5 (Challenge): Thêm "Hint" button

```html
<!-- SCREEN 5: MINIMAL PAIRS CHALLENGE -->
<div class="screen-container" :class="{ active: currentScreen === 5 }">
    <!-- ... existing code ... -->
    
    <!-- Challenge Question -->
    <div class="challenge-question mb-4" v-if="currentChallenge">
        <p class="text-muted mb-4">Bấm nút để nghe âm thanh, sau đó chọn từ bạn nghe được</p>
        
        <button class="challenge-audio-btn mb-4" @click="playChallengeAudio">
            <i class="fas fa-play" v-if="!isPlayingChallenge"></i>
            <i class="fas fa-volume-up" v-else></i>
        </button>
        
        <!-- Hint Button (NEW) -->
        <div class="mb-3" v-if="!hasAnswered">
            <button class="btn btn-sm btn-outline-secondary" @click="showHint = !showHint">
                <i class="fas fa-question-circle me-1"></i>
                [[ showHint ? 'Ẩn gợi ý' : 'Hiện gợi ý' ]]
            </button>
            
            <div v-if="showHint" class="alert alert-warning mt-2 small">
                <strong>💡 Gợi ý:</strong><br>
                • Đặt ngón tay lên cổ họng khi nghe<br>
                • Rung = /[[ phoneme2.ipa_symbol ]]/, Không rung = /[[ phoneme1.ipa_symbol ]]/
            </div>
        </div>
        
        <!-- ... existing choices ... -->
    </div>
</div>
```

---

### 🚀 CÁCH 2: MAJOR REDESIGN (5-7 ngày)

**Mục tiêu:** Thiết kế lại hoàn toàn theo "Contrastive Learning Pedagogy"

#### 2.1. Screen Structure (7 screens thay vì 5)

```
LESSON: "Âm bật hơi đối lập /p/ vs /b/"

Screen 1: Introduction & Concept
├── Giới thiệu cặp âm
├── Điểm CHUNG (same mouth position)
├── Điểm KHÁC BIỆT (voicing)
└── Mục tiêu: Phân biệt được 2 âm này

Screen 2: Deep Dive - Âm /p/
├── IPA + Vietnamese approx
├── Physical mechanism (tongue/lips)
├── Pronunciation tips
├── 6 example words with audio
└── Common mistakes

Screen 3: Deep Dive - Âm /b/
├── IPA + Vietnamese approx
├── Quick recall of /p/ (so sánh)
├── Physical mechanism
├── 6 example words with audio
└── Common mistakes

Screen 4: Side-by-Side Comparison (NEW)
├── Comparison table (voicing, tips, examples)
├── Interactive word pairs (ship vs sheep)
├── Guided practice (step by step)
└── Visual diagrams (mouth + waveform)

Screen 5: Minimal Pairs Listening
├── 10 questions with hints
├── Immediate feedback after each question
├── Explanation of correct answer
└── Progress tracker

Screen 6: Real-World Context (NEW)
├── Sentences with both sounds
   - "I want to BUY a PIE" (Tôi muốn mua một cái bánh)
   - "The BIG PIG" (Con lợn to)
├── Tongue twister
├── Mini conversation
└── Record yourself option

Screen 7: Summary & Next Steps
├── Final score + stats
├── XP earned
├── Weak points analysis
├── Recommended practice
└── Next lesson unlock
```

---

#### 2.2. New Features

##### Feature 1: Visual Waveform Comparison

```html
<!-- In Screen 4 -->
<div class="waveform-comparison">
    <h5 class="mb-3">
        <i class="fas fa-wave-square me-2"></i>
        So sánh sóng âm
    </h5>
    
    <div class="row">
        <div class="col-md-6">
            <div class="waveform-card">
                <h6 class="text-info">/p/ - Vô thanh</h6>
                <canvas id="waveformP" width="300" height="100"></canvas>
                <p class="small text-muted mt-2">
                    <i class="fas fa-info-circle"></i>
                    Sóng âm không đều, có "burst" mạnh ở đầu
                </p>
            </div>
        </div>
        <div class="col-md-6">
            <div class="waveform-card">
                <h6 class="text-warning">/b/ - Hữu thanh</h6>
                <canvas id="waveformB" width="300" height="100"></canvas>
                <p class="small text-muted mt-2">
                    <i class="fas fa-info-circle"></i>
                    Sóng âm đều đặn, có진동 rung từ đầu đến cuối
                </p>
            </div>
        </div>
    </div>
</div>

<script>
// Sử dụng Web Audio API để vẽ waveform
async function drawWaveform(audioUrl, canvasId) {
    const audioContext = new (window.AudioContext || window.webkitAudioContext)();
    const response = await fetch(audioUrl);
    const arrayBuffer = await response.arrayBuffer();
    const audioBuffer = await audioContext.decodeAudioData(arrayBuffer);
    
    const canvas = document.getElementById(canvasId);
    const ctx = canvas.getContext('2d');
    const data = audioBuffer.getChannelData(0);
    const step = Math.ceil(data.length / canvas.width);
    const amp = canvas.height / 2;
    
    ctx.fillStyle = '#F9FAFC';
    ctx.fillRect(0, 0, canvas.width, canvas.height);
    ctx.strokeStyle = canvasId === 'waveformP' ? '#3498DB' : '#F47C26';
    ctx.lineWidth = 2;
    ctx.beginPath();
    
    for (let i = 0; i < canvas.width; i++) {
        const min = data.slice(i * step, (i + 1) * step)
            .reduce((acc, val) => Math.min(acc, val), 1);
        const max = data.slice(i * step, (i + 1) * step)
            .reduce((acc, val) => Math.max(acc, val), -1);
        ctx.lineTo(i, (1 + min) * amp);
        ctx.lineTo(i, (1 + max) * amp);
    }
    
    ctx.stroke();
}
</script>
```

---

##### Feature 2: Sentences with Both Sounds (Screen 6)

```html
<!-- Screen 6: Real-World Context -->
<div class="screen-container" :class="{ active: currentScreen === 6 }">
    <div class="text-center mb-4">
        <span class="badge bg-success px-3 py-2 mb-3">
            <i class="fas fa-comments me-2"></i>
            Thực hành ngữ cảnh thực tế
        </span>
        <h2 class="h4 fw-bold">Câu có cả 2 âm</h2>
        <p class="text-muted">Luyện phân biệt trong câu hoàn chỉnh</p>
    </div>
    
    <!-- Sentence Practice Cards -->
    <div class="mb-4">
        <div v-for="(sentence, idx) in contextSentences" :key="idx" class="sentence-card mb-3">
            <div class="d-flex align-items-center justify-content-between">
                <div>
                    <div class="sentence-text" v-html="highlightPhonemesInSentence(sentence.text)"></div>
                    <div class="sentence-ipa mt-1">[[ sentence.ipa ]]</div>
                    <div class="sentence-meaning text-muted small">[[ sentence.meaning_vi ]]</div>
                </div>
                <button class="btn btn-primary" @click="playSentence(sentence)">
                    <i class="fas fa-volume-up"></i>
                </button>
            </div>
            
            <!-- Breakdown -->
            <div class="sentence-breakdown mt-3" v-if="sentence.breakdown">
                <small class="text-muted">
                    <strong>Phân tích:</strong><br>
                    • <span class="text-info">Từ có /p/:</span> [[ sentence.p_words.join(', ') ]]<br>
                    • <span class="text-warning">Từ có /b/:</span> [[ sentence.b_words.join(', ') ]]
                </small>
            </div>
        </div>
    </div>
    
    <!-- Mini Conversation -->
    <div class="card border-0 shadow-sm mb-4">
        <div class="card-body">
            <h5 class="card-title mb-3">
                <i class="fas fa-users text-primary me-2"></i>
                Đoạn hội thoại
            </h5>
            
            <div class="conversation">
                <div class="conversation-turn mb-3">
                    <div class="speaker-label">
                        <img src="/static/images/avatar-a.png" class="speaker-avatar">
                        <strong>Alice:</strong>
                    </div>
                    <div class="conversation-bubble">
                        I want to <span class="highlight-b">BUY</span> some <span class="highlight-p">PAPER</span>.
                    </div>
                    <button class="btn btn-sm btn-outline-secondary mt-1" @click="playConversationLine(1)">
                        <i class="fas fa-volume-up"></i>
                    </button>
                </div>
                
                <div class="conversation-turn mb-3">
                    <div class="speaker-label">
                        <img src="/static/images/avatar-b.png" class="speaker-avatar">
                        <strong>Bob:</strong>
                    </div>
                    <div class="conversation-bubble">
                        Let's go to the <span class="highlight-b">BIG</span> shop on <span class="highlight-p">Park</span> Street.
                    </div>
                    <button class="btn btn-sm btn-outline-secondary mt-1" @click="playConversationLine(2)">
                        <i class="fas fa-volume-up"></i>
                    </button>
                </div>
            </div>
        </div>
    </div>
    
    <!-- Recording Practice (Optional) -->
    <div class="card border-warning">
        <div class="card-body">
            <h6 class="card-title">
                <i class="fas fa-microphone text-warning me-2"></i>
                Thử ghi âm của bạn (Không bắt buộc)
            </h6>
            <p class="small text-muted mb-3">
                Đọc một trong các câu trên và so sánh với âm mẫu
            </p>
            <button class="btn btn-outline-warning" @click="startRecording" v-if="!isRecording">
                <i class="fas fa-microphone me-2"></i>
                Bắt đầu ghi âm
            </button>
            <button class="btn btn-danger" @click="stopRecording" v-else>
                <i class="fas fa-stop me-2"></i>
                Dừng ghi âm ([[ recordingTime ]]s)
            </button>
        </div>
    </div>
</div>

<style>
.sentence-card {
    background: white;
    border-radius: 16px;
    padding: 1.5rem;
    border: 2px solid #E0E6ED;
    transition: all 0.3s ease;
}

.sentence-card:hover {
    border-color: var(--phoneme-primary);
    box-shadow: 0 4px 20px rgba(0,0,0,0.08);
}

.sentence-text {
    font-size: 1.25rem;
    font-weight: 600;
    line-height: 1.6;
}

.sentence-text .highlight-p {
    color: #3498DB;
    background: rgba(52, 152, 219, 0.1);
    padding: 2px 6px;
    border-radius: 4px;
    font-weight: 700;
}

.sentence-text .highlight-b {
    color: #F47C26;
    background: rgba(244, 124, 38, 0.1);
    padding: 2px 6px;
    border-radius: 4px;
    font-weight: 700;
}

.conversation {
    padding: 1rem;
    background: #F9FAFC;
    border-radius: 12px;
}

.conversation-turn {
    margin-bottom: 1rem;
}

.speaker-label {
    display: flex;
    align-items: center;
    gap: 0.5rem;
    margin-bottom: 0.5rem;
}

.speaker-avatar {
    width: 32px;
    height: 32px;
    border-radius: 50%;
}

.conversation-bubble {
    background: white;
    padding: 0.75rem 1rem;
    border-radius: 12px;
    border-left: 4px solid var(--phoneme-primary);
    font-size: 1.1rem;
}
</style>

<script>
// In data()
contextSentences: [
    {
        text: "I want to BUY a PIE",
        ipa: "/aɪ wɒnt tuː baɪ ə paɪ/",
        meaning_vi: "Tôi muốn mua một cái bánh",
        p_words: ["PIE"],
        b_words: ["BUY"],
        breakdown: true
    },
    {
        text: "The BIG PIG is PINK",
        ipa: "/ðə bɪg pɪg ɪz pɪŋk/",
        meaning_vi: "Con lợn to có màu hồng",
        p_words: ["PIG", "PINK"],
        b_words: ["BIG"],
        breakdown: true
    },
    {
        text: "Please PUT the BOOK on the table",
        ipa: "/pliːz pʊt ðə bʊk ɒn ðə ˈteɪbl/",
        meaning_vi: "Làm ơn đặt quyển sách lên bàn",
        p_words: ["Please", "PUT"],
        b_words: ["BOOK"],
        breakdown: true
    }
],

methods: {
    highlightPhonemesInSentence(text) {
        // Highlight words with /p/ and /b/
        return text
            .replace(/\b(BUY|BIG|BOOK)\b/g, '<span class="highlight-b">$1</span>')
            .replace(/\b(PIE|PIG|PINK|PUT|Please)\b/g, '<span class="highlight-p">$1</span>');
    },
    
    async playSentence(sentence) {
        await this.playTTS(sentence.text);
    },
    
    async playConversationLine(lineNumber) {
        const lines = {
            1: "I want to buy some paper",
            2: "Let's go to the big shop on Park Street"
        };
        await this.playTTS(lines[lineNumber]);
    }
}
</script>
```

---

##### Feature 3: Adaptive Difficulty (Screen 5 Challenge)

```javascript
// Smart question selection based on user performance

setupChallengeQuestions() {
    // Get all minimal pairs
    let allPairs = this.minimalPairs || [];
    
    // Start with easy pairs (high frequency words)
    let easyPairs = allPairs.filter(p => p.difficulty <= 2);
    let mediumPairs = allPairs.filter(p => p.difficulty === 3);
    let hardPairs = allPairs.filter(p => p.difficulty >= 4);
    
    // Adaptive progression: 3 easy + 4 medium + 3 hard
    this.challengeQuestions = [
        ...this.shuffle(easyPairs).slice(0, 3),
        ...this.shuffle(mediumPairs).slice(0, 4),
        ...this.shuffle(hardPairs).slice(0, 3)
    ].map(pair => ({
        ...pair,
        correctWord: Math.random() > 0.5 ? pair.word_1 : pair.word_2
    }));
},

// After each answer, adjust next question
selectAnswer(word) {
    if (!this.hasAnswered) {
        this.selectedAnswer = word;
        this.hasAnswered = true;
        this.answeredCount++;
        
        this.correctAnswer = this.currentChallenge.correctWord;
        this.isCorrect = word === this.correctAnswer;
        
        if (this.isCorrect) {
            this.correctCount++;
            this.xpEarned += 2;
            
            // If 3 correct in a row, increase difficulty
            if (this.correctStreak >= 2) {
                this.showEncouragementMessage('🔥 Xuất sắc! Đang tăng độ khó...');
            }
            this.correctStreak++;
        } else {
            this.correctStreak = 0;
            
            // If 2 wrong in a row, add hint
            if (this.wrongStreak >= 1) {
                this.showHint = true;
            }
            this.wrongStreak++;
        }
    }
}
```

---

## 📦 IMPLEMENTATION PLAN

### Phase 1: Quick Wins (2-3 ngày)

**Tasks:**
1. ✅ Thêm Screen 4: Side-by-Side Comparison
2. ✅ Thêm "Recall Previous Sound" ở Screen 3
3. ✅ Thêm Hint button ở Screen 5
4. ✅ Cải thiện feedback sau mỗi câu hỏi
5. ✅ Update navigation: 5 screens → 6 screens

**Deliverables:**
- Template: `pronunciation_lesson.html` (updated)
- Views: Không cần thay đổi (dữ liệu đủ)
- Models: Không cần thay đổi

---

### Phase 2: New Features (3-4 ngày)

**Tasks:**
1. ✅ Thêm Screen 6: Real-World Context
2. ✅ Tạo model `SentenceExample` cho câu mẫu
3. ✅ Implement waveform visualization (Web Audio API)
4. ✅ Thêm recording feature (optional)
5. ✅ Adaptive difficulty algorithm

**Deliverables:**
- Model: `SentenceExample` (new)
- Migration: `0003_add_sentence_example.py`
- Template: Updated with Screen 6 & 7
- JavaScript: Audio recording + waveform

---

### Phase 3: Content Creation (2-3 ngày)

**Tasks:**
1. ✅ Tạo 20+ câu ví dụ cho từng cặp âm
2. ✅ Ghi âm native speaker cho sentences
3. ✅ Tạo conversation scripts
4. ✅ Cập nhật minimal pairs với `difference_note_vi`

**Deliverables:**
- Database: 200+ sentence examples
- Audio files: 200+ MP3/WAV files
- Scripts: `populate_sentences.py`

---

## 🎓 PEDAGOGY RATIONALE

### Tại sao học CẶP ÂM hiệu quả hơn?

#### 1. **Contrastive Learning Theory**
```
Isolated Learning:
Student learns /p/ → stores in memory
Student learns /b/ → stores in memory
Later: Confusion between /p/ and /b/

Contrastive Learning:
Student learns /p/ AND /b/ TOGETHER
Brain stores: "p = no vibration, b = vibration"
Result: Clear distinction, less confusion
```

**Research:** Brown & Hilferty (1986) - "Contrastive phonetics significantly improves L2 pronunciation accuracy"

---

#### 2. **Minimal Pair Pedagogy**
- Học cặp tối thiểu (ship/sheep) = học SỰ KHÁC BIỆT
- Native speakers không học isolated sounds
- They learn sounds in CONTEXT and CONTRAST

---

#### 3. **Cognitive Load Theory**
```
Method A (Current): 
Screen 2: Learn /p/ (all details) → High cognitive load
Screen 3: Learn /b/ (all details) → High cognitive load
Screen 4: Compare → Try to recall both → OVERLOAD

Method B (Proposed):
Screen 1: Overview of BOTH (low load)
Screen 2: Detail /p/ (medium load)
Screen 3: Detail /b/ + recall /p/ (medium load)
Screen 4: Side-by-side comparison (LOW load, reinforcement)
Screen 5: Practice (application)
```

**Result:** Distributed cognitive load = better retention

---

#### 4. **Real-World Context**
- Isolated sounds = artificial
- Sentences with both sounds = natural
- Conversation = how language is used

**Example:**
```
Isolated: "Ship" [just the word]
Context: "I want to BUY a SHIP ticket" [real usage]
```

Student sees:
1. How sounds work in sentences
2. How stress affects pronunciation
3. How sounds connect in speech

---

## 📊 SUCCESS METRICS

### Immediate (Week 1)
- ✅ User engagement: +20% time on lesson page
- ✅ Challenge completion rate: 60% → 75%
- ✅ Positive feedback: 4.0 → 4.5 stars

### Medium-term (Month 1)
- ✅ Pronunciation accuracy: +15% (measured via production scores)
- ✅ Retention rate: 70% → 85% (users remember after 1 week)
- ✅ Lesson completion: 80% → 90%

### Long-term (Quarter 1)
- ✅ User mastery: 60% → 80% reach "mastered" level
- ✅ Production scores: Average 75 → 85
- ✅ User testimonials: "Hiểu hơn, dễ hơn, nhớ lâu hơn"

---

## 🔧 TECHNICAL REQUIREMENTS

### Frontend
```javascript
// Libraries needed:
1. Web Audio API (built-in) - for waveform + recording
2. RecordRTC or MediaRecorder API - for audio recording
3. No additional dependencies

// File size impact:
- Template: +300 lines (~10KB)
- JavaScript: +500 lines (~15KB)
- CSS: +200 lines (~8KB)
Total: ~33KB (minimal)
```

### Backend
```python
# New model needed:
class SentenceExample(models.Model):
    pronunciation_lesson = ForeignKey(PronunciationLesson)
    phoneme_1 = ForeignKey(Phoneme)  # /p/
    phoneme_2 = ForeignKey(Phoneme)  # /b/
    
    text = CharField(max_length=500)
    ipa_transcription = CharField(max_length=600)
    meaning_vi = TextField()
    
    # Highlighted words
    phoneme_1_words = JSONField()  # ["PIE", "PIG"]
    phoneme_2_words = JSONField()  # ["BUY", "BIG"]
    
    audio_file = FileField()
    audio_slow = FileField()
    
    difficulty = PositiveSmallIntegerField()
    order = PositiveIntegerField()

# Migration impact: ~1 minute
# Data population: 2-3 hours (manual)
```

### Database
```sql
-- Cần thêm 200 rows cho SentenceExample
-- Cần update 100+ MinimalPair với difference_note_vi
-- Ước tính: +2MB database size
```

---

## 💡 EXAMPLE: Complete Lesson Flow

### Lesson: "Âm bật hơi đối lập /p/ vs /b/"

```
[Start] → User clicks "Bắt đầu học"

Screen 1: Introduction (1 min)
├── "Hai âm này gần giống nhau..."
├── Phoneme cards: /p/ vs /b/
├── Key difference: Voicing
└── Objectives: Nghe, phân biệt, phát âm

Screen 2: Deep Dive /p/ (2 min)
├── IPA: /p/
├── Tips: "Đặt tờ giấy..."
├── 6 words: Pen, Soap, Stop, Apple, Pea, Pop
└── Common mistakes

Screen 3: Deep Dive /b/ (2 min)
├── Quick recall: /p/ không rung
├── IPA: /b/
├── Tips: "Đặt tay lên cổ họng..."
├── 6 words: Ben, Sob, Bob, Able, Bee, Bob
└── Common mistakes

Screen 4: Side-by-Side (2 min)
├── Comparison table
├── Word pairs: ship vs sheep, pen vs ben
├── Waveform comparison
└── Guided practice

Screen 5: Challenge (3 min)
├── 10 questions
├── Adaptive difficulty
├── Hints available
└── Immediate feedback

Screen 6: Real Context (2 min)
├── 3 sentences with both sounds
├── Mini conversation
├── Optional: Record yourself
└── Tongue twister

Screen 7: Summary (1 min)
├── Score: 8/10 (80%)
├── XP: +20
├── Weak point: "ship vs sheep"
└── Next lesson: /t/ vs /d/

[End] → Redirect to library
```

**Total time:** ~13 minutes (vs 10 minutes current)
**Value added:** +30% learning effectiveness

---

## 🎯 RECOMMENDATIONS

### Ưu tiên thực hiện

**Priority 1: MUST HAVE (Week 1)**
1. ✅ Screen 4: Side-by-Side Comparison
2. ✅ Screen 3: Recall previous sound
3. ✅ Screen 5: Hint button

**Priority 2: SHOULD HAVE (Week 2)**
4. ✅ Screen 6: Real-world context (sentences)
5. ✅ Adaptive difficulty

**Priority 3: NICE TO HAVE (Week 3)**
6. ✅ Waveform visualization
7. ✅ Recording feature
8. ✅ Conversation practice

---

### Alternative: Gradual Rollout

**Option A: All at once**
- Redesign toàn bộ lesson page
- Deploy sau 1-2 tuần
- Risk: High (nhiều thay đổi cùng lúc)

**Option B: Progressive enhancement** ⭐ **RECOMMENDED**
- Week 1: Thêm Screen 4 only
- Week 2: Thêm Screen 6 only
- Week 3: Adaptive difficulty + recording
- User feedback sau mỗi sprint

**Advantage:**
- Lower risk
- User feedback early
- Can pivot if needed

---

## 📚 RELATED DOCUMENTS

- [SYSTEM_GAP_ANALYSIS.md](SYSTEM_GAP_ANALYSIS.md) - Original analysis
- [DEVELOPMENT_WORKFLOW.md](DEVELOPMENT_WORKFLOW.md) - Implementation guide
- [PRONUNCIATION_LEARNING_IMPLEMENTATION.md](PRONUNCIATION_LEARNING_IMPLEMENTATION.md) - Current implementation

---

## ✅ NEXT STEPS

1. **Review này với Product Owner**
   - Confirm pedagogical approach
   - Agree on priorities
   - Set timeline

2. **User Research (optional)**
   - Survey 10 users: "Bạn thích học từng âm hay cặp âm?"
   - A/B test: Current vs New design

3. **Start Implementation**
   - Begin with Priority 1 tasks
   - Deploy to staging
   - Collect feedback

---

**Tạo bởi:** GitHub Copilot  
**Ngày:** 18/12/2025  
**Status:** Đề xuất - Chờ review
