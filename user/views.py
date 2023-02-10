from knox.auth import AuthToken
from .serializers import RegisterSerializer,LoginSerializer,ProfileSerializer,ChangePasswordSerializer
from .models import Profile
from rest_framework import generics,permissions,parsers
from rest_framework.response import Response
from django.urls import reverse
from knox.auth import TokenAuthentication
# Create your views here.


class ChangePasswordAPI(generics.GenericAPIView):
    serializer_class = ChangePasswordSerializer
    parser_classes = [parsers.FormParser,parsers.JSONParser]
    authentication_classes = [TokenAuthentication]
    permission_classes = [permissions.IsAuthenticated]

    def get_serializer_context(self):
        context =  super().get_serializer_context()
        context.update({"request":self.request})
        return context
    
    def post(self,request):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.validated_data
        return Response({"message":"Password changed successfully"},status=200)




class ApiRoot(generics.GenericAPIView):
    authentication_classes = [TokenAuthentication]
    def get(self,request,*args,**kwargs):
        print(request.user)
        if request.user.is_authenticated:
            return Response({"urls":[
                request.build_absolute_uri(reverse('user'))
            ]})
        else:
            return Response({"urls":[
                request.build_absolute_uri(reverse('register_api')),
                request.build_absolute_uri(reverse('login_api')),
            ]})





class RegisterAPI(generics.GenericAPIView):
    serializer_class = RegisterSerializer
    parser_classes = [parsers.JSONParser]


    def post(self,request,*args,**kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response({"message":"Sign Up successful.Please procced to login."},status=201)

class LoginAPI(generics.GenericAPIView):
    serializer_class = LoginSerializer
    parser_classes = [parsers.FormParser,parsers.MultiPartParser]

    def post(self,request,*args,**kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.validated_data
        return Response({
            "message":"Login Successful.",
            "token":AuthToken.objects.create(user)[1]
        },status=200)


class ProfileAPI(generics.RetrieveUpdateAPIView):
    serializer_class = ProfileSerializer
    authentication_classes = [TokenAuthentication]
    permission_classes = [permissions.IsAuthenticated]

    def get_object(self):
        return Profile.objects.get(id = self.request.user.id)
    
    def put(self, request, *args, **kwargs):
        return self.update(request, *args, **kwargs)
    def patch(self, request, *args, **kwargs):
        return self.partial_update(request, *args, **kwargs)