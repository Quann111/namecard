from .models import Profile

def current_profile(request):
    cid = request.session.get("current_id")
    if cid:
        try:
            return {"profile": Profile.objects.get(id=cid)}
        except Profile.DoesNotExist:
            return {"profile": None}
    return {"profile": None}
