/* ====================================
   MOCK API SERVER
   English Learning Platform
   Phase 4: Backend Integration
   Created: 08/12/2025
   
   This mock server simulates backend API responses
   for development and testing purposes.
   ==================================== */

/**
 * MockApiServer - Intercepts fetch requests and returns mock data
 */
class MockApiServer {
    constructor(options = {}) {
        // ====================================
        // CONFIGURATION
        // ====================================
        this.config = {
            enabled: options.enabled !== false,
            delay: options.delay || 200, // Simulated network delay
            errorRate: options.errorRate || 0, // 0-1, probability of random errors
            debug: options.debug || true
        };

        // ====================================
        // MOCK DATA STORE
        // ====================================
        this.data = {
            users: this.initUsers(),
            lessons: this.initLessons(),
            flashcards: this.initFlashcards(),
            vocabulary: this.initVocabulary(),
            practiceExercises: this.initPracticeExercises(),
            progress: this.initProgress(),
            achievements: this.initAchievements(),
            notifications: this.initNotifications()
        };

        // Token management
        this.tokens = new Map();
        this.refreshTokens = new Map();

        // Initialize if enabled
        if (this.config.enabled) {
            this.intercept();
        }

        this.log('MockApiServer initialized');
    }

    // ====================================
    // INITIALIZATION DATA
    // ====================================

    initUsers() {
        return [
            {
                id: 1,
                name: 'Nguyễn Văn A',
                email: 'user@example.com',
                password: 'Password123', // Plain text for mock only!
                avatar: null,
                role: 'user',
                level: 'B1',
                xp: 2500,
                streak: 15,
                subscription: { status: 'active', plan: 'premium' },
                email_verified: true,
                created_at: '2024-01-15T10:00:00Z'
            },
            {
                id: 2,
                name: 'Admin User',
                email: 'admin@example.com',
                password: 'Admin123',
                avatar: null,
                role: 'admin',
                level: 'C1',
                xp: 10000,
                streak: 100,
                subscription: { status: 'active', plan: 'enterprise' },
                email_verified: true,
                created_at: '2023-06-01T10:00:00Z'
            }
        ];
    }

    initLessons() {
        return [
            {
                id: 1,
                title: 'Giới thiệu bản thân',
                description: 'Học cách giới thiệu bản thân bằng tiếng Anh',
                level: 'A1',
                topic: 'Giao tiếp cơ bản',
                duration: 15,
                xp_reward: 50,
                thumbnail: 'lesson-intro.jpg',
                content: {
                    sections: [
                        { type: 'video', url: 'intro-video.mp4', duration: 300 },
                        { type: 'vocabulary', words: ['hello', 'name', 'nice', 'meet'] },
                        { type: 'practice', questions: [] }
                    ]
                },
                created_at: '2024-01-01T10:00:00Z'
            },
            {
                id: 2,
                title: 'Thì hiện tại đơn',
                description: 'Nắm vững cách sử dụng thì hiện tại đơn',
                level: 'A1',
                topic: 'Ngữ pháp',
                duration: 20,
                xp_reward: 75,
                thumbnail: 'lesson-present-simple.jpg',
                content: {
                    sections: [
                        { type: 'explanation', html: '<p>Thì hiện tại đơn...</p>' },
                        { type: 'examples', items: [] },
                        { type: 'practice', questions: [] }
                    ]
                },
                created_at: '2024-01-02T10:00:00Z'
            },
            {
                id: 3,
                title: 'Mua sắm & Trả giá',
                description: 'Từ vựng và mẫu câu khi đi mua sắm',
                level: 'A2',
                topic: 'Từ vựng theo chủ đề',
                duration: 25,
                xp_reward: 100,
                thumbnail: 'lesson-shopping.jpg',
                content: {},
                created_at: '2024-01-03T10:00:00Z'
            },
            {
                id: 4,
                title: 'Câu điều kiện loại 1',
                description: 'Học cách sử dụng câu điều kiện loại 1',
                level: 'B1',
                topic: 'Ngữ pháp',
                duration: 30,
                xp_reward: 150,
                thumbnail: 'lesson-conditional.jpg',
                content: {},
                created_at: '2024-01-04T10:00:00Z'
            },
            {
                id: 5,
                title: 'IELTS Speaking Part 1',
                description: 'Chiến lược và mẹo cho IELTS Speaking Part 1',
                level: 'B2',
                topic: 'IELTS',
                duration: 45,
                xp_reward: 200,
                thumbnail: 'lesson-ielts.jpg',
                content: {},
                created_at: '2024-01-05T10:00:00Z'
            }
        ];
    }

