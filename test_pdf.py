"""Test PDF generation with xhtml2pdf"""
from pathlib import Path
import sys
sys.path.insert(0, str(Path(__file__).parent))

from utils.reporting import ReportGenerator

# Create test data
test_data = {
    'stats': {
        'website_name': 'Test Website',
        'website_url': 'https://example.com',
        'total_checks': 10,
        'successful_checks': 8,
        'failed_checks': 2,
        'avg_response_time': 250,
        'uptime_percentage': 95.5
    },
    'issues': [
        {
            'severity': 'critical',
            'message': 'SSL certificate expired',
            'monitor': 'SSL Monitor',
            'url': 'https://example.com',
            'details': {}
        },
        {
            'severity': 'high',
            'message': '2 broken links found',
            'monitor': 'Link Checker',
            'url': 'https://example.com/page1',
            'details': {
                'broken_links': [
                    {
                        'link_url': 'https://example.com/missing',
                        'link_text': 'Missing Page',
                        'status_code': 404,
                        'status_message': 'Not Found',
                        'found_on_page': 'https://example.com/page1'
                    }
                ]
            }
        }
    ]
}

# Create output directory
output_dir = Path(__file__).parent / 'test_reports'
output_dir.mkdir(exist_ok=True)

print("Testing PDF generation with xhtml2pdf...")
print("-" * 50)

# Test PDF generation
generator = ReportGenerator(output_dir=str(output_dir))
pdf_path = generator._generate_pdf_report('test123', test_data)

if pdf_path:
    print(f"✅ PDF generated successfully!")
    print(f"   Location: {pdf_path}")
    
    pdf_file = Path(pdf_path)
    if pdf_file.exists():
        size_kb = pdf_file.stat().st_size / 1024
        print(f"   Size: {size_kb:.1f} KB")
    else:
        print("   ⚠️ Warning: File not found after generation")
else:
    print("❌ PDF generation failed!")
    
print("-" * 50)
