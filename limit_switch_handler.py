from gpiozero import Button

LIMIT_SWITCHES = {
    'L1': Button(4),
    'L2': Button(17),
    'L3': Button(22),
    'L4': Button(13),
}

def get_limit_states():
    try:
        return {k: '1' if sw.is_pressed else '0' for k, sw in LIMIT_SWITCHES.items()}
    except Exception as e:
        print("[App] ⚠️ Limit switch lỗi:", e)
        return {k: '0' for k in LIMIT_SWITCHES}


def cleanup_switches():
    for sw in LIMIT_SWITCHES.values():
        sw.close()
