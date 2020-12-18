import pytest

from crawler.parser import AnchorTagParser
from crawler.parser import get_hrefs_from_html
from crawler.parser import HyperlinkCollection
from crawler.parser import make_hyperlink


def make_html(body: str) -> str:
    """make a html doc by passing data to appear in <body> tag"""
    return f"<html><head></head><body>{body}</body></html>"


def make_a_tag(path: str) -> str:
    """make a <a> tag with path as HREF value"""
    return f'<a href="{path}">another link</a>'


def make_a_tags(paths: list) -> str:
    """make multiple <a> tags (via `make_a_tag`) seperated by <br> tags"""
    return "<br>".join([make_a_tag(path) for path in paths])


@pytest.mark.parametrize(
    "input_link_and_output_result",
    [
        ("/", "/"),
        (".", "/"),
        ("example", "/example"),
        ("/example", "/example"),
        ("www.example.html", "/www.example.html"),
        ("#hello", "/#hello"),
        ("/#hello", "/#hello"),
        ("example#hello", "/example#hello"),
        ("/example#hello", "/example#hello"),
        ("?hello=world", "/?hello=world"),
        ("/?hello=world", "/?hello=world"),
        ("https://www.example.com/", "https://www.example.com/"),
        ("https://www.example.com.", "https://www.example.com/"),
        ("https://www.example.com/example", "https://www.example.com/example"),
        ("https://www.example.com#hello", "https://www.example.com/#hello"),
        ("https://www.example.com/#hello", "https://www.example.com/#hello"),
        (
            "https://www.example.com/example#hello",
            "https://www.example.com/example#hello",
        ),
        ("https://www.example.com?hello=world", "https://www.example.com/?hello=world"),
        (
            "https://www.example.com/?hello=world",
            "https://www.example.com/?hello=world",
        ),
    ],
)
def test_hyperlink(input_link_and_output_result):
    input_link, output_result = input_link_and_output_result
    href = make_hyperlink(input_link)
    assert str(href) == output_result


@pytest.mark.parametrize(
    "input_link_and_output_result",
    [
        ("/", False),
        (".", False),
        ("example", False),
        ("/example", False),
        ("www.example.html", False),
        ("#hello", False),
        ("/#hello", False),
        ("example#hello", False),
        ("/example#hello", False),
        ("?hello=world", False),
        ("/?hello=world", False),
        ("https://www.example.com/", True),
        ("https://www.example.com.", True),
        ("https://www.example.com/example", True),
        ("https://www.example.com#hello", True),
        ("https://www.example.com/#hello", True),
        ("https://www.example.com/example#hello", True),
        ("https://www.example.com?hello=world", True),
        ("https://www.example.com/?hello=world", True),
    ],
)
def test_hyperlink_is_absolute_or_relative(input_link_and_output_result):
    input_link, output_result = input_link_and_output_result
    href = make_hyperlink(input_link)
    assert href.is_absolute is output_result
    assert href.is_relative is not output_result


@pytest.mark.parametrize(
    "input_link_and_output_result",
    [
        ("/", "/"),
        (".", "/"),
        ("example", "/example"),
        ("/example", "/example"),
        ("www.example.html", "/www.example.html"),
        ("#hello", "/#hello"),
        ("/#hello", "/#hello"),
        ("example#hello", "/example#hello"),
        ("/example#hello", "/example#hello"),
        ("?hello=world", "/?hello=world"),
        ("/?hello=world", "/?hello=world"),
    ],
)
def test_hyperlink_join_with_relative_links(input_link_and_output_result):
    input_link, output_result = input_link_and_output_result
    href = make_hyperlink(input_link)
    domain = "https://helloworld.com"
    assert str(href.join(domain)) == domain + output_result


@pytest.mark.parametrize(
    "input_link_and_output_result",
    [
        ("https://www.example.com/", "https://www.example.com/"),
        ("https://www.example.com.", "https://www.example.com/"),
        ("https://www.example.com/example", "https://www.example.com/example"),
        ("https://www.example.com#hello", "https://www.example.com/#hello"),
        ("https://www.example.com/#hello", "https://www.example.com/#hello"),
        (
            "https://www.example.com/example#hello",
            "https://www.example.com/example#hello",
        ),
        ("https://www.example.com?hello=world", "https://www.example.com/?hello=world"),
        (
            "https://www.example.com/?hello=world",
            "https://www.example.com/?hello=world",
        ),
    ],
)
def test_hyperlink_join_with_absolute_links(input_link_and_output_result):
    input_link, output_result = input_link_and_output_result
    href = make_hyperlink(input_link)
    domain = "https://helloworld.com"
    assert str(href.join(domain)) == output_result


