const { createApp } = Vue;

createApp({
    data() {
        return {
            // Features data
            features: [
                {
                    icon: 'fas fa-route',
                    title: 'Lộ trình cá nhân hóa',
                    description: 'AI thông minh xây dựng lộ trình học riêng cho bạn, phù hợp với trình độ và mục tiêu của bạn.'
                },
                {
                    icon: 'fas fa-users',
                    title: 'Giáo viên bản xứ',
                    description: 'Đội ngũ giáo viên giàu kinh nghiệm đến từ Mỹ, Anh, Canada giúp bạn phát âm chuẩn.'
                },
                {
                    icon: 'fas fa-mobile-alt',
                    title: 'Học mọi lúc mọi nơi',
                    description: 'Ứng dụng di động giúp bạn học tập linh hoạt trên mọi thiết bị, kể cả khi offline.'
                },
                {
                    icon: 'fas fa-trophy',
                    title: 'Chứng chỉ quốc tế',
                    description: 'Nhận chứng chỉ được công nhận toàn cầu khi hoàn thành khóa học, nâng cao CV của bạn.'
                }
            ],

            // Teachers data
            teachers: [
                {
                    name: 'John Smith',
                    country: 'United States',
                    flag: 'https://flagcdn.com/32x24/us.png',
                    image: 'assets/images/teachers/teacher-1.jpg',
                    experience: '10+ năm kinh nghiệm giảng dạy'
                },
                {
                    name: 'Emma Wilson',
                    country: 'United Kingdom',
                    flag: 'https://flagcdn.com/32x24/gb.png',
                    image: 'assets/images/teachers/teacher-2.jpg',
                    experience: '8+ năm kinh nghiệm giảng dạy'
                },
                {
                    name: 'Michael Brown',
                    country: 'Canada',
                    flag: 'https://flagcdn.com/32x24/ca.png',
                    image: 'assets/images/teachers/teacher-3.jpg',
                    experience: '12+ năm kinh nghiệm giảng dạy'
                },
                {
                    name: 'Sarah Davis',
                    country: 'Australia',
                    flag: 'https://flagcdn.com/32x24/au.png',
                    image: 'assets/images/teachers/teacher-4.jpg',
                    experience: '7+ năm kinh nghiệm giảng dạy'
                }
            ],

            // Testimonials data
            testimonials: [
                {
                    content: 'Tôi đã thử rất nhiều ứng dụng học tiếng Anh nhưng không có ứng dụng nào hiệu quả bằng EnglishMaster. Chỉ sau 2 tháng, tôi đã có thể giao tiếp tự tin với đồng nghiệp nước ngoài!',
                    name: 'Nguyễn Văn A',
                    position: 'Kỹ sư phần mềm tại FPT',
                    avatar: 'assets/images/testimonials/avatar-1.jpg'
                },
                {
                    content: 'Lộ trình học được cá nhân hóa theo trình độ của tôi, giúp tôi tiến bộ rất nhanh. Giáo viên nhiệt tình, bài giảng sinh động. Tôi đã đạt 7.5 IELTS chỉ sau 3 tháng học!',
                    name: 'Trần Thị B',
                    position: 'Sinh viên ĐH Ngoại Thương',
                    avatar: 'assets/images/testimonials/avatar-2.jpg'
                },
                {
                    content: 'Là một người bận rộn, tôi rất thích tính năng học mọi lúc mọi nơi. Tôi có thể học trên điện thoại mỗi khi rảnh. Sau 4 tháng, tiếng Anh của tôi đã cải thiện đáng kể!',
                    name: 'Lê Văn C',
                    position: 'Giám đốc kinh doanh',
                    avatar: 'assets/images/testimonials/avatar-3.jpg'
                },
                {
                    content: 'EnglishMaster đã thay đổi cuộc đời tôi. Từ người ngại giao tiếp tiếng Anh, giờ tôi tự tin thuyết trình trước đám đông. Cảm ơn đội ngũ giáo viên tuyệt vời!',
                    name: 'Phạm Thị D',
                    position: 'Marketing Manager tại Unilever',
                    avatar: 'assets/images/testimonials/avatar-4.jpg'
                }
            ]
        };
    },

    mounted() {
        // Initialize AOS (Animate On Scroll)
        AOS.init({
            duration: 1000,
            once: true,
            offset: 100
        });

        // Navbar scroll effect
        this.initNavbarScroll();

        // Smooth scroll for anchor links
        this.initSmoothScroll();

        // Add hover effects to buttons
        this.initButtonEffects();

        // Initialize carousel auto-play
        this.initCarousel();
    },

    methods: {
        // Navbar scroll effect
        initNavbarScroll() {
            const navbar = document.querySelector('.navbar');
            
            window.addEventListener('scroll', () => {
                if (window.scrollY > 50) {
                    navbar.classList.add('scrolled');
                } else {
                    navbar.classList.remove('scrolled');
                }
            });
        },

        // Smooth scroll for anchor links
        initSmoothScroll() {
            document.querySelectorAll('a[href^="#"]').forEach(anchor => {
                anchor.addEventListener('click', function (e) {
                    e.preventDefault();
                    const target = document.querySelector(this.getAttribute('href'));
                    if (target) {
                        target.scrollIntoView({
                            behavior: 'smooth',
                            block: 'start'
                        });
                    }
                });
            });
        },

        // Button hover effects
        initButtonEffects() {
            const buttons = document.querySelectorAll('.btn');
            
            buttons.forEach(button => {
                button.addEventListener('mouseenter', function() {
                    this.style.transform = 'translateY(-3px)';
                });
                
                button.addEventListener('mouseleave', function() {
                    this.style.transform = 'translateY(0)';
                });
            });
        },

        // Initialize carousel
        initCarousel() {
            const carousel = document.querySelector('#testimonialCarousel');
            if (carousel) {
                const bsCarousel = new bootstrap.Carousel(carousel, {
                    interval: 5000,
                    wrap: true,
                    pause: 'hover'
                });
            }
        },

        // Handle form submissions (can be customized)
        handleRegistration() {
            alert('Chức năng đăng ký sẽ được triển khai sau!');
        },

        handleTest() {
            alert('Chức năng kiểm tra trình độ sẽ được triển khai sau!');
        }
    }
}).mount('#app');

