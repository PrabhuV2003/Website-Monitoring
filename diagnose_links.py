"""
Link Diagnostic Tool - Shows exactly what links are on each page.
Run: python diagnose_links.py https://yoursite.com /page1 /page2
"""
import sys
import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse
from collections import Counter

def count_links_on_page(base_url, page='/'):
    """Count and categorize all links on a page."""
    url = urljoin(base_url, page)
    
    print(f"\n{'='*70}")
    print(f"📄 PAGE: {url}")
    print('='*70)
    
    try:
        response = requests.get(url, timeout=15, headers={'User-Agent': 'WordPress-Monitor/1.0'})
        if response.status_code != 200:
            print(f"❌ Failed to fetch page: Status {response.status_code}")
            return
        
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # Find all anchor tags
        all_anchors = soup.find_all('a')
        
        # Categorize links
        internal_links = []
        external_links = []
        hash_links = []
        javascript_links = []
        mailto_links = []
        tel_links = []
        empty_links = []
        
        parsed_base = urlparse(base_url)
        base_domain = parsed_base.netloc
        
        for a in all_anchors:
            href = a.get('href', '')
            text = a.get_text(strip=True)[:40] or '[no text]'
            
            if not href:
                empty_links.append({'href': '(empty)', 'text': text})
            elif href.startswith('#'):
                hash_links.append({'href': href, 'text': text})
            elif href.startswith('javascript:'):
                javascript_links.append({'href': href[:50], 'text': text})
            elif href.startswith('mailto:'):
                mailto_links.append({'href': href, 'text': text})
            elif href.startswith('tel:'):
                tel_links.append({'href': href, 'text': text})
            else:
                full_url = urljoin(url, href).split('#')[0]
                parsed = urlparse(full_url)
                
                if parsed.netloc == base_domain or not parsed.netloc:
                    internal_links.append({'href': full_url, 'text': text})
                else:
                    external_links.append({'href': full_url, 'text': text})
        
        # Summary
        print(f"\n📊 LINK SUMMARY:")
        print(f"   Total <a> tags found:  {len(all_anchors)}")
        print(f"   ├── Internal links:    {len(internal_links)}")
        print(f"   ├── External links:    {len(external_links)}")
        print(f"   ├── Hash links (#):    {len(hash_links)}")
        print(f"   ├── JavaScript links:  {len(javascript_links)}")
        print(f"   ├── Mailto links:      {len(mailto_links)}")
        print(f"   ├── Tel links:         {len(tel_links)}")
        print(f"   └── Empty href:        {len(empty_links)}")
        
        # What the checker actually checks
        checkable = len(internal_links) + len(external_links)
        print(f"\n✅ CHECKABLE LINKS (what monitor checks): {checkable}")
        
        # Show unique internal links
        unique_internal = list(set(l['href'] for l in internal_links))
        print(f"\n🔗 UNIQUE INTERNAL LINKS ({len(unique_internal)}):")
        for i, link in enumerate(sorted(unique_internal)[:30], 1):
            print(f"   {i:2}. {link}")
        if len(unique_internal) > 30:
            print(f"   ... and {len(unique_internal) - 30} more")
        
        # Show unique external links
        unique_external = list(set(l['href'] for l in external_links))
        if unique_external:
            print(f"\n🌐 UNIQUE EXTERNAL LINKS ({len(unique_external)}):")
            for i, link in enumerate(sorted(unique_external)[:10], 1):
                print(f"   {i:2}. {link}")
            if len(unique_external) > 10:
                print(f"   ... and {len(unique_external) - 10} more")
        
        # Check for duplicates (nav/footer appearing multiple times)
        link_counts = Counter(l['href'] for l in internal_links)
        duplicates = {k: v for k, v in link_counts.items() if v > 1}
        if duplicates:
            print(f"\n🔄 DUPLICATE LINKS (same link appears multiple times):")
            for link, count in sorted(duplicates.items(), key=lambda x: -x[1])[:10]:
                print(f"   {count}x: {link}")
        
        return {
            'total': len(all_anchors),
            'internal': len(internal_links),
            'external': len(external_links),
            'unique_internal': len(unique_internal),
            'unique_external': len(unique_external)
        }
        
    except Exception as e:
        print(f"❌ Error: {e}")
        return None


def main():
    if len(sys.argv) < 2:
        print("Usage: python diagnose_links.py <base_url> [page1] [page2] ...")
        print("Example: python diagnose_links.py https://example.com / /about/ /contact/")
        sys.exit(1)
    
    base_url = sys.argv[1]
    if not base_url.startswith(('http://', 'https://')):
        base_url = 'https://' + base_url
    
    pages = sys.argv[2:] if len(sys.argv) > 2 else ['/']
    
    print(f"\n🔍 LINK DIAGNOSTIC TOOL")
    print(f"Base URL: {base_url}")
    print(f"Pages to check: {pages}")
    
    results = {}
    for page in pages:
        result = count_links_on_page(base_url, page)
        if result:
            results[page] = result
    
    # Compare pages
    if len(results) > 1:
        print(f"\n\n{'='*70}")
        print("📈 COMPARISON ACROSS PAGES")
        print('='*70)
        print(f"{'Page':<30} {'Total':<8} {'Internal':<10} {'External':<10} {'Unique':<10}")
        print('-'*70)
        for page, data in results.items():
            print(f"{page:<30} {data['total']:<8} {data['internal']:<10} {data['external']:<10} {data['unique_internal']:<10}")


if __name__ == '__main__':
    main()
