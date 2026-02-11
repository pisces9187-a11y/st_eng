/**
 * Layout Components - Navbar & Footer dùng chung
 * Sử dụng: Thêm data-component="navbar" hoặc data-component="footer" vào element
 * 
 * Ví dụ:
 * <div data-component="navbar"></div>
 * <div data-component="footer"></div>
 */

(function() {
    'use strict';

    // Xác định base path dựa trên vị trí trang hiện tại
    function getBasePath() {
        const path = window.location.pathname;
        // Nếu đang ở trong thư mục public/ hoặc admin/
        if (path.includes('/public/') || path.includes('/admin/')) {
            return '..';
        }
        return '.';
    }

    // Kiểm tra trang hiện tại để active menu
    function isActivePage(pageName) {
        const path = window.location.pathname;
        return path.includes(pageName);
    }

    // Navbar HTML template cho trang công khai
    function getPublicNavbarHTML() {
        const basePath = getBasePath();
        
        return `
        <nav class="navbar navbar-expand-lg navbar-light bg-white sticky-top shadow-sm">
            <div class="container">
                <a class="navbar-brand fw-bold" href="${basePath}/public/index.html">
                    <span class="text-primary-dark">English</span><span class="text-energetic-orange">Master</span>
                </a>
                <button class="navbar-toggler border-0" type="button" data-bs-toggle="collapse" data-bs-target="#navbarNav" aria-controls="navbarNav" aria-expanded="false" aria-label="Toggle navigation">
                    <span class="navbar-toggler-icon"></span>
                </button>
                <div class="collapse navbar-collapse" id="navbarNav">
                    <ul class="navbar-nav ms-auto align-items-lg-center">
                        <li class="nav-item">
                            <a class="nav-link ${isActivePage('forum') ? 'active' : ''}" href="${basePath}/public/forum.html">
                                <i class="fas fa-comments me-1"></i>Diễn đàn
                            </a>
                        </li>
                        <li class="nav-item">
                            <a class="nav-link ${isActivePage('leaderboard') ? 'active' : ''}" href="${basePath}/public/leaderboard.html">
                                <i class="fas fa-trophy me-1"></i>Xếp hạng
                            </a>
                        </li>
                        <li class="nav-item">
                            <a class="nav-link ${isActivePage('help-center') ? 'active' : ''}" href="${basePath}/public/help-center.html">
                                <i class="fas fa-question-circle me-1"></i>Hỗ trợ
                            </a>
                        </li>
                    </ul>
                    
                    <!-- Auth Buttons -->
                    <div class="d-flex align-items-center justify-content-center gap-2 ms-lg-3 mt-3 mt-lg-0 navbar-auth">
                        <a href="${basePath}/public/login.html" class="btn btn-outline-primary-dark">
                            Đăng nhập
                        </a>
                        <a href="${basePath}/public/signup.html" class="btn btn-energetic-orange">
                            Đăng ký
                        </a>
                    </div>
                </div>
            </div>
        </nav>`;
    }

    // Navbar HTML template cho trang đã đăng nhập (có sidebar hoặc không)
    function getAuthNavbarHTML(options = {}) {
        const basePath = getBasePath();
        const userName = options.userName || 'User';
        
        return `
        <nav class="navbar navbar-expand-lg navbar-light bg-white sticky-top shadow-sm">
            <div class="container">
                <a class="navbar-brand fw-bold" href="${basePath}/public/dashboard.html">
                    <span class="text-primary-dark">English</span><span class="text-energetic-orange">Master</span>
                </a>
                <button class="navbar-toggler border-0" type="button" data-bs-toggle="collapse" data-bs-target="#navbarNav" aria-controls="navbarNav" aria-expanded="false" aria-label="Toggle navigation">
                    <span class="navbar-toggler-icon"></span>
                </button>
                <div class="collapse navbar-collapse" id="navbarNav">
                    <ul class="navbar-nav ms-auto align-items-lg-center">
                        <li class="nav-item">
                            <a class="nav-link ${isActivePage('forum') ? 'active' : ''}" href="${basePath}/public/forum.html">
                                <i class="fas fa-comments me-1"></i>Diễn đàn
                            </a>
                        </li>
                        <li class="nav-item">
                            <a class="nav-link ${isActivePage('leaderboard') ? 'active' : ''}" href="${basePath}/public/leaderboard.html">
                                <i class="fas fa-trophy me-1"></i>Xếp hạng
                            </a>
                        </li>
                        <li class="nav-item">
                            <a class="nav-link ${isActivePage('help-center') ? 'active' : ''}" href="${basePath}/public/help-center.html">
                                <i class="fas fa-question-circle me-1"></i>Hỗ trợ
                            </a>
                        </li>
                    </ul>
                    
                    <!-- Auth Buttons -->
                    <div class="d-flex align-items-center justify-content-center gap-2 ms-lg-3 mt-3 mt-lg-0 navbar-auth">
                        <a href="${basePath}/public/login.html" class="btn btn-outline-primary-dark">
                            Đăng nhập
                        </a>
                        <a href="${basePath}/public/signup.html" class="btn btn-energetic-orange">
                            Đăng ký
                        </a>
                    </div>
                </div>
            </div>
        </nav>`;
    }

    // Footer HTML template chuẩn
    function getFooterHTML() {
        const basePath = getBasePath();
        
        return `
        <footer class="footer py-5 bg-primary-dark text-light">
            <div class="container">
                <div class="row g-4">
                    <div class="col-lg-4 mb-4 mb-lg-0">
                        <h3 class="h4 fw-bold mb-4">
                            <span class="text-white">English</span><span class="text-energetic-orange">Master</span>
                        </h3>
                        <p class="text-light-gray mb-4">
                            Nền tảng học Tiếng Anh trực tuyến hàng đầu Việt Nam. 
                            Phương pháp học tập hiện đại, hiệu quả vượt trội.
                        </p>
                        <div class="social-links">
                            <a href="#" class="social-link me-3"><i class="fab fa-facebook-f"></i></a>
                            <a href="#" class="social-link me-3"><i class="fab fa-youtube"></i></a>
                            <a href="#" class="social-link me-3"><i class="fab fa-instagram"></i></a>
                            <a href="#" class="social-link"><i class="fab fa-linkedin-in"></i></a>
                        </div>
                    </div>
                    <div class="col-lg-2 col-md-6">
                        <h5 class="fw-bold text-white mb-4">Khóa học</h5>
                        <ul class="list-unstyled">
                            <li class="mb-2"><a href="${basePath}/public/lesson-library.html" class="footer-link">Giao tiếp cơ bản</a></li>
                            <li class="mb-2"><a href="${basePath}/public/lesson-library.html" class="footer-link">Tiếng Anh công sở</a></li>
                            <li class="mb-2"><a href="${basePath}/public/lesson-library.html" class="footer-link">IELTS</a></li>
                            <li class="mb-2"><a href="${basePath}/public/lesson-library.html" class="footer-link">TOEIC</a></li>
                        </ul>
                    </div>
                    <div class="col-lg-2 col-md-6">
                        <h5 class="fw-bold text-white mb-4">Về chúng tôi</h5>
                        <ul class="list-unstyled">
                            <li class="mb-2"><a href="#" class="footer-link">Giới thiệu</a></li>
                            <li class="mb-2"><a href="#" class="footer-link">Giáo viên</a></li>
                            <li class="mb-2"><a href="#" class="footer-link">Blog</a></li>
                            <li class="mb-2"><a href="#" class="footer-link">Tuyển dụng</a></li>
                        </ul>
                    </div>
                    <div class="col-lg-2 col-md-6">
                        <h5 class="fw-bold text-white mb-4">Hỗ trợ</h5>
                        <ul class="list-unstyled">
                            <li class="mb-2"><a href="${basePath}/public/help-center.html" class="footer-link">Trung tâm trợ giúp</a></li>
                            <li class="mb-2"><a href="#" class="footer-link">Liên hệ</a></li>
                            <li class="mb-2"><a href="#" class="footer-link">Chính sách bảo mật</a></li>
                            <li class="mb-2"><a href="#" class="footer-link">Điều khoản dịch vụ</a></li>
                        </ul>
                    </div>
                    <div class="col-lg-2 col-md-6">
                        <h5 class="fw-bold text-white mb-4">Liên hệ</h5>
                        <ul class="list-unstyled">
                            <li class="mb-2 text-light-gray">
                                <i class="fas fa-phone me-2 text-energetic-orange"></i>
                                1900-xxxx
                            </li>
                            <li class="mb-2 text-light-gray">
                                <i class="fas fa-envelope me-2 text-energetic-orange"></i>
                                info@englishmaster.vn
                            </li>
                            <li class="mb-2 text-light-gray">
                                <i class="fas fa-map-marker-alt me-2 text-energetic-orange"></i>
                                Hà Nội, Việt Nam
                            </li>
                        </ul>
                    </div>
                </div>
                <hr class="my-4 bg-light-gray">
                <div class="row">
                    <div class="col-12 text-center">
                        <p class="text-light-gray mb-0">
                            &copy; 2025 EnglishMaster. All rights reserved. Made with 
                            <i class="fas fa-heart text-energetic-orange"></i> in Vietnam
                        </p>
                    </div>
                </div>
            </div>
        </footer>`;
    }

    // Load components khi DOM ready
    function loadComponents() {
        // Load Navbar
        const navbarContainers = document.querySelectorAll('[data-component="navbar"]');
        navbarContainers.forEach(container => {
            const type = container.dataset.type || 'public';
            if (type === 'auth') {
                container.outerHTML = getAuthNavbarHTML();
            } else {
                container.outerHTML = getPublicNavbarHTML();
            }
        });

        // Load Footer
        const footerContainers = document.querySelectorAll('[data-component="footer"]');
        footerContainers.forEach(container => {
            container.outerHTML = getFooterHTML();
        });
    }

    // Auto-load khi DOM ready
    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', loadComponents);
    } else {
        loadComponents();
    }

    // Export để sử dụng thủ công nếu cần
    window.LayoutComponents = {
        loadComponents,
        getPublicNavbarHTML,
        getAuthNavbarHTML,
        getFooterHTML,
        getBasePath
    };
})();
