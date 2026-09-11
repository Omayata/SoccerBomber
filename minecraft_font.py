

import os
import sys
import atexit

FONT_FILENAME = "Minecraft.ttf"

_loaded_font_path = None
_platform = sys.platform

#test น้องนุ 123456

# ================= Windows =================
def _load_windows(font_path):
    import ctypes
    FR_PRIVATE = 0x10
    added = ctypes.windll.gdi32.AddFontResourceExW(font_path, FR_PRIVATE, 0)
    return added != 0


def _unload_windows(font_path):
    import ctypes
    FR_PRIVATE = 0x10
    ctypes.windll.gdi32.RemoveFontResourceExW(font_path, FR_PRIVATE, 0)



def _load_macos(font_path):
    global _mac_url
    import ctypes
    import ctypes.util

    ct_path = ctypes.util.find_library("CoreText")
    cf_path = ctypes.util.find_library("CoreFoundation")
    if not ct_path or not cf_path:
        print("[minecraft_font] ไม่พบ CoreText/CoreFoundation framework")
        return False

    core_text = ctypes.cdll.LoadLibrary(ct_path)
    core_foundation = ctypes.cdll.LoadLibrary(cf_path)

    core_foundation.CFURLCreateFromFileSystemRepresentation.restype = ctypes.c_void_p
    core_foundation.CFURLCreateFromFileSystemRepresentation.argtypes = [
        ctypes.c_void_p, ctypes.c_char_p, ctypes.c_long, ctypes.c_bool
    ]

    path_bytes = font_path.encode("utf-8")
    url = core_foundation.CFURLCreateFromFileSystemRepresentation(
        None, path_bytes, len(path_bytes), False
    )
    if not url:
        print("[minecraft_font] สร้าง CFURL ไม่สำเร็จ")
        return False

    core_text.CTFontManagerRegisterFontsForURL.restype = ctypes.c_bool
    core_text.CTFontManagerRegisterFontsForURL.argtypes = [
        ctypes.c_void_p, ctypes.c_int, ctypes.c_void_p
    ]

    kCTFontManagerScopeProcess = 1  # โหลดแค่ในโปรเซสนี้ ไม่ติดตั้งเครื่อง
    error_ptr = ctypes.c_void_p()
    success = core_text.CTFontManagerRegisterFontsForURL(
        url, kCTFontManagerScopeProcess, ctypes.byref(error_ptr)
    )

    if success:
        _mac_url = url  # เก็บไว้ unregister ตอนปิดโปรแกรม
    return bool(success)


def _unload_macos(font_path):
    import ctypes
    import ctypes.util

    if _mac_url is None:
        return

    ct_path = ctypes.util.find_library("CoreText")
    core_text = ctypes.cdll.LoadLibrary(ct_path)
    core_text.CTFontManagerUnregisterFontsForURL.restype = ctypes.c_bool
    core_text.CTFontManagerUnregisterFontsForURL.argtypes = [
        ctypes.c_void_p, ctypes.c_int, ctypes.c_void_p
    ]
    kCTFontManagerScopeProcess = 1
    error_ptr = ctypes.c_void_p()
    core_text.CTFontManagerUnregisterFontsForURL(
        _mac_url, kCTFontManagerScopeProcess, ctypes.byref(error_ptr)
    )


# ================= Public API =================
def load_private_font(font_path=FONT_FILENAME):
    """โหลดฟอนต์แบบ private ให้ process ปัจจุบันใช้ได้ (ไม่ติดตั้งเครื่อง)"""
    global _loaded_font_path
    font_path = os.path.abspath(font_path)

    if not os.path.exists(font_path):
        print(f"[minecraft_font] ไม่พบไฟล์ฟอนต์: {font_path}")
        return False

    if _platform.startswith("win"):
        ok = _load_windows(font_path)
    elif _platform == "darwin":
        ok = _load_macos(font_path)
    else:
        print(f"[minecraft_font] ยังไม่รองรับแพลตฟอร์ม: {_platform}")
        print("  ทางเลือก: ติดตั้งฟอนต์ลงเครื่องแทน เช่น ~/.fonts (Linux) แล้ว fc-cache -f")
        return False

    if not ok:
        print(f"[minecraft_font] โหลดฟอนต์ไม่สำเร็จ: {font_path}")
        return False

    print(f"[minecraft_font] โหลดฟอนต์สำเร็จ: {font_path}")
    _loaded_font_path = font_path
    return True


def unload_private_font(): 
    """ถอนฟอนต์ออกตอนโปรแกรมปิด (เรียกอัตโนมัติผ่าน atexit)"""
    if not _loaded_font_path:
        return
    if _platform.startswith("win"):
        _unload_windows(_loaded_font_path)
    elif _platform == "darwin":
        _unload_macos(_loaded_font_path)


# โหลดฟอนต์ทันทีที่มีการ import โมดูลนี้
load_private_font()

# ถอนฟอนต์อัตโนมัติตอนโปรแกรมจบการทำงาน (ไม่ต้องเรียกเองในเกม)
atexit.register(unload_private_font)
