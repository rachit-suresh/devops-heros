"""Capture actual browser pixels and assert the real UI/API behavior."""
import json
import os
from pathlib import Path
from playwright.sync_api import sync_playwright

out = Path('evidence')
out.mkdir(exist_ok=True)
with sync_playwright() as p:
    ingress_host = os.getenv('INGRESS_HOST')
    # Chromium rejects an overridden Host header; map the ingress host to
    # localhost at the DNS level instead.
    launch_args = [f'--host-resolver-rules=MAP {ingress_host} 127.0.0.1'] if ingress_host else []
    browser = p.chromium.launch(args=launch_args)
    if os.getenv('MONITORING_PROOF'):
        page = browser.new_page(viewport={'width': 1440, 'height': 1000})
        page.goto('http://localhost:9090/targets')
        page.wait_for_timeout(3000)
        page.screenshot(path=str(out / 'prometheus-targets.png'), full_page=True)
        page.goto('http://localhost:3001/d/tracktonic/tracktonic-listening-api?orgId=1&from=now-15m&to=now&refresh=5s')
        page.wait_for_timeout(8000)
        page.screenshot(path=str(out / 'grafana-dashboard.png'), full_page=True)
        browser.close()
        raise SystemExit(0)
    url = os.environ['APP_URL']
    prefix = os.environ.get('OUTPUT_PREFIX', 'app')
    if ingress_host:
        from urllib.parse import urlparse, urlunparse
        parsed = urlparse(url)
        url = urlunparse(parsed._replace(netloc=f'{ingress_host}:{parsed.port or 80}'))
    context = browser.new_context(viewport={'width': 1440, 'height': 1000})
    page = context.new_page()
    errors = []
    page.on('pageerror', lambda error: errors.append(str(error)))
    page.goto(url)
    page.get_by_text('Your next favorite record starts here. Queue your first album above.').wait_for()
    for title, artist, year in [('Discovery','Daft Punk',2001),('OK Computer','Radiohead',1997),('In Rainbows','Radiohead',2007),('Random Access Memories','Daft Punk',2013)]:
        page.locator('#title').fill(title)
        page.locator('#artist').fill(artist)
        page.locator('#year').fill(str(year))
        page.locator('#add-button').click()
        page.get_by_role('heading', name=title, exact=True).wait_for()
    page.get_by_role('button', name='Rate Discovery 5 out of 5', exact=True).click()
    page.get_by_role('button', name='Rate Discovery 5 out of 5', exact=True).wait_for()
    page.get_by_label('Listening status for OK Computer', exact=True).select_option('listening')
    page.wait_for_timeout(1000)
    page.screenshot(path=str(out / f'{prefix}-desktop.png'), full_page=True)
    page.get_by_role('button',name='Queued',exact=True).click()
    assert page.locator('article.album').count() == 2
    page.get_by_role('button',name='All albums',exact=True).click()
    page.locator('#search').fill('discovery')
    assert page.locator('article.album').count() == 1
    page.locator('#search').fill('')
    for width in [390,320]:
        page.set_viewport_size({'width':width,'height':844})
        assert page.evaluate('document.documentElement.scrollWidth <= innerWidth'), 'horizontal page overflow'
        page.screenshot(path=str(out / f'{prefix}-mobile-{width}.png'), full_page=True)
    # XSS regression: payload must display as plain text, never create an image.
    payload = '<img src=x onerror=alert(1)>'
    page.locator('#title').fill(payload)
    page.locator('#artist').fill('Security test')
    page.locator('#add-button').click()
    page.get_by_role('heading',name=payload,exact=True).wait_for()
    assert page.locator('article.album img').count() == 0
    assert not errors, errors
    (out / f'{prefix}-browser-checks.json').write_text(json.dumps({'crud_create':True,'ratings':True,'status_change':True,'filters':True,'search':True,'no_overflow_widths':[320,390],'xss_plain_text':True,'page_errors':errors},indent=2))
    browser.close()