    initFlashcards() {
        return [
            // Deck 1: Basic Greetings
            { id: 1, deck_id: 1, front: 'Hello', back: 'Xin chào', level: 'A1', topic: 'Greetings' },
            { id: 2, deck_id: 1, front: 'Good morning', back: 'Chào buổi sáng', level: 'A1', topic: 'Greetings' },
            { id: 3, deck_id: 1, front: 'Good afternoon', back: 'Chào buổi chiều', level: 'A1', topic: 'Greetings' },
            { id: 4, deck_id: 1, front: 'Good evening', back: 'Chào buổi tối', level: 'A1', topic: 'Greetings' },
            { id: 5, deck_id: 1, front: 'Goodbye', back: 'Tạm biệt', level: 'A1', topic: 'Greetings' },
            
            // Deck 2: Numbers
            { id: 6, deck_id: 2, front: 'One', back: 'Một', level: 'A1', topic: 'Numbers' },
            { id: 7, deck_id: 2, front: 'Two', back: 'Hai', level: 'A1', topic: 'Numbers' },
            { id: 8, deck_id: 2, front: 'Three', back: 'Ba', level: 'A1', topic: 'Numbers' },
            { id: 9, deck_id: 2, front: 'Ten', back: 'Mười', level: 'A1', topic: 'Numbers' },
            { id: 10, deck_id: 2, front: 'Hundred', back: 'Trăm', level: 'A1', topic: 'Numbers' },
            
            // Deck 3: Food & Drinks
            { id: 11, deck_id: 3, front: 'Water', back: 'Nước', level: 'A1', topic: 'Food' },
            { id: 12, deck_id: 3, front: 'Coffee', back: 'Cà phê', level: 'A1', topic: 'Food' },
            { id: 13, deck_id: 3, front: 'Rice', back: 'Cơm', level: 'A1', topic: 'Food' },
            { id: 14, deck_id: 3, front: 'Breakfast', back: 'Bữa sáng', level: 'A2', topic: 'Food' },
            { id: 15, deck_id: 3, front: 'Delicious', back: 'Ngon', level: 'A2', topic: 'Food' }
        ];
    }

    initVocabulary() {
        return [
            { id: 1, word: 'accomplish', definition: 'Hoàn thành, đạt được', example: 'She accomplished her goal.', level: 'B2', topic: 'Achievement', learned: true },
            { id: 2, word: 'beneficial', definition: 'Có lợi', example: 'Exercise is beneficial to health.', level: 'B1', topic: 'Health', learned: true },
            { id: 3, word: 'comprehensive', definition: 'Toàn diện', example: 'A comprehensive guide.', level: 'B2', topic: 'Academic', learned: false },
            { id: 4, word: 'determine', definition: 'Xác định', example: 'We need to determine the cause.', level: 'B1', topic: 'Academic', learned: false },
            { id: 5, word: 'enthusiasm', definition: 'Sự nhiệt tình', example: 'He shows great enthusiasm.', level: 'B1', topic: 'Personality', learned: true }
        ];
    }

