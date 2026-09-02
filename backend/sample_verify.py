import importlib
import asyncio
import json
from multiprocessing import Process, Pipe
from instant_100k_generator import PLATFORM_CONFIGS, SEARCH_TERMS_BY_PLATFORM

TIMEOUT = 30  # seconds per scraper


def worker(module_name, func_name, term, max_pages, conn):
    try:
        mod = importlib.import_module(module_name)
        func = getattr(mod, func_name)
        try:
            products = asyncio.run(func(term, max_pages=max_pages))
        except TypeError:
            products = asyncio.run(func(term))
        except Exception:
            # last resort, try without max_pages
            products = asyncio.run(func(term))

        out = []
        for p in products[:5]:
            out.append({
                'product_name': (p.get('product_name') or p.get('title') or '')[:120],
                'product_url': p.get('product_url') or p.get('url') or ''
            })
        conn.send({'ok': True, 'products': out})
    except Exception as e:
        conn.send({'ok': False, 'error': str(e)})
    finally:
        conn.close()


if __name__ == '__main__':
    summary = {}
    for cfg in PLATFORM_CONFIGS:
        name = cfg['name']
        if name == 'Daraz':
            continue
        term_pool = SEARCH_TERMS_BY_PLATFORM.get(name, [])
        term = term_pool[0] if term_pool else 'laptop'
        # determine module and function name from the scraper callable
        scraper = cfg['scraper']
        module_name = getattr(scraper, '__module__', None)
        func_name = getattr(scraper, '__name__', None)
        max_pages = cfg.get('max_pages', 1)
        summary[name] = {'term': term, 'status': 'running', 'products': []}
        if not module_name or not func_name:
            summary[name]['status'] = 'error'
            summary[name]['error'] = 'invalid scraper reference'
            continue

        parent_conn, child_conn = Pipe()
        p = Process(target=worker, args=(module_name, func_name, term, max_pages, child_conn))
        p.start()
        p.join(TIMEOUT)
        if p.is_alive():
            p.terminate()
            summary[name]['status'] = 'timeout'
            continue
        if parent_conn.poll():
            res = parent_conn.recv()
            if res.get('ok'):
                summary[name]['status'] = 'ok'
                summary[name]['products'] = res.get('products', [])
            else:
                summary[name]['status'] = 'error'
                summary[name]['error'] = res.get('error')
        else:
            summary[name]['status'] = 'no-output'

    print(json.dumps(summary, indent=2))