@pytest.mark.parametrize(
    "input_link_and_output_result",
    [
        ("/ hello world", "/%20hello%20world"),
        ("/example!@£$%^&*()", "/example%21%40%C2%A3%24%%5E%26%2A%28%29"),
        ("www.EXAMPLE.html", "/www.EXAMPLE.html"),
        ("#hello", "/#hello"),
        ("/#hello", "/#hello"),
        ("HTTPS://WWW.eXaMpLe.cOm/", "https://www.example.com/"),
        ("?hello=world+hello+world", "/?hello=world%2Bhello%2Bworld"),
        (
            "/hello-world?hello=world+hello+world",
            "/hello-world?hello=world%2Bhello%2Bworld",
        ),
        ("/?hello=world&world=hello", "/?hello=world&world=hello"),
    ],
)
def test_hyperlink_normalisation(input_link_and_output_result):
    input_link, output_result = input_link_and_output_result
    assert str(make_hyperlink(input_link)) == output_result


@pytest.mark.parametrize(
    "link",
    [
        "https://example.com",
        "http://example.com",
        "mailto://example.com",
        "//example.com",
        "/",
        ".",
        "example",
        "example.html",
        "www.example.html",
        "../example.html",
        "#hello",
        "?hello=world",
        ".git",
        "/example",
        "/example.html",
        "/example#hello",
        "?hello=world",
        "/example?hello=world&world=hello",
    ],
)
def test_anchor_tag_parser_single_link(link):
    html, href = make_html(make_a_tag(link)), make_hyperlink(link)
    parser = AnchorTagParser()
    parser.feed(html)
    assert parser.found_links.collection == [href]
    assert parser.found_links == HyperlinkCollection([href])


@pytest.mark.parametrize(
    "links",
    [
        ["https://example.com", "http://example.com"],
        ["http://example.com", "mailto://example.com", "//example.com"],
        ["/", ".", "example", "example.html"],
        ["www.example.html", "../example.html", "#hello", "?hello=world", ".git"],
        [
            "https://example.com",
            "/example",
            "/example.html",
            "/example#hello",
            "?hello=world",
            "/example?hello=world&world=hello",
        ],
    ],
)
def test_anchor_tag_parser_multiple_links_no_duplicates(links):
    html, hrefs = (
        make_html(make_a_tags(links)),
        [make_hyperlink(link) for link in links],
    )
    parser = AnchorTagParser()
    parser.feed(html)
    assert parser.found_links.collection == hrefs
    assert parser.found_links == HyperlinkCollection(hrefs)


@pytest.mark.parametrize(
    "links",
    [
        [
            "https://example.com",
            "http://example.com",
            "/example",
            "?hello=world",
            "/example?hello=world&world=hello",
        ],
        [
            "/hello-world",
            "http://example.com",
            "mailto://example.com",
            "//example.com",
            "/hello-world",
        ],
        [
            "https://example.com",
            "https://example.com",
            "#hello",
            "#hello",
            "?hello=world",
        ],
    ],
)
def test_anchor_tag_parser_multiple_links_with_duplicates(links):
    html, hrefs = (
        make_html(make_a_tags(links)),
        [make_hyperlink(link) for link in links],
    )
    parser = AnchorTagParser()
    parser.feed(html)
    assert parser.found_links.collection == hrefs
    assert parser.found_links == HyperlinkCollection(hrefs)


@pytest.mark.parametrize(
    "links",
    [
        [
            "https://example.com",
            "http://example.com",
            "/example",
            "?hello=world",
            "/example?hello=world&world=hello",
        ],
        [
            "/hello-world",
            "http://example.com",
            "mailto://example.com",
            "//example.com",
            "/hello-world",
        ],
        [
            "https://example.com",
            "https://example.com",
            "#hello",
            "#hello",
            "?hello=world",
        ],
    ],
)
def test_get_hrefs_from_html_not_unique(links):
    html, hrefs = (
        make_html(make_a_tags(links)),
        [make_hyperlink(link) for link in links],
    )
    assert get_hrefs_from_html(html).collection == hrefs
    assert get_hrefs_from_html(html, unique=False).collection == hrefs
    assert get_hrefs_from_html(html) == HyperlinkCollection(hrefs)
    assert get_hrefs_from_html(html, unique=False) == HyperlinkCollection(hrefs)


