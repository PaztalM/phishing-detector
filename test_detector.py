from detector import is_ip_link


def test_ip_link_is_detected():
    assert is_ip_link("http://192.168.4.20/login")


def test_normal_link_is_not_ip():
    assert not is_ip_link("https://www.paypal.com")