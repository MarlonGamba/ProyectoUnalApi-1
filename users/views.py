#PARA CONTROLAR LAS SESIONES ACTIVAS

from django.contrib.admin.sites import all_sites
from django.contrib.sessions.models import Session
from datetime import datetime



from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
# PARA GENERAL Y ACTUALIZAR TOKEN
from rest_framework.authtoken.models import Token
from rest_framework.authtoken.views import ObtainAuthToken

#EL ZERIALIZER QUE SE VA A MOSTART AL INICIAR SESION
from users.api.serializers import UserTokenSerializer
from users.models import User


class UserToken(APIView):
  def get(self,request,*args,**kwargs):
    username = request.GET.get('username')
    try:
      user_token = Token.objects.get(user= UserTokenSerializer().Meta
      .model.objects.filter(username = username).first())
      return Response({
        'token': user_token.key
      })
    except:
      return Response({
        'error':'Credenciales enviadas incorrectas'
      },status= status.HTTP_400_BAD_REQUEST)
      





class Login(ObtainAuthToken):

  def post(self,request,*args,**kwargs):    
    login_serializer = self.serializer_class(data = request.data, context = {'request':request})

    if login_serializer.is_valid():    
      user = login_serializer.validated_data['user']
      if user.is_active:
        token,created= Token.objects.get_or_create(user = user)
        user_serializer= UserTokenSerializer(user)         
        if created:
          return Response({
            'token': token.key,
            'user':user_serializer.data,
            'mensaje':'Inicio de sesion exitoso'
          },status=status.HTTP_201_CREATED)
        else:
          '''PARA CERRAR SESIONES Y GENERAR UN NUEVO TOKEN'''
          
          all_sessions= Session.objects.filter(expire_date__gte=datetime.now())         
          if all_sessions.exists():            
            for session in all_sessions:
              session_data=session.get_decoded()
              if user.id == int(session_data.get('_auth_user_id')):
                session.delete()
          token.delete()
          token=Token.objects.create(user=user)         
          return Response({
            'token': token.key,
            'user':user_serializer.data,
            'mensaje':'Inicio de sesion exitoso'
          },status=status.HTTP_201_CREATED)
          '''
          # SI QUEREMOS QUE INICIE EN UNA SOLA SESION 
          token.delete()
          return Response({
            'error':'Ya se ha iniciado sesion con este usuario'
         }, status=status.HTTP_409_CONFLICT)
          '''
      else:
        return Response({'mensaje': 'Este usuario no esta logueado'},status=status.HTTP_401_UNAUTHORIZED) 

    else:
      return Response({'mensaje':'Nombre de usuario o contraseña incorrectos'},status=status.HTTP_400_BAD_REQUEST)

    



class Logout(APIView):
  def get(self,request,*args,**kwargs):
    try:
      token=request.GET.get('token')        
      token=Token.objects.filter(key=token).first()
      #token=Token.objects.filter(key=request.GET.get('token')).first()        
      if token:
        user=token.user
        all_sessions= Session.objects.filter(expire_date__gte=datetime.now())        
        if all_sessions.exists():
          for session in all_sessions:
            session_data=session.get_decoded()              
            if user.id == int(session_data.get('_auth_user_id')):
              session.delete()

        token.delete()

        session_message='Sesion de usuario eliminada'
        token_message= 'Token eliminado'
        return Response({
          'mensaje sesion':session_message,
          'mensaje token': token_message
        },status=status.HTTP_200_OK)
      return Response({
      'error':'Nose ha encontrado un usuario con estas credenciales'
      },status=status.HTTP_400_BAD_REQUEST)

    except: 
      return Response({
        'error':'No se ha encontrado token en la peticion'
       },status=status.HTTP_409_CONFLICT)    
      
      