from django.conf import settings


def private_links(request):
    return {
        "BOARD_DOCS": settings.PRIVATE_LINKS['BOARD_DOCS'],
    }
# wpa_project/secrets.json