from detector import (
    find_links,
    is_ip_link,
    real_domain,
    check_link,
    check_sender,
)

def test_ip_link_is_detected():
    assert is_ip_link("http://192.168.4.20/login")

def test_normal_link_is_not_ip():
    assert not is_ip_link("https://www.paypal.com")

def test_find_links_keeps_full_link():
    assert find_links("Go to http://192.168.4.20/login now") == ["http://192.168.4.20/login"]

def test_real_domain_takes_last_two_parts():
    assert real_domain("paypal.com.secure-check.xyz") == "secure-check.xyz"

def test_fake_brand_link_is_suspicious():
    reasons = check_link("https://paypal.com.secure-check.xyz/verify")
    assert any("pretends to be paypal" in r for r in reasons)

def test_official_link_is_clean():
    assert check_link("https://www.paypal.com/activity") == []

def test_lookalike_sender_is_detected():
    reasons = check_sender("PayPal <security@paypa1-support.com>")
    assert any("lookalike" in r for r in reasons)

def test_real_sender_is_clean():
    assert check_sender("PayPal <service@paypal.com>") == []