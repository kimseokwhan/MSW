from django.db import models

# Create your models here.

# 게시글 저장을 위한 테이블 설계
# 우리가 DB와 상호작용하는 것을 직접 개발하려면 굉장히 많은 것들을 고려해야 합니다.
# 보안, 어떤 방식으로 소통을 할지, 여러 기능 등(수정, 삭제 등등)...
# 그래서 Django는 이러한 기본적인 설계 기능을 미리 구현을 해놓았음 ==> models라는 모듈에 구현
# 우리가 해야하는 건 그냥 models 모듈에서 필요한 클래스, 함수들을 잘 가져다가 사용하는 것!
# 기본적인 model class에 대한 구현이 완료된 Model 클래스를 상속 받으면서 시작.
class Article(models.Model):
    # 우리는 Model 클래스를 상속받으면서 다른 것들을 고민할 필요없이
    # 지금 해야할 것(테이블의 컬럼을 정의하고, 여러 제약조건들을 정의하는 일)에 대해서만 개발할 수 있음
    # 컬럼을 정의할 때 id 컬럼은 django가 알아서 만들어 줌
    # 컬럼은 클래스 변수로 정의
    # 컬럼의 기본 틀(클래스) 자체도 django가 제공을 해줌
    title = models.CharField(max_length=10)
    content = models.TextField()
    # 추가 필드 정의
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)