    initPracticeExercises() {
        return {
            dictation: [
                {
                    id: 1,
                    audio_url: 'dictation-1.mp3',
                    transcript: 'The weather is beautiful today.',
                    level: 'A2',
                    topic: 'Daily Life'
                },
                {
                    id: 2,
                    audio_url: 'dictation-2.mp3',
                    transcript: 'I usually go to work by bus.',
                    level: 'A2',
                    topic: 'Transportation'
                },
                {
                    id: 3,
                    audio_url: 'dictation-3.mp3',
                    transcript: 'Learning a new language requires patience and dedication.',
                    level: 'B1',
                    topic: 'Education'
                }
            ],
            writing: [
                {
                    id: 1,
                    prompt: 'Describe your daily routine.',
                    level: 'A2',
                    min_words: 50,
                    max_words: 150,
                    hints: ['morning activities', 'work/study', 'evening']
                },
                {
                    id: 2,
                    prompt: 'Write about the advantages and disadvantages of social media.',
                    level: 'B1',
                    min_words: 150,
                    max_words: 300,
                    hints: ['communication', 'privacy', 'information']
                },
                {
                    id: 3,
                    prompt: 'Some people believe that technology has made our lives easier. Do you agree or disagree?',
                    level: 'B2',
                    min_words: 250,
                    max_words: 400,
                    hints: ['examples', 'advantages', 'disadvantages', 'conclusion']
                }
            ],
            quiz: [
                {
                    id: 1,
                    title: 'Present Simple Quiz',
                    level: 'A1',
                    questions: [
                        {
                            type: 'multiple-choice',
                            question: 'She ___ to school every day.',
                            options: ['go', 'goes', 'going', 'went'],
                            correct: 1
                        },
                        {
                            type: 'fill-blank',
                            question: 'They ___ (not/like) coffee.',
                            correct: "don't like"
                        },
                        {
                            type: 'true-false',
                            question: '"He don\'t work on Sundays" is grammatically correct.',
                            correct: false
                        }
                    ]
                },
                {
                    id: 2,
                    title: 'Vocabulary - Food',
                    level: 'A2',
                    questions: [
                        {
                            type: 'multiple-choice',
                            question: 'What is "pho" in English?',
                            options: ['Rice', 'Noodle soup', 'Spring roll', 'Fried rice'],
                            correct: 1
                        },
                        {
                            type: 'matching',
                            question: 'Match the words with their meanings',
                            pairs: [
                                { left: 'Delicious', right: 'Ngon' },
                                { left: 'Spicy', right: 'Cay' },
                                { left: 'Sweet', right: 'Ngọt' }
                            ]
                        }
                    ]
                }
            ]
        };
    }

    initProgress() {
        return {
            overall: {
                level: 'B1',
                xp: 2500,
                streak: 15,
                total_lessons: 25,
                completed_lessons: 12,
                total_flashcards_reviewed: 450,
                total_practice_minutes: 1200
            },
            skills: {
                listening: 72,
                speaking: 65,
                reading: 80,
                writing: 68,
                vocabulary: 75,
                grammar: 70
            },
            weekly: [
                { day: 'Mon', minutes: 45, xp: 150 },
                { day: 'Tue', minutes: 30, xp: 100 },
                { day: 'Wed', minutes: 60, xp: 200 },
                { day: 'Thu', minutes: 25, xp: 80 },
                { day: 'Fri', minutes: 50, xp: 175 },
                { day: 'Sat', minutes: 40, xp: 130 },
                { day: 'Sun', minutes: 35, xp: 120 }
            ]
        };
    }

    initAchievements() {
        return [
            { id: 1, name: 'First Steps', description: 'Hoàn thành bài học đầu tiên', icon: 'trophy', unlocked: true, unlocked_at: '2024-01-15' },
            { id: 2, name: 'Week Warrior', description: 'Duy trì streak 7 ngày', icon: 'fire', unlocked: true, unlocked_at: '2024-01-22' },
            { id: 3, name: 'Vocabulary Master', description: 'Học 100 từ vựng', icon: 'book', unlocked: true, unlocked_at: '2024-02-01' },
            { id: 4, name: 'Month Champion', description: 'Duy trì streak 30 ngày', icon: 'crown', unlocked: false, progress: 50 },
            { id: 5, name: 'Perfect Score', description: 'Đạt 100% trong 1 bài quiz', icon: 'star', unlocked: false, progress: 0 },
            { id: 6, name: 'Social Butterfly', description: 'Tham gia 10 live class', icon: 'users', unlocked: false, progress: 30 }
        ];
    }