@pytest.mark.parametrize(
    "input_links_output_results",
    [
        (
            [
                "https://example.com",
                "http://example.com",
                "/example",
                "?hello=world",
                "/example?hello=world&world=hello",
            ],
            [
                "https://example.com",
                "http://example.com",
                "/example",
                "?hello=world",
                "/example?hello=world&world=hello",
            ],
        ),
        (
            [
                "/hello-world",
                "http://example.com",
                "mailto://example.com",
                "//example.com",
                "/hello-world",
            ],
            [
                "/hello-world",
                "http://example.com",
                "mailto://example.com",
                "//example.com",
            ],
        ),
        (
            [
                "https://example.com",
                "https://example.com",
                "https://example.com",
                "#hello",
                "?hello=world",
            ],
            ["https://example.com", "#hello", "?hello=world"],
        ),
    ],
)
def test_get_hrefs_from_html_unique(input_links_output_results):
    input_links, output_results = input_links_output_results
    html = make_html(make_a_tags(input_links))
    hrefs = [make_hyperlink(link) for link in output_results]
    assert get_hrefs_from_html(html, unique=True).collection == hrefs
    assert get_hrefs_from_html(html, unique=True) == HyperlinkCollection(hrefs)


def test_hyperlink_collection_behaves_like_list():
    hrefs = [
        make_hyperlink("/hello"),
        make_hyperlink("/world"),
        make_hyperlink("/?hello=world"),
    ]
    # check __init__
    links = HyperlinkCollection(hrefs)
    # check __len__
    assert len(links) == 3
    # check append
    links.append(make_hyperlink("/?hello=world&world=hello"))
    # check __len__ again
    assert len(links) == 4
    # check __getitem__
    assert links[0] == make_hyperlink("/hello")
    assert links[3] == make_hyperlink("/?hello=world&world=hello")
    # check __contains__
    for href in hrefs:
        assert href in links
    # check __iter__
    for index, link in enumerate(links):
        assert hrefs[index] == link


@pytest.mark.parametrize(
    "input_and_output_links",
    [
        (["/"], ["/"]),
        (["/", "/"], ["/"]),
        (["/hello", "/hello", "/hello", "/world"], ["/hello", "/world"]),
    ],
)
def test_hyperlink_collection_dedupe(input_and_output_links):
    input_links, output_links = input_and_output_links
    links = HyperlinkCollection(input_links)
    assert links.dedupe() == HyperlinkCollection(output_links)


@pytest.mark.parametrize(
    "input_and_output",
    [
        (["/", "/"], ["/", "/"]),
        (["hello", "world"], ["/hello", "/world"]),
        (["www.example.com"], ["/www.example.com"]),
    ],
)
def test_hyperlink_collection_relative_links_join_all(input_and_output):
    input_links, output_links = input_and_output
    links = HyperlinkCollection([make_hyperlink(link) for link in input_links])
    domain = "https://www.google.com"
    assert links.join_all(domain).collection == [
        make_hyperlink(domain + link) for link in output_links
    ]


@pytest.mark.parametrize(
    "input_and_output",
    [
        (["https://www.google.com/"], ["https://www.google.com/"]),
        (
            ["https://hello.world", "https://world.hello"],
            ["https://hello.world", "https://world.hello"],
        ),
        (["http://www.example.com"], ["http://www.example.com"]),
    ],
)
def test_hyperlink_collection_absolute_links_join_all(input_and_output):
    input_links, output_links = input_and_output
    links = HyperlinkCollection([make_hyperlink(link) for link in input_links])
    domain = "https://www.google.com"
    assert links.join_all(domain).collection == [make_hyperlink(link) for link in output_links]


