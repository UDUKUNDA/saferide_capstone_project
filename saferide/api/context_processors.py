from django.conf import settings

def global_settings(request):
    return {
        'google_maps_api_key': settings.GOOGLE_MAPS_API_KEY,
    }
