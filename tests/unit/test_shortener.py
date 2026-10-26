import string

import pytest

from snip import shortener
from snip.store import Store


def test_code_collision_does_not_overwrite_existing_link(monkeypatch):
    monkeypatch.setattr(shortener, "store", Store())
    codes = iter(["AAAAAA", "AAAAAA", "BBBBBB"])
    monkeypatch.setattr(shortener, "generate_code", lambda: next(codes))

    first = shortener.create_link("https://first.example/a")
    second = shortener.create_link("https://second.example/b")

    assert shortener.resolve(first.code).url == "https://first.example/a"
    assert shortener.resolve(second.code).url == "https://second.example/b"
    assert first.code == "AAAAAA"
    assert second.code == "BBBBBB"


# --- SLI 2: redirect availability (unit-level contract behind the API 404) ---


def test_resolve_unknown_code_raises_keyerror():
    # main.py maps KeyError to 404; if this contract changes, that mapping breaks.
    with pytest.raises(KeyError):
        shortener.resolve("nope00")


def test_stats_unknown_code_raises_keyerror():
    with pytest.raises(KeyError):
        shortener.stats("nope00")


def test_resolve_unknown_code_creates_no_record_and_leaves_others_untouched():
    known = shortener.create_link("https://known.example")

    with pytest.raises(KeyError):
        shortener.resolve("nope00")

    assert [r.code for r in shortener.list_links()] == [known.code]
    assert shortener.stats(known.code).clicks == 0


# --- SLI 3: resolve correctness ---

EXACT_URLS = [
    "https://example.com",
    "https://example.com/",
    "https://example.com/path?q=a&b=c%20d#frag",
    "https://example.com/?q=",
    "https://example.com/a/b/../c",
    "HTTP://EXAMPLE.COM/CaSe/Path",
    "https://münchen.example/ü?x=ö",
    "https://example.com/?q=" + "x" * 2000,
]


@pytest.mark.parametrize("url", EXACT_URLS)
def test_resolve_returns_the_exact_url_it_was_created_with(url):
    created = shortener.create_link(url)

    assert shortener.resolve(created.code).url == url


def test_each_link_resolves_to_its_own_url():
    urls = [f"https://example.com/{i}" for i in range(50)]
    codes = [shortener.create_link(u).code for u in urls]

    assert [shortener.resolve(c).url for c in codes] == urls


def test_codes_differing_only_in_case_are_different_links(monkeypatch):
    codes = iter(["abcdef", "ABCDEF"])
    monkeypatch.setattr(shortener, "generate_code", lambda: next(codes))
    lower = shortener.create_link("https://lower.example")
    upper = shortener.create_link("https://upper.example")

    assert shortener.resolve("abcdef").url == "https://lower.example"
    assert shortener.resolve("ABCDEF").url == "https://upper.example"
    assert (lower.code, upper.code) == ("abcdef", "ABCDEF")


def test_generate_code_is_six_chars_from_the_documented_alphabet():
    for _ in range(500):
        code = shortener.generate_code()
        assert len(code) == 6
        assert set(code) <= set(string.ascii_letters + string.digits)


# --- SLI 5: stats accuracy ---


def test_new_link_starts_with_zero_clicks():
    assert shortener.create_link("https://example.com").clicks == 0


@pytest.mark.parametrize("n", [1, 2, 7])
def test_n_follows_record_exactly_n_clicks(n):
    code = shortener.create_link("https://example.com").code

    for _ in range(n):
        shortener.resolve(code)

    assert shortener.stats(code).clicks == n


def test_clicks_do_not_leak_between_codes():
    a = shortener.create_link("https://a.example").code
    b = shortener.create_link("https://b.example").code

    for _ in range(3):
        shortener.resolve(a)

    assert shortener.stats(a).clicks == 3
    assert shortener.stats(b).clicks == 0


def test_reading_stats_and_listing_do_not_count_as_clicks():
    code = shortener.create_link("https://example.com").code

    shortener.stats(code)
    shortener.stats(code)
    shortener.list_links()

    assert shortener.stats(code).clicks == 0


def test_list_links_reports_each_links_own_click_count():
    a = shortener.create_link("https://a.example").code
    b = shortener.create_link("https://b.example").code
    shortener.resolve(a)
    shortener.resolve(a)
    shortener.resolve(b)

    assert {r.code: r.clicks for r in shortener.list_links()} == {a: 2, b: 1}
