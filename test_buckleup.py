import buckleup
import pytest
import openseespy.opensees as ops   # import OpenSeesPy

def test_check_args():
    assert buckleup.check_args(["buckleup","-user"]) == "user"
    assert buckleup.check_args(["buckleup","-default"]) == "default"

def test_get_input():
    with pytest.raises(SystemExit):
        buckleup.get_input("-help")
    with pytest.raises(SystemExit):
        buckleup.get_input("asdf")

def test_buckling():
    #buckling(width, height, thickness, nelem, sigma_x, sigma_y, nmodes, supports, E, v):
    with pytest.raises(SystemExit):
        buckleup.buckling(1, 1, 0.01, 10, -10, -10, 2, 4, 0, 0.3)
    with pytest.raises(ops.OpenSeesError):
        buckleup.buckling(1, 1, 0.01, 10, -10, -10, 10, 4, 210000*10**6, 0)
    with pytest.raises(ops.OpenSeesError):
        buckleup.buckling(1, 1, 0.01, 10, 10, 10, 10, 4, 210000*10**6, 0.3)
    with pytest.raises(SystemExit):
        buckleup.buckling(1, 1, 0, 10, -10, -10, 10, 4, 210000*10**6, 0.3)
    with pytest.raises(ZeroDivisionError):
        buckleup.buckling(1, 0, 0.01, 10, -10, -10, 10, 4, 210000*10**6, 0.3)
    with pytest.raises(ZeroDivisionError):
        buckleup.buckling(0, 1, 0.01, 10, -10, -10, 10, 4, 210000*10**6, 0.3)

def test_get_esize():
    assert buckleup.get_esize(1, 1, 10) == (0.1, 0.1, 0.1)
    assert buckleup.get_esize(1, 2, 10) == (0.1, 0.1, 0.1)
    assert buckleup.get_esize(1, 1.5, 10) == (0.1, 0.1, 1.5/16)
    assert buckleup.get_esize(1, 1.5, 5) == (0.2, 1/4, 1.5/8)
    with pytest.raises(ZeroDivisionError):
        buckleup.get_esize(0, 1.5, 5)
    with pytest.raises(ZeroDivisionError):
        buckleup.get_esize(1, 0, 5)
