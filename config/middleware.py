class PermissionsPolicyMiddleware:
    """
    Ajoute l'en-tête `Permissions-Policy` : le navigateur refuse à cette page (et à tout contenu
    intégré) l'accès à la caméra, au micro, à la position et au suivi publicitaire FLoC.
    Aucune de ces fonctions n'est utilisée par le site : autant les désactiver.
    """

    POLICY = "camera=(), microphone=(), geolocation=(), interest-cohort=()"

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        response = self.get_response(request)
        response.headers.setdefault("Permissions-Policy", self.POLICY)
        return response
