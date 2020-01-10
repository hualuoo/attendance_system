from rest_framework import mixins
from random import choice
from datetime import datetime, timedelta
from .models import UserModel, UserInfo, CaptchaModel
from utils import smtp
from .serializers import UserListSerializer, UserInfoSerializer, UserRegSerializer, VerifyCodeSerializer, ChangeEmailSerializer, ChangePasswordSerializer
from .serializers import checkUserMailSerializer, sendOldMailCaptchaSerializer, confirmMailCaptchaSerializer, sendNewMailCaptchaSerializer

from rest_framework import viewsets
from rest_framework.views import APIView
from rest_framework.authentication import SessionAuthentication
from rest_framework_jwt.authentication import JSONWebTokenAuthentication
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from utils.permission import UserIsOwner, UserInfoIsOwner

# Create your views here.


class UserInfoViewset(mixins.ListModelMixin, mixins.UpdateModelMixin, mixins.RetrieveModelMixin, viewsets.GenericViewSet):
    """
    用户详细信息
    """
    # permission_classes = (IsAuthenticated, UserInfoIsOwner, )
    # authentication_classes = (JSONWebTokenAuthentication, SessionAuthentication)
    queryset = UserInfo.objects.all()
    serializer_class = UserInfoSerializer
    # 根据用户ID查询用户详细信息
    # lookup_field = "user_id"

    """
    def get_queryset(self):
        if self.request.user.is_superuser:
            return UserInfo.objects.all()
        return UserInfo.objects.filter(user=self.request.user)
    """

    def list(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())
        serializer = self.get_serializer(queryset, many=True)

        return Response(
            {
                'data': serializer.data
            })


class UsersViewset(mixins.ListModelMixin, mixins.CreateModelMixin, mixins.UpdateModelMixin, viewsets.GenericViewSet):
    """
    用戶
    """
    authentication_classes = (JSONWebTokenAuthentication, SessionAuthentication)
    serializer_class = UserRegSerializer
    queryset = UserModel.objects.all()

    def get_permissions(self):
        if self.action == "create":
            return []
        if self.action == "update":
            return [IsAuthenticated(), UserIsOwner(), ]
        return []

    def get_serializer_class(self):
        print(self.action)
        if self.action == "list":
            return UserListSerializer
        if self.action == "create":
            return UserRegSerializer
        if self.action == "update":
            return ChangeEmailSerializer
        return UserRegSerializer

    def put(self, request, pk, *args, **kwargs):
        return self.update(request, *args, **kwargs)


class ChangePasswordViewset(mixins.UpdateModelMixin, viewsets.GenericViewSet):
    """
    修改密码
    """
    permission_classes = (IsAuthenticated, UserIsOwner,)
    authentication_classes = (JSONWebTokenAuthentication, SessionAuthentication)
    serializer_class = ChangePasswordSerializer
    queryset = UserModel.objects.all()


class VerifyCodeViewset(mixins.CreateModelMixin, viewsets.GenericViewSet):
    """
    发送邮箱验证码
    """
    permission_classes = (IsAuthenticated, )
    authentication_classes = (JSONWebTokenAuthentication, SessionAuthentication)
    serializer_class = VerifyCodeSerializer

    def generate_code(self):
        """
        生成六位数字的验证码
        """
        seeds = "1234567890"
        random_str = []
        for i in range(6):
            random_str.append(choice(seeds))
        return "".join(random_str)

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        email = serializer.validated_data["email"]

        code = self.generate_code()

        smtp.code_smtp(email, code)
        code_record = CaptchaModel(email=email, code=code)
        code_record.save()
        return Response({
            "msg": "发送成功"
        }, status=status.HTTP_201_CREATED)


class getUserFuzzyMailViewset(mixins.ListModelMixin, viewsets.GenericViewSet):
    """
        获取模糊用户邮箱
        URL:
            /member/security/getUserFuzzyMail/
        TYPE:
            GET
    """
    permission_classes = (IsAuthenticated, )
    authentication_classes = (JSONWebTokenAuthentication, SessionAuthentication)
    queryset = UserModel.objects.all()

    def fuzzy_mail(self, mail):
        end = mail.index("@")
        if end % 2 == 1:
            start = int((end - 1) / 2)
        else:
            start = int(end / 2)
        fuzzyMail = mail.replace(mail[start:end], "****")
        return "".join(fuzzyMail)

    def list(self, request, *args, **kwargs):
        mail = self.request.user.email
        if mail is None:
            return Response({
                'detail': '未绑定邮箱'
            }, status=status.HTTP_400_BAD_REQUEST)
        else:
            return Response({
                "email": self.fuzzy_mail(mail)
            }, status=status.HTTP_200_OK)


