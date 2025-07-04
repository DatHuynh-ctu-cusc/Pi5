DANH_SACH_TAI_KHOAN = {
    "admin": "123",
    "user": "123"
}

def kiem_tra_dang_nhap(ten, mat_khau):
    return DANH_SACH_TAI_KHOAN.get(ten) == mat_khau
