# Content Generation Frontend

## Tổng quan

Giao diện frontend cho tính năng tạo nội dung AI, được tích hợp vào admin dashboard của EasySale.

## Tính năng

### 🤖 Tạo Nội Dung AI
- **Đường dẫn**: `/dashboard/content-generate`
- **Quyền truy cập**: Yêu cầu đăng nhập với role admin/user/manager

### 📝 Form đầu vào
1. **Chủ đề** (*bắt buộc*): Chủ đề cần tạo nội dung
2. **Loại bài viết**: Dropdown với các lựa chọn:
   - Bài viết quảng cáo sản phẩm
   - Bài viết giới thiệu dịch vụ
   - Email marketing khuyến mãi
   - Bài đăng mạng xã hội
   - Bài viết blog chia sẻ kinh nghiệm
   - Bài viết giới thiệu khóa học

3. **Sở thích khách hàng**: Mô tả sở thích của đối tượng khách hàng
4. **Nỗi sợ/Lo lắng**: Những điều khách hàng lo lắng
5. **Điểm đau/Vấn đề**: Vấn đề khách hàng đang gặp phải
6. **Giọng điệu**: Dropdown với các lựa chọn:
   - Thân thiện, tự tin, chuyên nghiệp
   - Động viên, tích cực, dễ hiểu
   - Sang trọng, hấp dẫn, tin cậy
   - Vui vẻ, phấn khích, tin cậy
   - Chuyên nghiệp, trang trọng
   - Thân thiện, gần gũi

7. **Mục tiêu**: Mục tiêu của bài viết

### 🎯 Kết quả
- **Hiển thị nội dung**: Nội dung được tạo hiển thị trong khung văn bản có thể scroll
- **Thông tin metadata**: Hiển thị các tham số đã sử dụng
- **Copy to clipboard**: Nút copy nội dung vào clipboard
- **Xóa kết quả**: Nút xóa kết quả hiện tại

### 🔄 Trạng thái
- **Loading state**: Hiển thị spinner và thông báo "AI đang tạo nội dung..."
- **Error state**: Hiển thị thông báo lỗi với icon cảnh báo
- **Success state**: Hiển thị nội dung và các action buttons
- **Empty state**: Hiển thị placeholder khi chưa có kết quả

## Cấu trúc Component

### ContentGenerateComponent
- **File**: `src/app/pages/content-generate/content-generate.component.ts`
- **Route**: `/dashboard/content-generate`
- **Service**: `DocumentService.generateContent()`

### Interface
```typescript
interface ContentGenerateRequest {
  topic: string;
  loai_bai_viet?: string;
  khach_hang_so_thich?: string;
  khach_hang_noi_so?: string;
  khach_hang_noi_dau?: string;
  giong_dieu?: string;
  muc_tieu?: string;
}

interface ContentGenerateResponse {
  success: boolean;
  content: string;
  topic: string;
  loai_bai_viet: string;
  khach_hang_so_thich: string;
  khach_hang_noi_so: string;
  khach_hang_noi_dau: string;
  giong_dieu: string;
  muc_tieu: string;
}
```

## UI/UX Design

### Layout
- **Grid**: 2 cột trên desktop (form + kết quả), 1 cột trên mobile
- **Responsive**: Tự động điều chỉnh theo kích thước màn hình
- **Colors**: Sử dụng Tailwind CSS với theme blue chính

### Form Design
- **Validation**: Required field validation cho topic
- **Styling**: Clean, modern với focus states
- **Accessibility**: Labels, placeholders, và semantic HTML

### Result Panel
- **Content Display**: Pre-formatted text với custom scrollbar
- **Metadata**: Grid layout hiển thị thông tin tham số
- **Actions**: Buttons với hover effects và loading states

## Tích hợp

### Menu Navigation
- Thêm menu item "🤖 Tạo Nội Dung AI" vào admin sidebar
- Active state highlighting khi ở trang content generation

### Authentication
- Sử dụng JWT token từ AuthService
- Tự động redirect đến login nếu chưa đăng nhập

### API Integration
- Gọi API `/content/generate` qua DocumentService
- Error handling với user-friendly messages
- Loading states với visual feedback

## Styling

### Tailwind Classes
- **Container**: `container mx-auto px-4 py-8`
- **Cards**: `bg-white rounded-lg shadow-md p-6`
- **Form Elements**: Consistent styling với focus rings
- **Buttons**: Color-coded với hover và disabled states

### Custom Styles
- **Scrollbar**: Custom webkit scrollbar cho content area
- **Loading Spinner**: CSS animation với SVG icons
- **Transitions**: Smooth transitions cho interactive elements

## Ví dụ sử dụng

### 1. Tạo bài quảng cáo sản phẩm
```
Chủ đề: "Kem dưỡng da chống lão hóa ABC"
Loại bài viết: "Bài viết quảng cáo sản phẩm"
Sở thích KH: "Làm đẹp tự nhiên, chăm sóc da"
Nỗi sợ KH: "Da bị lão hóa, nếp nhăn"
Điểm đau KH: "Da khô, thiếu độ ẩm"
Giọng điệu: "Thân thiện, tự tin, chuyên nghiệp"
Mục tiêu: "Thuyết phục khách hàng mua sản phẩm"
```

### 2. Tạo email marketing
```
Chủ đề: "Nhà hàng buffet hải sản XYZ"
Loại bài viết: "Email marketing khuyến mãi"
Sở thích KH: "Ẩm thực, hải sản, không gian sang trọng"
Nỗi sợ KH: "Giá cả cao, chất lượng không đảm bảo"
Điểm đau KH: "Khó tìm nhà hàng chất lượng"
Giọng điệu: "Sang trọng, hấp dẫn, tin cậy"
Mục tiêu: "Tạo cảm giác thèm ăn và muốn đặt bàn"
```

## Development

### Chạy development server
```bash
cd frontend
npm start
```

### Build production
```bash
cd frontend
npm run build
```

### Testing
- Unit tests với Jasmine/Karma
- E2E tests với Cypress (nếu có)

## Lưu ý

1. **Performance**: Component sử dụng OnPush change detection strategy
2. **Memory**: Cleanup subscriptions trong ngOnDestroy
3. **Accessibility**: ARIA labels và keyboard navigation
4. **SEO**: Meta tags và structured data (nếu cần)
5. **Analytics**: Track user interactions (nếu có Google Analytics)

## Troubleshooting

### Lỗi thường gặp
1. **401 Unauthorized**: Kiểm tra token hết hạn, đăng nhập lại
2. **500 Server Error**: Kiểm tra backend server và GROQ_API_KEY
3. **Network Error**: Kiểm tra kết nối mạng và CORS settings
4. **Form Validation**: Đảm bảo topic không để trống

### Debug
- Mở Developer Tools → Network tab để xem API calls
- Console logs cho error details
- Check Local Storage cho JWT token 