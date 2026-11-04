
from django.shortcuts import render
from .models import CommentAnalysis

# B가 작성한 파이프라인 불러오기
from run_pipeline import run_pipeline


def index(request):
    context = {}

    if request.method == "POST":

        # F601: 회사명 입력받기
        company_name = request.POST.get(
            "company_name", ""
        ).strip()

        context["company_name"] = company_name

        # 빈 입력 방지
        if not company_name:
            context["error"] = "회사명을 입력해주세요."
            return render(
                request,
                "comments/index.html",
                context
            )

        print("입력한 회사명:", company_name)

        try:
            # F603~F606: B의 통합 파이프라인 실행
            result = run_pipeline(
                company_name,
                limit=20,
                criteria_name="strict",
                headless=True
            )

            # 댓글이 없는 경우
            if result.get("message"):
                context["error"] = result["message"]
                return render(
                    request,
                    "comments/index.html",
                    context
                )

            # 단계별 결과 가져오기
            raw_comments = result.get(
                "raw_comments", []
            )
            cleaned_comments = result.get(
                "cleaned_comments", []
            )
            augmented_comments = result.get(
                "augmented_comments", []
            )

            # 증강 실패 시 성공한 분석으로 저장하지 않음
            if not augmented_comments:
                context["error"] = (
                    "증강 결과가 없습니다. "
                    "정제 결과와 LLM 응답을 확인해주세요."
                )
                return render(
                    request,
                    "comments/index.html",
                    context
                )

            # F607: DB 저장
            analysis = CommentAnalysis.objects.create(
                input_name=company_name,
                company_name=(
                    result.get("company_name")
                    or company_name
                ),
                company_code=(
                    result.get("company_code")
                    or ""
                ),
                raw_comments=raw_comments,
                cleaned_comments=cleaned_comments,
                augmented_comments=augmented_comments,
                iqr_thresholds=result.get(
                    "iqr_thresholds", {}
                ),
            )

            # F607: HTML 화면으로 전달
            context["analysis"] = analysis
            context["counts"] = result.get(
                "counts", {}
            )

        except Exception as e:
            print("프로젝트 실행 오류:", repr(e))

            context["error"] = (
                "분석 과정에서 오류가 발생했습니다. "
                "터미널을 확인해주세요."
            )

    return render(
        request,
        "comments/index.html",
        context
    )
