from .models import Policy

def policy_list(request):
    access = ['public']
    if request.user.is_authenticated:
        if request.user.has_perm('student_app.members'):
            access.append('member')
        if request.user.has_perm('student_app.staff'):
            access.append('staff')
        if request.user.has_perm('student_app.board'):
            access.append('board')
    return {
        "policies": Policy.objects.filter(access__in=access).filter(policytext__status=1).distinct(),
    }
