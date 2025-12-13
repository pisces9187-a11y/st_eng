# 📱 PWA Icons Guide

## Cấu trúc thư mục icons

```
assets/images/icons/
├── icon-72x72.png      (72x72px)
├── icon-96x96.png      (96x96px)
├── icon-128x128.png    (128x128px)
├── icon-144x144.png    (144x144px)
├── icon-152x152.png    (152x152px - iOS)
├── icon-180x180.png    (180x180px - iOS)
├── icon-192x192.png    (192x192px - Android)
├── icon-384x384.png    (384x384px)
├── icon-512x512.png    (512x512px - Splash)
├── maskable-192x192.png (192x192px - Maskable)
└── maskable-512x512.png (512x512px - Maskable)
```

## Yêu cầu thiết kế

### Standard Icons
- **Format**: PNG với nền trong suốt hoặc màu #F47C26
- **Content**: Logo EnglishMaster
- **Safe zone**: Nội dung chính nằm trong 80% diện tích

### Maskable Icons
- **Purpose**: Cho Android Adaptive Icons
- **Safe zone**: Nội dung chính phải nằm trong vùng tròn 80%
- **Background**: Màu #F47C26 (hoặc gradient)
- **Padding**: Thêm 10% padding xung quanh logo

## Công cụ tạo icons

### Online Tools
1. [Maskable.app](https://maskable.app/) - Kiểm tra maskable icons
2. [PWA Asset Generator](https://pwa-asset-generator.nicholashoule.me/) - Tạo tất cả sizes
3. [Favicon.io](https://favicon.io/) - Tạo favicon từ text/image

### Figma/Sketch Export
- Export từ thiết kế với các kích thước yêu cầu
- Sử dụng plugin như "Export for Screens"

## Temporary Placeholder Icons

Trong quá trình phát triển, có thể dùng placeholder icons:

```html
<!-- Temporary: Sử dụng placeholder.com -->
<!-- Thay thế bằng icon thật khi có -->
```

## Checklist

- [ ] Tạo icon gốc (1024x1024px) từ logo
- [ ] Export tất cả kích thước standard
- [ ] Export maskable icons (192, 512)
- [ ] Test với maskable.app
- [ ] Test PWA installation trên Android/iOS
- [ ] Verify icons hiển thị đúng trong manifest

---

*Lưu ý: Placeholder icons sẽ được thay thế sau khi có thiết kế chính thức*