class checkUserMailViewset(mixins.CreateModelMixin, viewsets.GenericViewSet):
    """
        检查用户邮箱
        URL:
            /member/security/checkUserMail/
        TYPE:
            POST
        JSON:
            {
                "email": "<email>"
            }
    """
    permission_classes = (IsAuthenticated, )
    authentication_classes = (JSONWebTokenAuthentication, SessionAuthentication)
    serializer_class = checkUserMailSerializer

    def create(self, request, *args, **kwargs):
        user = self.request.user

        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        if user.email is None:
            return Response({
                'detail': '未绑定邮箱'
            }, status=status.HTTP_400_BAD_REQUEST)
        if user.email == serializer.validated_data["email"]:
            return Response({
                "msg": "邮箱校验正确"
            }, status=status.HTTP_200_OK)
        else:
            return Response({
                'detail': '邮箱校验不正确'
            }, status=status.HTTP_400_BAD_REQUEST)


class sendOldMailCaptchaViewset(mixins.CreateModelMixin, viewsets.GenericViewSet):
    """
        向旧邮箱发送验证码
        URL:
            /member/security/sendOldMailCaptcha/
        TYPE:
            POST
    """
    permission_classes = (IsAuthenticated, )
    authentication_classes = (JSONWebTokenAuthentication, SessionAuthentication)
    serializer_class = sendOldMailCaptchaSerializer

    def generate_code(self):
        """
        生成六位数字的验证码
        """
        seeds = "1234567890"
        random_str = []
        for i in range(6):
            random_str.append(choice(seeds))
        return "".join(random_str)

    def create(self, request, *args, **kwargs):
        user = self.request.user

        if user.email is None:
            return Response({
                'detail': '未绑定邮箱'
            }, status=status.HTTP_400_BAD_REQUEST)

        data = request.POST.copy()
        data['email'] = user.email

        serializer = self.get_serializer(data=data)
        serializer.is_valid(raise_exception=True)

        email = serializer.validated_data["email"]
        code = self.generate_code()

        if smtp.code_smtp(email, code) == 1:
            code_record = CaptchaModel(email=email, code=code)
            code_record.save()
            return Response({
                "msg": "发送成功"
            }, status=status.HTTP_201_CREATED)
        else:
            return Response({
                "detail": "发送失败"
            }, status=status.HTTP_400_BAD_REQUEST)


class confirmOldMailCaptchaViewset(mixins.CreateModelMixin, viewsets.GenericViewSet):
    """
        确认旧邮箱验证码
        URL:
            /member/security/confirmOldMailCaptcha/
        TYPE:
            POST
        JSON:
        {
            "code": "<code>"
        }
    """
    permission_classes = (IsAuthenticated, UserIsOwner,)
    authentication_classes = (JSONWebTokenAuthentication, SessionAuthentication)
    serializer_class = confirmMailCaptchaSerializer

    def create(self, request, *args, **kwargs):
        user = self.request.user

        if user.email is None:
            return Response({
                'detail': '未绑定邮箱'
            }, status=status.HTTP_400_BAD_REQUEST)

        data = request.data.copy()
        data['email'] = user.email

        serializer = self.get_serializer(data=data)
        serializer.is_valid(raise_exception=True)

        return Response({
            'msg': '验证码正确'
        }, status=status.HTTP_200_OK)


class sendNewMailCaptchaViewset(mixins.CreateModelMixin, viewsets.GenericViewSet):
    """
        向新邮箱发送验证码
        URL:
            /member/security/sendNewMailCaptcha/
        TYPE:
            POST
        JSON:
            {
                "email": "<email>"
            }
    """
    permission_classes = (IsAuthenticated, )
    authentication_classes = (JSONWebTokenAuthentication, SessionAuthentication)
    serializer_class = sendNewMailCaptchaSerializer

    def generate_code(self):
        """
        生成六位数字的验证码
        """
        seeds = "1234567890"
        random_str = []
        for i in range(6):
            random_str.append(choice(seeds))
        return "".join(random_str)

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        email = serializer.validated_data["email"]
        code = self.generate_code()

        if smtp.code_smtp(email, code) == 1:
            code_record = CaptchaModel(email=email, code=code)
            code_record.save()
            return Response({
                "msg": "发送成功"
            }, status=status.HTTP_201_CREATED)
        else:
            return Response({
                "detail": "发送失败"
            }, status=status.HTTP_400_BAD_REQUEST)


class confirmNewMailCaptchaViewset(mixins.CreateModelMixin, viewsets.GenericViewSet):
    """
        确认新邮箱验证码
        URL:
            /member/security/confirmNewMailCaptcha/
        TYPE:
            POST
        JSON:
            {
                "email": "<email>",
                "code": "<code>"
            }
    """
    permission_classes = (IsAuthenticated,)
    authentication_classes = (JSONWebTokenAuthentication, SessionAuthentication)
    serializer_class = confirmMailCaptchaSerializer

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        return Response({
            'msg': '验证码正确'
        }, status=status.HTTP_200_OK)
