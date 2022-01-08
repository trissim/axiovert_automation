from mm_api import mm_ctrl

def test_brute_force_af():
    scope = mm_ctrl()
    scope.autofocus_software(2,exposure=250,bin=2,step_size=0.2)

def test_cpbd_af():
    scope = mm_ctrl()
    scope.autofocus_software(8,exposure=250,bin=1,algo='cpdb',error_tol=0.2)

def test_fft_af():
    scope = mm_ctrl()
    #scope.autofocus_software(10,exposure=100,bin=2,algo='fft',error_tol=0.1,crop_ratio=2)
    #scope.autofocus_software(4,exposure=250,bin=1,algo='cpdb',error_tol=0.01,crop_ratio=4)
    scope.autofocus_software(10,exposure=100,bin=2,algo='fine',error_tol=0.25,crop_ratio=2)
   #scope.autofocus_software(4,exposure=250,bin=2,algo='fft',error_tol=0.05,crop_ratio=2)
    scope.autofocus_software(4,exposure=250,bin=1,algo='fine',error_tol=0.05,crop_ratio=1)

def test_calibration():
    scope = mm_ctrl()
    scope.xyz_calibration()
def test_oughta_focus():
    scope = mm_ctrl()
    scope.oughta_focus()
def test_offset():
    scope = mm_ctrl()
    offsets={'TRITC':{'DAPI':0.8},'DAPI':{'TRITC':-0.8}}
   # current_channel='TRITC'
   # last_channel='DAPI'
    current_channel='DAPI'
    last_channel='TRITC'
    if not offsets is None:
        try:
            focus_offset=offsets[last_channel][current_channel]
            scope.set_rel_focus(focus_offset)
        except Exception:
            print("offset dict missing keys")

if __name__ == "__main__":
    #test_fft_af()
    #test_cpbd_af()
    #test_calibration()
    #test_offset()
    test_oughta_focus()