    initNotifications() {
        return [
            { id: 1, type: 'reminder', title: 'Đến giờ học rồi!', message: 'Đừng quên duy trì streak của bạn hôm nay.', read: false, created_at: new Date().toISOString() },
            { id: 2, type: 'achievement', title: 'Achievement Unlocked!', message: 'Bạn đã đạt được "Week Warrior"', read: false, created_at: new Date(Date.now() - 86400000).toISOString() },
            { id: 3, type: 'system', title: 'Bài học mới', message: 'Bài học "IELTS Writing Task 2" đã được thêm vào.', read: true, created_at: new Date(Date.now() - 172800000).toISOString() }
        ];
    }

    // ====================================
    // FETCH INTERCEPTOR
    // ====================================

    intercept() {
        const originalFetch = window.fetch;
        const self = this;

        window.fetch = async function(url, options = {}) {
            // Only intercept API calls
            if (typeof url === 'string' && url.includes('/api/')) {
                return self.handleRequest(url, options);
            }
            return originalFetch.apply(this, arguments);
        };

        this.log('Fetch interceptor installed');
    }

    async handleRequest(url, options) {
        // Simulate network delay
        await this.delay(this.config.delay);

        // Random errors for testing
        if (Math.random() < this.config.errorRate) {
            return this.errorResponse(500, 'SERVER_ERROR', 'Lỗi máy chủ giả lập');
        }

        const method = (options.method || 'GET').toUpperCase();
        const path = new URL(url, window.location.origin).pathname.replace('/api/v1', '');
        const body = options.body ? JSON.parse(options.body) : null;
        const token = this.extractToken(options.headers);

        this.log(`${method} ${path}`, body);

        // Route handling
        try {
            return await this.route(method, path, body, token);
        } catch (error) {
            this.log('Error handling request:', error);
            return this.errorResponse(500, 'SERVER_ERROR', error.message);
        }
    }

    extractToken(headers) {
        if (!headers) return null;
        const authHeader = headers['Authorization'] || headers['authorization'];
        if (authHeader && authHeader.startsWith('Bearer ')) {
            return authHeader.substring(7);
        }
        return null;
    }

    // ====================================
    // ROUTING
    // ====================================

    async route(method, path, body, token) {
        // Auth routes (no token required)
        if (path.startsWith('/auth/')) {
            return this.handleAuthRoutes(method, path, body);
        }

        // Protected routes - verify token
        if (!this.verifyToken(token)) {
            return this.errorResponse(401, 'UNAUTHORIZED', 'Token không hợp lệ hoặc đã hết hạn');
        }

        const userId = this.getUserIdFromToken(token);

        // User routes
        if (path.startsWith('/user/')) {
            return this.handleUserRoutes(method, path, body, userId);
        }

        // Lessons routes
        if (path.startsWith('/lessons')) {
            return this.handleLessonsRoutes(method, path, body, userId);
        }

        // Flashcards routes
        if (path.startsWith('/flashcards')) {
            return this.handleFlashcardsRoutes(method, path, body, userId);
        }

        // Practice routes
        if (path.startsWith('/practice')) {
            return this.handlePracticeRoutes(method, path, body, userId);
        }

        // Progress routes
        if (path.startsWith('/progress')) {
            return this.handleProgressRoutes(method, path, body, userId);
        }

        // Vocabulary routes
        if (path.startsWith('/vocabulary')) {
            return this.handleVocabularyRoutes(method, path, body, userId);
        }

        // Achievements routes
        if (path === '/achievements') {
            return this.successResponse(this.data.achievements);
        }

        // Notifications routes
        if (path.startsWith('/notifications')) {
            return this.handleNotificationsRoutes(method, path, body, userId);
        }

        // Leaderboard
        if (path === '/leaderboard') {
            return this.successResponse(this.getLeaderboard());
        }

        return this.errorResponse(404, 'NOT_FOUND', 'Endpoint không tồn tại');
    }

    // ====================================
    // AUTH HANDLERS
    // ====================================