// Additional utility functions

// Counter animation for statistics
function animateCounter(element, target, duration = 2000) {
    let start = 0;
    const increment = target / (duration / 16);
    
    const timer = setInterval(() => {
        start += increment;
        if (start >= target) {
            element.textContent = target.toLocaleString();
            clearInterval(timer);
        } else {
            element.textContent = Math.floor(start).toLocaleString();
        }
    }, 16);
}

// Intersection Observer for animations
const observerOptions = {
    threshold: 0.1,
    rootMargin: '0px 0px -50px 0px'
};

const observer = new IntersectionObserver((entries) => {
    entries.forEach(entry => {
        if (entry.isIntersecting) {
            entry.target.classList.add('animate-in');
        }
    });
}, observerOptions);

// Observe all animated elements
document.addEventListener('DOMContentLoaded', () => {
    const animatedElements = document.querySelectorAll('[data-animate]');
    animatedElements.forEach(el => observer.observe(el));
});

// Lazy loading images
if ('IntersectionObserver' in window) {
    const imageObserver = new IntersectionObserver((entries, observer) => {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                const img = entry.target;
                if (img.dataset.src) {
                    img.src = img.dataset.src;
                    img.removeAttribute('data-src');
                    observer.unobserve(img);
                }
            }
        });
    });

    document.querySelectorAll('img[data-src]').forEach(img => {
        imageObserver.observe(img);
    });
}

// Handle window resize
let resizeTimer;
window.addEventListener('resize', () => {
    clearTimeout(resizeTimer);
    resizeTimer = setTimeout(() => {
        // Reinitialize AOS on resize
        AOS.refresh();
    }, 250);
});

// Prevent default form submission
document.addEventListener('DOMContentLoaded', () => {
    const forms = document.querySelectorAll('form');
    forms.forEach(form => {
        form.addEventListener('submit', (e) => {
            e.preventDefault();
            // Handle form submission here
            console.log('Form submitted');
        });
    });
});

// Add loading animation
window.addEventListener('load', () => {
    document.body.classList.add('loaded');
});

// Performance optimization: Debounce scroll events
function debounce(func, wait = 10) {
    let timeout;
    return function executedFunction(...args) {
        const later = () => {
            clearTimeout(timeout);
            func(...args);
        };
        clearTimeout(timeout);
        timeout = setTimeout(later, wait);
    };
}

// Track scroll position for animations
let lastScrollTop = 0;
window.addEventListener('scroll', debounce(() => {
    const scrollTop = window.pageYOffset || document.documentElement.scrollTop;
    
    if (scrollTop > lastScrollTop) {
        // Scrolling down
        document.body.classList.add('scrolling-down');
        document.body.classList.remove('scrolling-up');
    } else {
        // Scrolling up
        document.body.classList.add('scrolling-up');
        document.body.classList.remove('scrolling-down');
    }
    
    lastScrollTop = scrollTop <= 0 ? 0 : scrollTop;
}, 10));

// Console greeting message
console.log('%c🚀 EnglishMaster', 'color: #F47C26; font-size: 24px; font-weight: bold;');
console.log('%cChào mừng bạn đến với EnglishMaster!', 'color: #183B56; font-size: 14px;');
console.log('%cPhát triển bởi Vue.js 3 + Bootstrap 5', 'color: #4A4A4A; font-size: 12px;');
