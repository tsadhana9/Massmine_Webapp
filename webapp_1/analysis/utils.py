from io import BytesIO
from django.http import HttpResponse

from xhtml2pdf import pisa

def render_html_to_pdf(html, context_dict={}):
    result = BytesIO()
    pdf = pisa.pisaDocument(BytesIO(html.encode("utf-8")), result)
    if not pdf.err:
        return HttpResponse(result.getvalue(), content_type='application/pdf')
    return None