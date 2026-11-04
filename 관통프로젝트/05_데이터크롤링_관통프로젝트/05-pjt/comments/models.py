from django.db import models

# Create your models here.
class CommentAnalysis(models.Model):
    # 사용자가 입력한 회사명
    input_name = models.CharField(max_length=100)

    # 실제 검색된 종목명
    company_name = models.CharField(max_length=100)

    # 종목코드
    company_code = models.CharField(max_length=20, blank=True)

    # 원본 댓글
    raw_comments = models.JSONField(default=list)

    # 정제 댓글
    cleaned_comments = models.JSONField(default=list)

    # 증강 댓글
    augmented_comments = models.JSONField(default=list)

    # IQR 임계값 정보
    iqr_thresholds = models.JSONField(default=dict)

    # 생성 일시
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.company_name