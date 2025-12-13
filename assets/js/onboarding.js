const { createApp } = Vue;

createApp({
    data() {
        return {
            currentScreen: 0,
            selectedGoal: null,
            selectedLevel: null,
            selectedVocab: null,
            selectedGrammar: null,
            selectedListening: null,
            vocabularyChecked: false,
            vocabularyCorrect: false,
            grammarChecked: false,
            grammarCorrect: false,
            listeningChecked: false,
            listeningCorrect: false,
            audioPlayed: false,
            userEmail: '',
            loaderText: '... Đang phân tích kết quả ...',
            
            // Question data
            goals: [
                {
                    id: 1,
                    icon: 'fas fa-briefcase',
                    text: 'Thăng tiến công việc / Lương cao hơn'
                },
                {
                    id: 2,
                    icon: 'fas fa-plane',
                    text: 'Đi du lịch / Định cư'
                },
                {
                    id: 3,
                    icon: 'fas fa-book',
                    text: 'Thi chứng chỉ (IELTS, TOEIC)'
                },
                {
                    id: 4,
                    icon: 'fas fa-microphone',
                    text: 'Giao tiếp tự tin, không sợ Tây'
                }
            ],
            
            levels: [
                {
                    id: 1,
                    title: 'Mới tinh (Zero)',
                    description: '"Hello" cũng chưa biết viết'
                },
                {
                    id: 2,
                    title: 'Sơ cấp (Beginner)',
                    description: 'Biết vài từ nhưng không ghép được câu'
                },
                {
                    id: 3,
                    title: 'Tạm ổn (Intermediate)',
                    description: 'Đọc hiểu nhưng không nói được (Mất gốc)'
                },
                {
                    id: 4,
                    title: 'Khá (Advanced)',
                    description: 'Muốn nói trôi chảy như người bản xứ'
                }
            ],
            
            vocabularyAnswers: [
                { id: 1, text: 'Orange', correct: false },
                { id: 2, text: 'Apple', correct: true },
                { id: 3, text: 'Banana', correct: false }
            ],
            
            grammarAnswers: [
                { id: 1, text: 'A. go', correct: false },
                { id: 2, text: 'B. goes', correct: true },
                { id: 3, text: 'C. going', correct: false }
            ],
            
            listeningAnswers: [
                { id: 1, text: 'Can you help me?', correct: true },
                { id: 2, text: 'How are you today?', correct: false },
                { id: 3, text: 'What is your name?', correct: false }
            ]
        };
    },
    
    computed: {
        progressPercentage() {
            const progressMap = {
                1: 20,
                2: 40,
                3: 60,
                4: 80,
                5: 90,
                6: 100
            };
            return progressMap[this.currentScreen] || 0;
        }
    },
    
    methods: {
        nextScreen() {
            this.currentScreen++;
            window.scrollTo(0, 0);
        },
        
        selectGoal(goalId) {
            this.selectedGoal = goalId;
            setTimeout(() => {
                this.nextScreen();
            }, 500);
        },
        
        selectLevel(levelId) {
            this.selectedLevel = levelId;
            setTimeout(() => {
                this.nextScreen();
            }, 500);
        },
        
        selectVocabulary(answerId, isCorrect) {
            this.selectedVocab = answerId;
            this.vocabularyChecked = true;
            this.vocabularyCorrect = isCorrect;
            
            setTimeout(() => {
                this.nextScreen();
            }, isCorrect ? 800 : 2000);
        },
        
        selectGrammar(answerId, isCorrect) {
            this.selectedGrammar = answerId;
            this.grammarChecked = true;
            this.grammarCorrect = isCorrect;
            
            setTimeout(() => {
                this.nextScreen();
            }, isCorrect ? 800 : 2000);
        },
        
        playAudio() {
            this.audioPlayed = true;
            // Simulate audio playback
            const utterance = new SpeechSynthesisUtterance('Can you help me?');
            utterance.lang = 'en-US';
            utterance.rate = 0.9;
            window.speechSynthesis.speak(utterance);
        },
        
        selectListening(answerId, isCorrect) {
            this.selectedListening = answerId;
            this.listeningChecked = true;
            this.listeningCorrect = isCorrect;
            
            setTimeout(() => {
                this.startLoading();
            }, isCorrect ? 800 : 2000);
        },
        
        startLoading() {
            this.nextScreen(); // Go to loader screen
            
            const loaderMessages = [
                '... Đang phân tích kết quả ...',
                '... Đang tìm giáo viên phù hợp ...',
                `... Đang xây dựng lộ trình cho mục tiêu "${this.getGoalText()}" ...`
            ];
            
            let messageIndex = 0;
            const messageInterval = setInterval(() => {
                messageIndex++;
                if (messageIndex < loaderMessages.length) {
                    this.loaderText = loaderMessages[messageIndex];
                }
            }, 1500);
            
            // After 4.5 seconds, show results
            setTimeout(() => {
                clearInterval(messageInterval);
                this.nextScreen();
                this.triggerConfetti();
            }, 4500);
        },
        
        triggerConfetti() {
            setTimeout(() => {
                confetti({
                    particleCount: 100,
                    spread: 70,
                    origin: { y: 0.6 },
                    colors: ['#F47C26', '#183B56', '#FFA500']
                });
            }, 300);
        },
        
        getGoalText() {
            const goal = this.goals.find(g => g.id === this.selectedGoal);
            return goal ? goal.text : 'mục tiêu của bạn';
        },
        
        getUserLevel() {
            const levelMap = {
                1: 'Sơ cấp (A1)',
                2: 'Sơ cấp (A2)',
                3: 'Trung cấp (B1)',
                4: 'Trung cấp (B2)'
            };
            return levelMap[this.selectedLevel] || 'Sơ cấp (A2)';
        },
        
        getStrength() {
            const strengths = ['Từ vựng', 'Ngữ pháp', 'Nghe hiểu', 'Phát âm'];
            let strongSkills = [];
            
            if (this.vocabularyCorrect) strongSkills.push('Từ vựng');
            if (this.grammarCorrect) strongSkills.push('Ngữ pháp');
            if (this.listeningCorrect) strongSkills.push('Nghe hiểu');
            
            if (strongSkills.length === 0) {
                return 'Nhiệt huyết học tập';
            }
            
            return strongSkills.join(', ');
        },
        
        getWeakness() {
            let weakSkills = [];
            
            if (!this.vocabularyCorrect) weakSkills.push('Từ vựng');
            if (!this.grammarCorrect) weakSkills.push('Ngữ pháp');
            if (!this.listeningCorrect) weakSkills.push('Nghe hiểu');
            
            if (weakSkills.length === 0) {
                return 'Phản xạ giao tiếp';
            }
            
            return weakSkills[0];
        },
        
        submitEmail() {
            if (!this.userEmail) {
                alert('Vui lòng nhập email của bạn!');
                return;
            }
            
            // Store user data
            const userData = {
                email: this.userEmail,
                goal: this.getGoalText(),
                level: this.getUserLevel(),
                strength: this.getStrength(),
                weakness: this.getWeakness(),
                timestamp: new Date().toISOString()
            };
            
            console.log('User data:', userData);
            
            // Save to localStorage
            localStorage.setItem('englishmaster_user', JSON.stringify(userData));
            
            // Show success message
            alert('🎉 Tuyệt vời! Lộ trình học của bạn đã được gửi đến email.\n\nVui lòng kiểm tra hộp thư (và cả spam nếu cần).');
            
            // Redirect to main page
            setTimeout(() => {
                window.location.href = 'index.html';
            }, 1500);
        }
    },
    
    mounted() {
        console.log('%c🚀 EnglishMaster Onboarding', 'color: #F47C26; font-size: 20px; font-weight: bold;');
        console.log('%cPersonalization Quiz System', 'color: #183B56; font-size: 14px;');
        
        // Prevent back button during quiz
        history.pushState(null, null, location.href);
        window.onpopstate = function () {
            history.go(1);
        };
    }
}).mount('#onboarding-app');

