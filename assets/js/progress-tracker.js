/* ====================================
   PROGRESS TRACKER - Learning Analytics
   Phase 2: Core Features
   Version: 1.0.0
   ==================================== */

/**
 * ProgressTracker - Comprehensive learning progress tracking and visualization
 * Features:
 * - Daily/Weekly/Monthly statistics
 * - Streak tracking
 * - Skill progress (LSRW)
 * - Charts and visualizations
 * - Goal setting and achievement
 */
const ProgressTracker = {
    // ====================================
    // CONFIGURATION
    // ====================================
    config: {
        dailyGoal: {
            xp: 50,
            minutes: 15,
            cards: 20,
            lessons: 1
        },
        streakBonus: {
            7: 1.1,   // 10% bonus at 7 days
            30: 1.2,  // 20% bonus at 30 days
            100: 1.5  // 50% bonus at 100 days
        },
        skills: ['listening', 'speaking', 'reading', 'writing'],
        chartColors: {
            primary: '#F47C26',
            secondary: '#183B56',
            success: '#28a745',
            warning: '#ffc107',
            danger: '#dc3545',
            info: '#17a2b8'
        },
        debug: true
    },

    // State
    state: {
        currentUser: null,
        todayProgress: null,
        streak: { current: 0, longest: 0 },
        weeklyData: [],
        monthlyData: [],
        skillLevels: {},
        achievements: [],
        goals: []
    },

    // ====================================
    // INITIALIZATION
    // ====================================
    
    /**
     * Initialize progress tracker
     */
    async init(userId = 'default') {
        this.state.currentUser = userId;
        
        // Load data from IndexedDB
        await this.loadProgress();
        
        // Check and update streak
        await this.updateStreak();
        
        this.log('Progress Tracker initialized');
        return this;
    },

    /**
     * Load progress data from storage
     */
    async loadProgress() {
        if (typeof englishDB === 'undefined') {
            this.log('Database not available, using defaults');
            this.setDefaults();
            return;
        }

        try {
            // Load today's progress
            const today = this.getDateString();
            this.state.todayProgress = await englishDB.get('dailyProgress', today) || this.createDailyProgress(today);

            // Load weekly data
            this.state.weeklyData = await this.getWeeklyData();

            // Load monthly data
            this.state.monthlyData = await this.getMonthlyData();

            // Load skill levels
            const skills = await englishDB.get('userSkills', this.state.currentUser);
            this.state.skillLevels = skills || this.getDefaultSkillLevels();

            // Load achievements
            this.state.achievements = await englishDB.getAll('achievements') || [];

            // Load streak
            const streakData = await englishDB.get('streaks', this.state.currentUser);
            if (streakData) {
                this.state.streak = streakData;
            }

        } catch (error) {
            this.log('Error loading progress:', error);
            this.setDefaults();
        }
    },

    /**
     * Set default values
     */
    setDefaults() {
        const today = this.getDateString();
        this.state.todayProgress = this.createDailyProgress(today);
        this.state.skillLevels = this.getDefaultSkillLevels();
        this.state.weeklyData = [];
        this.state.monthlyData = [];
        this.state.achievements = [];
    },

    /**
     * Create daily progress object
     */
    createDailyProgress(date) {
        return {
            date,
            xp: 0,
            minutes: 0,
            cardsReviewed: 0,
            cardsLearned: 0,
            lessonsCompleted: 0,
            exercisesCompleted: 0,
            listening: { time: 0, exercises: 0, score: 0 },
            speaking: { time: 0, exercises: 0, score: 0 },
            reading: { time: 0, exercises: 0, score: 0 },
            writing: { time: 0, exercises: 0, score: 0 },
            vocabulary: { reviewed: 0, learned: 0, mastered: 0 },
            streak: 0,
            updatedAt: new Date().toISOString()
        };
    },

    /**
     * Get default skill levels
     */
    getDefaultSkillLevels() {
        return {
            listening: { level: 'A1', progress: 0, totalXP: 0 },
            speaking: { level: 'A1', progress: 0, totalXP: 0 },
            reading: { level: 'A1', progress: 0, totalXP: 0 },
            writing: { level: 'A1', progress: 0, totalXP: 0 },
            vocabulary: { words: 0, mastered: 0 },
            grammar: { topics: 0, mastered: 0 },
            overallLevel: 'A1',
            totalXP: 0
        };
    },

    // ====================================
    // PROGRESS LOGGING
    // ====================================
    
    /**
     * Log XP earned
     */
    async addXP(amount, source = 'general') {
        this.state.todayProgress.xp += amount;
        this.state.skillLevels.totalXP += amount;
        
        await this.saveProgress();
        await this.checkLevelUp();
        await this.checkAchievements('xp', this.state.skillLevels.totalXP);

        this.log(`Added ${amount} XP from ${source}. Total today: ${this.state.todayProgress.xp}`);
        
        return {
            added: amount,
            todayTotal: this.state.todayProgress.xp,
            overallTotal: this.state.skillLevels.totalXP
        };
    },

    /**
     * Log study time
     */
    async addStudyTime(minutes, skill = 'general') {
        this.state.todayProgress.minutes += minutes;
        
        if (skill !== 'general' && this.state.todayProgress[skill]) {
            this.state.todayProgress[skill].time += minutes;
        }

        await this.saveProgress();
        await this.checkAchievements('time', this.state.todayProgress.minutes);

        this.log(`Added ${minutes} minutes of ${skill} study`);
    },

    /**
     * Log flashcard review
     */
    async logFlashcardReview(result) {
        this.state.todayProgress.cardsReviewed++;
        this.state.todayProgress.vocabulary.reviewed++;

        if (result.isNew) {
            this.state.todayProgress.cardsLearned++;
            this.state.todayProgress.vocabulary.learned++;
        }

        if (result.mastered) {
            this.state.todayProgress.vocabulary.mastered++;
            this.state.skillLevels.vocabulary.mastered++;
        }

        // Award XP based on quality
        const xpMap = { again: 2, hard: 5, good: 10, easy: 15 };
        const xp = xpMap[result.quality] || 10;
        await this.addXP(xp, 'flashcard');

        await this.saveProgress();
    },

    /**
     * Log lesson completion
     */
    async logLessonComplete(lesson) {
        this.state.todayProgress.lessonsCompleted++;
        
        // Add XP based on lesson
        const xp = lesson.xp || 50;
        await this.addXP(xp, 'lesson');

        // Update skill progress
        if (lesson.skill && this.state.skillLevels[lesson.skill]) {
            this.state.skillLevels[lesson.skill].totalXP += xp;
            this.state.skillLevels[lesson.skill].progress += 5;
        }

        await this.saveProgress();
        await this.checkAchievements('lessons', this.state.todayProgress.lessonsCompleted);

        this.log(`Lesson completed: ${lesson.title}, +${xp} XP`);
    },

    /**
     * Log exercise completion
     */
    async logExercise(skill, score, timeSpent) {
        this.state.todayProgress.exercisesCompleted++;
        
        if (this.state.todayProgress[skill]) {
            this.state.todayProgress[skill].exercises++;
            this.state.todayProgress[skill].score = 
                (this.state.todayProgress[skill].score + score) / 2;
            this.state.todayProgress[skill].time += timeSpent;
        }

        // Award XP based on score
        const xp = Math.round(score / 10) * 5;
        await this.addXP(xp, skill);

        // Update skill level
        if (this.state.skillLevels[skill]) {
            this.state.skillLevels[skill].totalXP += xp;
            this.state.skillLevels[skill].progress += Math.round(score / 20);
        }

        await this.saveProgress();
    },

    // ====================================
    // STREAK MANAGEMENT
    // ====================================
    
    /**
     * Update streak
     */
    async updateStreak() {
        const today = this.getDateString();
        const yesterday = this.getDateString(-1);

        if (typeof englishDB !== 'undefined') {
            const todayProgress = await englishDB.get('dailyProgress', today);
            const yesterdayProgress = await englishDB.get('dailyProgress', yesterday);

            // Check if goal was met yesterday
            if (yesterdayProgress && this.isGoalMet(yesterdayProgress)) {
                // Continue streak
                if (!todayProgress || !todayProgress.streakCounted) {
                    this.state.streak.current++;
                    this.state.streak.longest = Math.max(
                        this.state.streak.longest, 
                        this.state.streak.current
                    );
                }
            } else if (!yesterdayProgress || !this.isGoalMet(yesterdayProgress)) {
                // Reset streak if yesterday's goal wasn't met
                const twoDaysAgo = await englishDB.get('dailyProgress', this.getDateString(-2));
                if (!twoDaysAgo || !this.isGoalMet(twoDaysAgo)) {
                    this.state.streak.current = 0;
                }
            }

            // Save streak
            await englishDB.put('streaks', {
                id: this.state.currentUser,
                ...this.state.streak,
                lastUpdated: new Date().toISOString()
            });
        }

        this.state.todayProgress.streak = this.state.streak.current;
        this.log(`Current streak: ${this.state.streak.current} days`);
    },

    /**
     * Check if daily goal is met
     */
    isGoalMet(progress) {
        const goal = this.config.dailyGoal;
        return (
            progress.xp >= goal.xp ||
            progress.minutes >= goal.minutes ||
            progress.cardsReviewed >= goal.cards ||
            progress.lessonsCompleted >= goal.lessons
        );
    },

    /**
     * Get streak bonus multiplier
     */
    getStreakBonus() {
        const streak = this.state.streak.current;
        let bonus = 1;

        for (const [days, multiplier] of Object.entries(this.config.streakBonus).sort((a, b) => b[0] - a[0])) {
            if (streak >= parseInt(days)) {
                bonus = multiplier;
                break;
            }
        }

        return bonus;
    },

    // ====================================
    // LEVEL SYSTEM
    // ====================================
    
    /**
     * Check for level up
     */
    async checkLevelUp() {
        const levels = ['A1', 'A2', 'B1', 'B2', 'C1', 'C2'];
        const xpThresholds = [0, 500, 2000, 5000, 10000, 20000];

        const totalXP = this.state.skillLevels.totalXP;
        
        let newLevel = 'A1';
        for (let i = xpThresholds.length - 1; i >= 0; i--) {
            if (totalXP >= xpThresholds[i]) {
                newLevel = levels[i];
                break;
            }
        }

        if (newLevel !== this.state.skillLevels.overallLevel) {
            const oldLevel = this.state.skillLevels.overallLevel;
            this.state.skillLevels.overallLevel = newLevel;
            
            // Trigger level up event
            this.onLevelUp(oldLevel, newLevel);
            
            await this.saveProgress();
        }

        // Check individual skills
        for (const skill of this.config.skills) {
            if (this.state.skillLevels[skill]) {
                const skillXP = this.state.skillLevels[skill].totalXP;
                let skillLevel = 'A1';
                
                for (let i = xpThresholds.length - 1; i >= 0; i--) {
                    if (skillXP >= xpThresholds[i] / 2) { // Skills level up faster
                        skillLevel = levels[i];
                        break;
                    }
                }

                if (skillLevel !== this.state.skillLevels[skill].level) {
                    this.state.skillLevels[skill].level = skillLevel;
                    this.onSkillLevelUp(skill, skillLevel);
                }
            }
        }
    },

    /**
     * Handle level up event
     */
    onLevelUp(oldLevel, newLevel) {
        this.log(`Level up! ${oldLevel} -> ${newLevel}`);
        
        // Dispatch custom event
        window.dispatchEvent(new CustomEvent('progressTracker:levelUp', {
            detail: { oldLevel, newLevel }
        }));

        // Show notification if UIComponents available
        if (typeof UIComponents !== 'undefined') {
            UIComponents.toast.success(`🎉 Chúc mừng! Bạn đã lên level ${newLevel}!`);
        }
    },

    /**
     * Handle skill level up
     */
    onSkillLevelUp(skill, level) {
        this.log(`Skill level up! ${skill}: ${level}`);
        
        window.dispatchEvent(new CustomEvent('progressTracker:skillLevelUp', {
            detail: { skill, level }
        }));
    },

    /**
     * Get XP needed for next level
     */
    getXPToNextLevel() {
        const levels = ['A1', 'A2', 'B1', 'B2', 'C1', 'C2'];
        const xpThresholds = [0, 500, 2000, 5000, 10000, 20000];
        
        const currentLevel = this.state.skillLevels.overallLevel;
        const currentIndex = levels.indexOf(currentLevel);
        
        if (currentIndex >= levels.length - 1) {
            return { current: this.state.skillLevels.totalXP, needed: xpThresholds[currentIndex], progress: 100 };
        }

        const currentThreshold = xpThresholds[currentIndex];
        const nextThreshold = xpThresholds[currentIndex + 1];
        const currentXP = this.state.skillLevels.totalXP;
        
        const xpInLevel = currentXP - currentThreshold;
        const xpNeeded = nextThreshold - currentThreshold;
        const progress = Math.round((xpInLevel / xpNeeded) * 100);

        return {
            current: xpInLevel,
            needed: xpNeeded,
            remaining: xpNeeded - xpInLevel,
            progress: Math.min(100, progress),
            nextLevel: levels[currentIndex + 1]
        };
    },

    // ====================================
    // ACHIEVEMENTS
    // ====================================
    
    /**
     * Check and award achievements
     */
    async checkAchievements(type, value) {
        const achievements = this.getAchievementDefinitions();
        
        for (const achievement of achievements) {
            if (achievement.type === type && value >= achievement.threshold) {
                await this.awardAchievement(achievement);
            }
        }
    },

    /**
     * Get achievement definitions
     */
    getAchievementDefinitions() {
        return [
            // XP achievements
            { id: 'xp-100', type: 'xp', threshold: 100, name: 'Người mới bắt đầu', icon: '🌱', xp: 10 },
            { id: 'xp-500', type: 'xp', threshold: 500, name: 'Đang tiến bộ', icon: '📈', xp: 25 },
            { id: 'xp-1000', type: 'xp', threshold: 1000, name: 'Học viên chăm chỉ', icon: '💪', xp: 50 },
            { id: 'xp-5000', type: 'xp', threshold: 5000, name: 'Cao thủ', icon: '🏆', xp: 100 },
            { id: 'xp-10000', type: 'xp', threshold: 10000, name: 'Huyền thoại', icon: '👑', xp: 200 },

            // Streak achievements
            { id: 'streak-7', type: 'streak', threshold: 7, name: 'Một tuần liên tiếp', icon: '🔥', xp: 50 },
            { id: 'streak-30', type: 'streak', threshold: 30, name: 'Một tháng liên tiếp', icon: '⚡', xp: 150 },
            { id: 'streak-100', type: 'streak', threshold: 100, name: '100 ngày bền bỉ', icon: '💎', xp: 500 },

            // Card achievements
            { id: 'cards-100', type: 'cards', threshold: 100, name: 'Nhà sưu tầm từ vựng', icon: '📚', xp: 30 },
            { id: 'cards-500', type: 'cards', threshold: 500, name: 'Bách khoa từ vựng', icon: '🎓', xp: 100 },

            // Time achievements
            { id: 'time-60', type: 'time', threshold: 60, name: 'Học 1 giờ/ngày', icon: '⏰', xp: 20 },
            { id: 'time-300', type: 'time', threshold: 300, name: 'Học 5 giờ/ngày', icon: '🕐', xp: 100 },

            // Lesson achievements
            { id: 'lessons-10', type: 'lessons', threshold: 10, name: 'Hoàn thành 10 bài', icon: '📖', xp: 50 },
            { id: 'lessons-50', type: 'lessons', threshold: 50, name: 'Hoàn thành 50 bài', icon: '📕', xp: 200 }
        ];
    },

    /**
     * Award achievement
     */
    async awardAchievement(achievement) {
        // Check if already earned
        const earned = this.state.achievements.find(a => a.id === achievement.id);
        if (earned) return;

        // Add achievement
        const awarded = {
            ...achievement,
            earnedAt: new Date().toISOString()
        };
        
        this.state.achievements.push(awarded);

        if (typeof englishDB !== 'undefined') {
            await englishDB.add('achievements', awarded);
        }

        // Award bonus XP
        if (achievement.xp) {
            await this.addXP(achievement.xp, 'achievement');
        }

        // Notify
        this.log(`Achievement unlocked: ${achievement.name}`);
        
        window.dispatchEvent(new CustomEvent('progressTracker:achievement', {
            detail: achievement
        }));

        if (typeof UIComponents !== 'undefined') {
            UIComponents.toast.success(`🏅 Achievement: ${achievement.name}!`);
        }
    },

    // ====================================
    // DATA RETRIEVAL
    // ====================================
    
    /**
     * Get today's progress
     */
    getTodayProgress() {
        return {
            ...this.state.todayProgress,
            goalProgress: this.getGoalProgress()
        };
    },

    /**
     * Get goal progress percentage
     */
    getGoalProgress() {
        const progress = this.state.todayProgress;
        const goal = this.config.dailyGoal;

        return {
            xp: Math.min(100, Math.round((progress.xp / goal.xp) * 100)),
            minutes: Math.min(100, Math.round((progress.minutes / goal.minutes) * 100)),
            cards: Math.min(100, Math.round((progress.cardsReviewed / goal.cards) * 100)),
            lessons: Math.min(100, Math.round((progress.lessonsCompleted / goal.lessons) * 100)),
            overall: Math.min(100, Math.round(
                ((progress.xp / goal.xp) * 25 +
                (progress.minutes / goal.minutes) * 25 +
                (progress.cardsReviewed / goal.cards) * 25 +
                (progress.lessonsCompleted / goal.lessons) * 25)
            ))
        };
    },

    /**
     * Get weekly data
     */
    async getWeeklyData() {
        const data = [];
        
        for (let i = 6; i >= 0; i--) {
            const dateStr = this.getDateString(-i);
            let dayData = null;
            
            if (typeof englishDB !== 'undefined') {
                dayData = await englishDB.get('dailyProgress', dateStr);
            }
            
            data.push({
                date: dateStr,
                dayName: this.getDayName(-i),
                ...( dayData || this.createDailyProgress(dateStr))
            });
        }

        return data;
    },

    /**
     * Get monthly data
     */
    async getMonthlyData() {
        const data = [];
        
        for (let i = 29; i >= 0; i--) {
            const dateStr = this.getDateString(-i);
            let dayData = null;
            
            if (typeof englishDB !== 'undefined') {
                dayData = await englishDB.get('dailyProgress', dateStr);
            }
            
            data.push({
                date: dateStr,
                ...(dayData || { xp: 0, minutes: 0, cardsReviewed: 0 })
            });
        }

        return data;
    },

    /**
     * Get skill summary
     */
    getSkillSummary() {
        return Object.entries(this.state.skillLevels)
            .filter(([key]) => this.config.skills.includes(key))
            .map(([skill, data]) => ({
                skill,
                ...data,
                displayName: this.getSkillDisplayName(skill)
            }));
    },

    /**
     * Get skill display name
     */
    getSkillDisplayName(skill) {
        const names = {
            listening: 'Nghe',
            speaking: 'Nói',
            reading: 'Đọc',
            writing: 'Viết'
        };
        return names[skill] || skill;
    },

    // ====================================
    // CHARTS & VISUALIZATION
    // ====================================
    
    /**
     * Generate chart data for XP over time
     */
    getXPChartData(period = 'week') {
        const data = period === 'week' ? this.state.weeklyData : this.state.monthlyData;
        
        return {
            labels: data.map(d => period === 'week' ? d.dayName : d.date.slice(5)),
            datasets: [{
                label: 'XP',
                data: data.map(d => d.xp),
                backgroundColor: this.config.chartColors.primary,
                borderColor: this.config.chartColors.primary,
                borderWidth: 2,
                fill: true,
                tension: 0.4
            }]
        };
    },

    /**
     * Generate chart data for study time
     */
    getTimeChartData(period = 'week') {
        const data = period === 'week' ? this.state.weeklyData : this.state.monthlyData;
        
        return {
            labels: data.map(d => period === 'week' ? d.dayName : d.date.slice(5)),
            datasets: [{
                label: 'Phút học',
                data: data.map(d => d.minutes),
                backgroundColor: this.config.chartColors.info,
                borderColor: this.config.chartColors.info,
                borderWidth: 2
            }]
        };
    },

    /**
     * Generate skill radar chart data
     */
    getSkillRadarData() {
        const skills = this.getSkillSummary();
        
        return {
            labels: skills.map(s => s.displayName),
            datasets: [{
                label: 'Trình độ',
                data: skills.map(s => this.levelToNumber(s.level) * 100 / 6),
                backgroundColor: 'rgba(244, 124, 38, 0.2)',
                borderColor: this.config.chartColors.primary,
                borderWidth: 2,
                pointBackgroundColor: this.config.chartColors.primary
            }]
        };
    },

    /**
     * Convert level to number
     */
    levelToNumber(level) {
        const levels = { 'A1': 1, 'A2': 2, 'B1': 3, 'B2': 4, 'C1': 5, 'C2': 6 };
        return levels[level] || 1;
    },

    /**
     * Render progress card HTML
     */
    renderProgressCard() {
        const progress = this.getTodayProgress();
        const streak = this.state.streak;
        const nextLevel = this.getXPToNextLevel();

        return `
            <div class="progress-card">
                <div class="progress-header">
                    <div class="level-badge">
                        <span class="level">${this.state.skillLevels.overallLevel}</span>
                        <span class="xp">${this.state.skillLevels.totalXP} XP</span>
                    </div>
                    <div class="streak-badge ${streak.current > 0 ? 'active' : ''}">
                        <i class="fas fa-fire"></i>
                        <span>${streak.current} ngày</span>
                    </div>
                </div>
                
                <div class="progress-level">
                    <div class="level-info">
                        <span>Tiến độ đến ${nextLevel.nextLevel || 'MAX'}</span>
                        <span>${nextLevel.current}/${nextLevel.needed} XP</span>
                    </div>
                    <div class="level-bar">
                        <div class="level-fill" style="width: ${nextLevel.progress}%"></div>
                    </div>
                </div>
                
                <div class="daily-goals">
                    <h4>Mục tiêu hôm nay</h4>
                    <div class="goal-items">
                        ${this.renderGoalItem('XP', progress.xp, this.config.dailyGoal.xp, 'fas fa-star')}
                        ${this.renderGoalItem('Phút', progress.minutes, this.config.dailyGoal.minutes, 'fas fa-clock')}
                        ${this.renderGoalItem('Thẻ', progress.cardsReviewed, this.config.dailyGoal.cards, 'fas fa-layer-group')}
                        ${this.renderGoalItem('Bài', progress.lessonsCompleted, this.config.dailyGoal.lessons, 'fas fa-book')}
                    </div>
                </div>
            </div>
        `;
    },

    /**
     * Render goal item HTML
     */
    renderGoalItem(label, current, goal, icon) {
        const percent = Math.min(100, Math.round((current / goal) * 100));
        const completed = percent >= 100;
        
        return `
            <div class="goal-item ${completed ? 'completed' : ''}">
                <div class="goal-icon">
                    <i class="${icon}"></i>
                </div>
                <div class="goal-content">
                    <div class="goal-label">${label}</div>
                    <div class="goal-value">${current}/${goal}</div>
                </div>
                <div class="goal-progress">
                    <svg viewBox="0 0 36 36">
                        <path class="goal-bg" d="M18 2.0845 a 15.9155 15.9155 0 0 1 0 31.831 a 15.9155 15.9155 0 0 1 0 -31.831"/>
                        <path class="goal-fill" stroke-dasharray="${percent}, 100" d="M18 2.0845 a 15.9155 15.9155 0 0 1 0 31.831 a 15.9155 15.9155 0 0 1 0 -31.831"/>
                    </svg>
                    ${completed ? '<i class="fas fa-check"></i>' : ''}
                </div>
            </div>
        `;
    },

    // ====================================
    // SAVE & SYNC
    // ====================================
    
    /**
     * Save progress to storage
     */
    async saveProgress() {
        if (typeof englishDB === 'undefined') return;

        try {
            // Save daily progress
            this.state.todayProgress.updatedAt = new Date().toISOString();
            await englishDB.put('dailyProgress', this.state.todayProgress);

            // Save skill levels
            await englishDB.put('userSkills', {
                id: this.state.currentUser,
                ...this.state.skillLevels
            });

            // Add to sync queue
            await englishDB.addToSyncQueue('progress', {
                date: this.state.todayProgress.date,
                progress: this.state.todayProgress,
                skills: this.state.skillLevels
            });

            this.log('Progress saved');
        } catch (error) {
            this.log('Error saving progress:', error);
        }
    },

    // ====================================
    // UTILITIES
    // ====================================
    
    /**
     * Get date string (YYYY-MM-DD)
     */
    getDateString(daysOffset = 0) {
        const date = new Date();
        date.setDate(date.getDate() + daysOffset);
        return date.toISOString().split('T')[0];
    },

    /**
     * Get day name
     */
    getDayName(daysOffset = 0) {
        const days = ['CN', 'T2', 'T3', 'T4', 'T5', 'T6', 'T7'];
        const date = new Date();
        date.setDate(date.getDate() + daysOffset);
        return days[date.getDay()];
    },

    /**
     * Debug log
     */
    log(...args) {
        if (this.config.debug) {
            console.log('[ProgressTracker]', ...args);
        }
    }
};

// Export
window.ProgressTracker = ProgressTracker;

console.log('[Progress Tracker] Module loaded');
