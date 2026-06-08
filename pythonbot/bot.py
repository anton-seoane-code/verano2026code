#!/usr/bin/env python3
"""Gibraltar Culture News Bot — fetches RSS feed and generates a tidy HTML page."""

import html
import re
import time
import xml.etree.ElementTree as ET
from urllib.request import urlopen

RSS_URL = "https://www.culture.gi/feed/"
OUTPUT = "news.html"
USER_AGENT = "GibraltarCultureBot/1.0"


def fetch_rss(url):
    req = urlopen(url, timeout=15)
    return req.read()


def parse_rss(xml_data):
    root = ET.fromstring(xml_data)
    items = []
    for item in root.iter("item"):
        title = item.findtext("title", "").strip()
        link = item.findtext("link", "").strip()
        pub_date = item.findtext("pubDate", "").strip()
        description = item.findtext("description", "").strip()
        content = item.findtext("{http://purl.org/rss/1.0/modules/content/}encoded", "")
        creator = item.findtext("{http://purl.org/dc/elements/1.1/}creator", "")

        img_src = ""
        for text in (content, description):
            m = re.search(r'<img[^>]+src="([^"]+)"', text)
            if m:
                img_src = m.group(1)
                break

        excerpt = re.sub(r"<[^>]+>", "", description)
        excerpt = html.unescape(excerpt)
        excerpt = re.sub(r"\s+", " ", excerpt).strip()
        if len(excerpt) > 250:
            excerpt = excerpt[:250].rsplit(" ", 1)[0] + "…"

        try:
            parsed = time.strptime(pub_date, "%a, %d %b %Y %H:%M:%S %z")
            formatted_date = time.strftime("%d %b %Y", parsed)
        except (ValueError, TypeError):
            formatted_date = pub_date

        items.append({
            "title": title,
            "link": link,
            "date": formatted_date,
            "excerpt": excerpt,
            "img": img_src,
            "author": creator,
        })
    return items


def generate_html(items):
    cards = "\n".join(
        _card(i) for i in items
    )

    return f"""<!DOCTYPE html>
<html lang="en-GB">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Gibraltar Culture News</title>
<style>
  *, *::before, *::after {{ box-sizing: border-box; margin: 0; padding: 0; }}
  body {{
    font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif;
    background: #f4f4f4; color: #222; line-height: 1.6; padding: 2rem 1rem;
  }}
  .container {{ max-width: 1200px; margin: 0 auto; }}
  header {{ text-align: center; margin-bottom: 2.5rem; }}
  header h1 {{
    font-size: 2rem; color: #DA0000; letter-spacing: -0.5px;
    display: inline-flex; align-items: center; gap: 0.5rem;
  }}
  header h1::before {{
    content: ""; display: inline-block; width: 32px; height: 32px;
    background: url('data:image/svg+xml,<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 32 32"><rect width="32" height="32" fill="%23DA0000" rx="4"/><text x="16" y="22" text-anchor="middle" fill="%23fff" font-size="14" font-weight="bold">G</text></svg>') no-repeat;
  }}
  header p {{ color: #666; margin-top: 0.25rem; }}
  .grid {{
    display: grid; grid-template-columns: repeat(auto-fill, minmax(320px, 1fr));
    gap: 1.5rem;
  }}
  .card {{
    background: #fff; border-radius: 10px; overflow: hidden;
    box-shadow: 0 2px 8px rgba(0,0,0,.08); transition: transform .15s, box-shadow .15s;
  }}
  .card:hover {{ transform: translateY(-3px); box-shadow: 0 6px 20px rgba(0,0,0,.12); }}
  .card-img {{ width: 100%; height: 200px; object-fit: cover; display: block; background: #eee; }}
  .card-body {{ padding: 1.25rem 1.25rem 1.5rem; }}
  .card-date {{ font-size: .8rem; color: #DA0000; font-weight: 600; text-transform: uppercase; letter-spacing: .5px; margin-bottom: .35rem; }}
  .card-title {{ font-size: 1.1rem; font-weight: 700; margin-bottom: .5rem; line-height: 1.3; }}
  .card-title a {{ color: #222; text-decoration: none; }}
  .card-title a:hover {{ color: #DA0000; }}
  .card-excerpt {{ font-size: .9rem; color: #555; }}
  .card-author {{ font-size: .8rem; color: #999; margin-top: .75rem; }}
  .footer {{ text-align: center; margin-top: 2.5rem; font-size: .85rem; color: #999; }}
  .footer a {{ color: #DA0000; text-decoration: none; }}
</style>
</head>
<body>
<div class="container">
  <header>
    <h1>Gibraltar Culture News</h1>
    <p>Latest from Gibraltar Cultural Services</p>
  </header>
  <div class="grid">
{cards}
  </div>
  <div class="footer">
    <p>Source: <a href="{html.escape(RSS_URL)}">Gibraltar Cultural Services RSS Feed</a></p>
  </div>
</div>
</body>
</html>"""


def _card(item):
    img_html = f'<img class="card-img" src="{html.escape(item["img"])}" alt="" loading="lazy">' if item["img"] else '<div class="card-img"></div>'
    author_html = f'<p class="card-author">{html.escape(item["author"])}</p>' if item["author"] else ""

    return f'''    <article class="card">
      <a href="{html.escape(item["link"])}">{img_html}</a>
      <div class="card-body">
        <p class="card-date">{html.escape(item["date"])}</p>
        <h2 class="card-title"><a href="{html.escape(item["link"])}">{html.escape(item["title"])}</a></h2>
        <p class="card-excerpt">{html.escape(item["excerpt"])}</p>
        {author_html}
      </div>
    </article>'''


def main():
    print(f"Fetching {RSS_URL} …")
    xml_data = fetch_rss(RSS_URL)
    items = parse_rss(xml_data)
    print(f"Found {len(items)} articles")
    html_out = generate_html(items)
    with open(OUTPUT, "w", encoding="utf-8") as f:
        f.write(html_out)
    print(f"Written {OUTPUT} ({len(html_out)} bytes)")


if __name__ == "__main__":
    main()
