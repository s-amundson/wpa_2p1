from .models import Policy

def policy_list(request):
    return {
        "policies": Policy.objects.filter(policytext__status=1).distinct(),
    }