    handleAuthRoutes(method, path, body) {
        switch (path) {
            case '/auth/login':
                return this.login(body);
            case '/auth/register':
                return this.register(body);
            case '/auth/logout':
                return this.logout(body);
            case '/auth/refresh':
                return this.refreshToken(body);
            case '/auth/forgot-password':
                return this.forgotPassword(body);
            case '/auth/reset-password':
                return this.resetPassword(body);
            default:
                return this.errorResponse(404, 'NOT_FOUND', 'Không tìm thấy endpoint');
        }
    }

    login(body) {
        const { email, password } = body;
        const user = this.data.users.find(u => u.email === email);

        if (!user || user.password !== password) {
            return this.errorResponse(401, 'INVALID_CREDENTIALS', 'Email hoặc mật khẩu không đúng');
        }

        const tokens = this.generateTokens(user.id);

        return this.successResponse({
            access_token: tokens.accessToken,
            refresh_token: tokens.refreshToken,
            expires_in: 3600,
            user: this.sanitizeUser(user)
        });
    }

    register(body) {
        const { name, email, password } = body;

        // Check if email exists
        if (this.data.users.find(u => u.email === email)) {
            return this.errorResponse(422, 'VALIDATION_ERROR', 'Email đã được sử dụng', {
                errors: { email: ['Email đã được sử dụng'] }
            });
        }

        // Create new user
        const newUser = {
            id: this.data.users.length + 1,
            name,
            email,
            password,
            avatar: null,
            role: 'user',
            level: 'A1',
            xp: 0,
            streak: 0,
            subscription: { status: 'free', plan: null },
            email_verified: false,
            created_at: new Date().toISOString()
        };

        this.data.users.push(newUser);
        const tokens = this.generateTokens(newUser.id);

        return this.successResponse({
            access_token: tokens.accessToken,
            refresh_token: tokens.refreshToken,
            expires_in: 3600,
            user: this.sanitizeUser(newUser)
        });
    }

    logout(body) {
        // Invalidate tokens
        return this.successResponse({ message: 'Đăng xuất thành công' });
    }

    refreshToken(body) {
        const { refresh_token } = body;
        const userId = this.refreshTokens.get(refresh_token);

        if (!userId) {
            return this.errorResponse(401, 'INVALID_TOKEN', 'Refresh token không hợp lệ');
        }

        const user = this.data.users.find(u => u.id === userId);
        if (!user) {
            return this.errorResponse(401, 'USER_NOT_FOUND', 'Người dùng không tồn tại');
        }

        const tokens = this.generateTokens(user.id);

        return this.successResponse({
            access_token: tokens.accessToken,
            refresh_token: tokens.refreshToken,
            expires_in: 3600
        });
    }

    forgotPassword(body) {
        // Always return success to prevent email enumeration
        return this.successResponse({ message: 'Email đặt lại mật khẩu đã được gửi' });
    }

    resetPassword(body) {
        return this.successResponse({ message: 'Mật khẩu đã được đặt lại thành công' });
    }

    // ====================================
    // USER HANDLERS
    // ====================================

    handleUserRoutes(method, path, body, userId) {
        const user = this.data.users.find(u => u.id === userId);

        if (path === '/user/profile') {
            if (method === 'GET') {
                return this.successResponse(this.sanitizeUser(user));
            }
            if (method === 'PUT') {
                Object.assign(user, body);
                return this.successResponse(this.sanitizeUser(user));
            }
        }

        if (path === '/user/settings') {
            if (method === 'GET') {
                return this.successResponse(user.settings || {});
            }
            if (method === 'PUT') {
                user.settings = { ...user.settings, ...body };
                return this.successResponse(user.settings);
            }
        }

        return this.errorResponse(404, 'NOT_FOUND', 'Không tìm thấy endpoint');
    }

    // ====================================
    // LESSONS HANDLERS
    // ====================================