// Additional utility functions

// Keyboard navigation
document.addEventListener('keydown', (e) => {
    // Press Enter to continue on certain screens
    if (e.key === 'Enter') {
        const currentApp = document.querySelector('#onboarding-app').__vue_app__;
        if (currentApp && currentApp._instance) {
            const screen = currentApp._instance.ctx.currentScreen;
            // Auto-continue on welcome screen
            if (screen === 0) {
                currentApp._instance.ctx.nextScreen();
            }
        }
    }
});

// Prevent page refresh during quiz
window.addEventListener('beforeunload', (e) => {
    const currentScreen = document.querySelector('#onboarding-app').__vue_app__?._instance?.ctx?.currentScreen;
    if (currentScreen > 0 && currentScreen < 7) {
        e.preventDefault();
        e.returnValue = 'Bạn có chắc muốn thoát? Tiến trình của bạn sẽ không được lưu.';
    }
});

// Analytics tracking (mock)
function trackEvent(eventName, data) {
    console.log(`📊 Event: ${eventName}`, data);
    // Here you can integrate with Google Analytics, Mixpanel, etc.
    // Example: gtag('event', eventName, data);
}

// Track screen views
const observer = new MutationObserver(() => {
    const app = document.querySelector('#onboarding-app').__vue_app__?._instance?.ctx;
    if (app) {
        trackEvent('screen_view', {
            screen: app.currentScreen,
            timestamp: Date.now()
        });
    }
});

// Start observing
setTimeout(() => {
    const appElement = document.querySelector('#onboarding-app');
    if (appElement) {
        observer.observe(appElement, {
            childList: true,
            subtree: true
        });
    }
}, 1000);
