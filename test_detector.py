from detector import (
    find_links,
    is_ip_link,
    real_domain,
    check_link,
    check_sender,
    check_wording,
    check_attachment,
    risk_level,
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

def test_urgency_is_detected():
    reasons = check_wording("Act now", "Please respond immediately")
    assert any(r.startswith("urgency") for r in reasons)


def test_login_inside_url_is_not_wording():
    assert check_wording("", "http://example.com/login") == []


def test_double_extension_is_detected():
    reasons = check_attachment("invoice.pdf.exe")
    assert any("double extension" in r for r in reasons)


def test_normal_pdf_is_clean():
    assert check_attachment("terms.pdf") == []


def test_risk_levels():
    assert risk_level(0) == "low"
    assert risk_level(29) == "low"
    assert risk_level(30) == "medium"
    assert risk_level(59) == "medium"
    assert risk_level(60) == "high"    