    handleLessonsRoutes(method, path, body, userId) {
        const lessonIdMatch = path.match(/^\/lessons\/(\d+)/);

        if (lessonIdMatch) {
            const lessonId = parseInt(lessonIdMatch[1]);
            const lesson = this.data.lessons.find(l => l.id === lessonId);

            if (!lesson) {
                return this.errorResponse(404, 'NOT_FOUND', 'Bài học không tồn tại');
            }

            if (path.endsWith('/content')) {
                return this.successResponse(lesson.content);
            }

            if (path.endsWith('/progress') && method === 'PUT') {
                // Update progress
                return this.successResponse({ updated: true, ...body });
            }

            if (path.endsWith('/complete') && method === 'POST') {
                // Mark lesson complete
                return this.successResponse({
                    completed: true,
                    xp_earned: lesson.xp_reward,
                    new_xp: this.data.progress.overall.xp + lesson.xp_reward
                });
            }

            return this.successResponse(lesson);
        }

        // Get lessons list
        if (method === 'GET') {
            return this.successResponse(this.data.lessons);
        }

        return this.errorResponse(404, 'NOT_FOUND', 'Không tìm thấy endpoint');
    }

    // ====================================
    // FLASHCARDS HANDLERS
    // ====================================

    handleFlashcardsRoutes(method, path, body, userId) {
        if (path === '/flashcards' || path === '/flashcards/decks') {
            return this.successResponse(this.data.flashcards);
        }

        if (path === '/flashcards/review') {
            // Return cards due for review
            const reviewCards = this.data.flashcards.slice(0, 10);
            return this.successResponse(reviewCards);
        }

        if (path === '/flashcards/sync' && method === 'POST') {
            return this.successResponse({
                synced: true,
                count: body.progress?.length || 0
            });
        }

        const cardIdMatch = path.match(/^\/flashcards\/(\d+)\/review$/);
        if (cardIdMatch && method === 'POST') {
            return this.successResponse({
                updated: true,
                next_review: new Date(Date.now() + 86400000).toISOString()
            });
        }

        return this.errorResponse(404, 'NOT_FOUND', 'Không tìm thấy endpoint');
    }

    // ====================================
    // PRACTICE HANDLERS
    // ====================================

    handlePracticeRoutes(method, path, body, userId) {
        const typeMatch = path.match(/^\/practice\/(\w+)/);
        if (!typeMatch) {
            return this.errorResponse(404, 'NOT_FOUND', 'Không tìm thấy endpoint');
        }

        const type = typeMatch[1];
        const exercises = this.data.practiceExercises[type];

        if (!exercises) {
            return this.errorResponse(404, 'NOT_FOUND', 'Loại bài tập không tồn tại');
        }

        if (path.endsWith('/submit') && method === 'POST') {
            // Handle submission
            return this.successResponse({
                id: Date.now(),
                score: body.score || Math.floor(Math.random() * 30) + 70,
                xp_earned: 50,
                feedback: 'Tốt lắm! Tiếp tục phát huy!'
            });
        }

        return this.successResponse(exercises);
    }

    // ====================================
    // PROGRESS HANDLERS
    // ====================================

    handleProgressRoutes(method, path, body, userId) {
        if (path === '/progress/overview') {
            return this.successResponse(this.data.progress.overall);
        }

        if (path === '/progress/detailed') {
            return this.successResponse(this.data.progress);
        }

        if (path === '/progress/skills') {
            return this.successResponse(this.data.progress.skills);
        }

        if (path === '/progress/streak') {
            return this.successResponse({
                current: this.data.progress.overall.streak,
                longest: 30,
                today_completed: true
            });
        }

        return this.errorResponse(404, 'NOT_FOUND', 'Không tìm thấy endpoint');
    }

    // ====================================
    // VOCABULARY HANDLERS
    // ====================================