@pytest.mark.parametrize(
    "fields_and_input_links_and_output_links",
    [
        (
            ("scheme", "http"),
            [
                "http://www.google.com/",
                "/hello-world?hello=world",
                "#hello",
                "/?hello=world#hello",
                "https://www.example.com",
                "https://example.com/hello-world?world=hello",
            ],
            ["http://www.google.com/"],
        ),
        (
            ("authority", "www.example.com"),
            [
                "/",
                "/hello-world?hello=world",
                "#hello",
                "/?hello=world#hello",
                "https://www.example.com",
                "https://www.example.com/hello-world?world=hello",
            ],
            [
                "https://www.example.com",
                "https://www.example.com/hello-world?world=hello",
            ],
        ),
        (
            ("path", "/hello-world"),
            [
                "/",
                "/hello-world?hello=world",
                "#hello",
                "/?hello=world#hello",
                "https://www.example.com",
                "https://example.com/hello-world?world=hello",
            ],
            [
                "/hello-world?hello=world",
                "https://example.com/hello-world?world=hello",
            ],
        ),
        (
            ("query", "hello=world"),
            [
                "/",
                "/hello-world?hello=world",
                "#hello",
                "/?hello=world#hello",
                "https://www.example.com",
                "https://example.com/?world=hello",
            ],
            [
                "/hello-world?hello=world",
                "/?hello=world#hello",
            ],
        ),
        (
            ("fragment", "hello"),
            [
                "/",
                "/hello-world?hello=world",
                "#goodbye",
                "/?hello=world#hello",
                "https://www.example.com",
                "https://example.com/#hello",
            ],
            ["/?hello=world#hello", "https://example.com/#hello"],
        ),
    ],
)
def test_hyperlink_collection_filter_by(
    fields_and_input_links_and_output_links,
):
    fields, input_links, output_links = fields_and_input_links_and_output_links

    input_hrefs = HyperlinkCollection([make_hyperlink(link) for link in input_links])
    k, v = fields
    filtered_hrefs = input_hrefs.filter_by(**{k: v})

    output_hrefs = HyperlinkCollection([make_hyperlink(link) for link in output_links])

    assert filtered_hrefs == output_hrefs


@pytest.mark.parametrize(
    "fields_and_input_links_and_output_links",
    [
        (
            {"scheme": "http", "authority": "www.example.com"},
            [
                "http://www.google.com/",
                "/hello-world?hello=world",
                "#hello",
                "/?hello=world#hello",
                "http://www.example.com",
                "https://example.com/hello-world?world=hello",
            ],
            ["http://www.example.com"],
        ),
        (
            {
                "authority": "www.example.com",
                "path": "/hello-world",
                "query": "world=hello",
            },
            [
                "/",
                "/hello-world?hello=world",
                "#hello",
                "/?hello=world#hello",
                "https://www.example.com",
                "https://www.example.com/hello-world?world=hello",
            ],
            ["https://www.example.com/hello-world?world=hello"],
        ),
        (
            {"path": "/hello", "query": "hello=world", "fragment": "here"},
            [
                "/hello?hello=world#here",
                "/hello-world?hello=world",
                "#hello",
                "/?hello=world#hello",
                "https://www.example.com",
                "https://yoyoyo.co.uk/hello?hello=world#here",
            ],
            [
                "/hello?hello=world#here",
                "https://yoyoyo.co.uk/hello?hello=world#here",
            ],
        ),
        (
            {
                "scheme": "https",
                "authority": "www.example.com",
                "path": "/",
                "query": "",
                "fragment": "",
            },
            [
                "/",
                "/hello-world?hello=world",
                "#hello",
                "/?hello=world#hello",
                "https://www.example.com",
                "https://example.com/?world=hello",
            ],
            ["https://www.example.com"],
        ),
        (
            {
                "scheme": "https",
                "authority": "www.example.com",
                "path": "/",
                "query": "",
                "fragment": "",
            },
            [
                "/",
                "/hello-world?hello=world",
                "#hello",
                "/?hello=world#hello",
                "https://www.yoyoyo.com",
                "https://example.com/?world=hello",
            ],
            [],
        ),
    ],
)
def test_hyperlink_collection_filter_by_mutli_kwargs(
    fields_and_input_links_and_output_links,
):
    fields, input_links, output_links = fields_and_input_links_and_output_links

    input_hrefs = HyperlinkCollection([make_hyperlink(link) for link in input_links])
    filtered_hrefs = input_hrefs.filter_by(**fields)

    output_hrefs = HyperlinkCollection([make_hyperlink(link) for link in output_links])

    assert filtered_hrefs == output_hrefs
