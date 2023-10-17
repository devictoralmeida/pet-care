from rest_framework.views import APIView, Response, Request, status


class GroupView(APIView):
    def get(self, request: Request) -> Response:
        return Response

    def post(self, request: Request) -> Response:
        return Response