    handleVocabularyRoutes(method, path, body, userId) {
        if (method === 'GET' && path === '/vocabulary') {
            return this.successResponse(this.data.vocabulary);
        }

        if (method === 'POST' && path === '/vocabulary') {
            const newWord = {
                id: this.data.vocabulary.length + 1,
                ...body,
                learned: false
            };
            this.data.vocabulary.push(newWord);
            return this.successResponse(newWord);
        }

        if (method === 'POST' && path === '/vocabulary/sync') {
            return this.successResponse({
                synced: true,
                ids: body.vocabulary?.map((_, i) => i + 100)
            });
        }

        const wordIdMatch = path.match(/^\/vocabulary\/(\d+)$/);
        if (wordIdMatch) {
            const wordId = parseInt(wordIdMatch[1]);
            const wordIndex = this.data.vocabulary.findIndex(w => w.id === wordId);

            if (wordIndex === -1) {
                return this.errorResponse(404, 'NOT_FOUND', 'Từ vựng không tồn tại');
            }

            if (method === 'PUT') {
                this.data.vocabulary[wordIndex] = { ...this.data.vocabulary[wordIndex], ...body };
                return this.successResponse(this.data.vocabulary[wordIndex]);
            }

            if (method === 'DELETE') {
                this.data.vocabulary.splice(wordIndex, 1);
                return this.successResponse({ deleted: true });
            }
        }

        return this.errorResponse(404, 'NOT_FOUND', 'Không tìm thấy endpoint');
    }

    // ====================================
    // NOTIFICATIONS HANDLERS
    // ====================================

    handleNotificationsRoutes(method, path, body, userId) {
        if (method === 'GET' && path === '/notifications') {
            return this.successResponse(this.data.notifications);
        }

        if (path === '/notifications/read-all' && method === 'PUT') {
            this.data.notifications.forEach(n => n.read = true);
            return this.successResponse({ updated: true });
        }

        const notifIdMatch = path.match(/^\/notifications\/(\d+)\/read$/);
        if (notifIdMatch && method === 'PUT') {
            const notifId = parseInt(notifIdMatch[1]);
            const notif = this.data.notifications.find(n => n.id === notifId);
            if (notif) {
                notif.read = true;
                return this.successResponse({ updated: true });
            }
        }

        return this.errorResponse(404, 'NOT_FOUND', 'Không tìm thấy endpoint');
    }

    // ====================================
    // HELPER METHODS
    // ====================================

    getLeaderboard() {
        return this.data.users
            .map(u => ({
                id: u.id,
                name: u.name,
                avatar: u.avatar,
                xp: u.xp,
                level: u.level,
                streak: u.streak
            }))
            .sort((a, b) => b.xp - a.xp);
    }

    generateTokens(userId) {
        const accessToken = `mock_token_${userId}_${Date.now()}`;
        const refreshToken = `mock_refresh_${userId}_${Date.now()}`;

        this.tokens.set(accessToken, { userId, expires: Date.now() + 3600000 });
        this.refreshTokens.set(refreshToken, userId);

        return { accessToken, refreshToken };
    }

    verifyToken(token) {
        if (!token) return false;
        const tokenData = this.tokens.get(token);
        return tokenData && tokenData.expires > Date.now();
    }

    getUserIdFromToken(token) {
        const tokenData = this.tokens.get(token);
        return tokenData?.userId;
    }

    sanitizeUser(user) {
        const { password, ...safeUser } = user;
        return safeUser;
    }

    // ====================================
    // RESPONSE HELPERS
    // ====================================

    successResponse(data, meta = {}) {
        return new Response(JSON.stringify({ data, meta }), {
            status: 200,
            headers: { 'Content-Type': 'application/json' }
        });
    }

    errorResponse(status, code, message, extra = {}) {
        return new Response(JSON.stringify({ code, message, ...extra }), {
            status,
            headers: { 'Content-Type': 'application/json' }
        });
    }

    delay(ms) {
        return new Promise(resolve => setTimeout(resolve, ms));
    }

    log(...args) {
        if (this.config.debug) {
            console.log('[MockAPI]', ...args);
        }
    }
}

// ====================================
// GLOBAL INSTANCE
// ====================================

// Auto-initialize mock server only if useMockApi is true
const shouldUseMock = window.AppConfig ? window.AppConfig.api.useMockApi : false;

const mockServer = new MockApiServer({
    enabled: shouldUseMock, // Only enable if AppConfig says so
    delay: 200,
    errorRate: 0,
    debug: true
});

if (shouldUseMock) {
    console.log('[MockAPI] Mock server enabled');
} else {
    console.log('[MockAPI] Mock server disabled - using real backend');
}

window.mockServer = mockServer;

// Export for module use
if (typeof module !== 'undefined' && module.exports) {
    module.exports = { MockApiServer };
}
