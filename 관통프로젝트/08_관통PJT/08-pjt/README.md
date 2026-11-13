# 관통 프로젝트 원칙
- branch 이름은 각자 이니셜로
- commit은 요구사항번호 + 작업내용요약
- 변수명이랑 함수명은 통일

## 작업내역
공통 : F801 ~ F806
김석환 : F808 ~ F811
김가영 : F807, F812 ~ F814

## F801 ~ F806 구현

- F801: `mypjt` 프로젝트, `books` 앱, Django REST Framework 설정
- F802: 카테고리 이름을 저장하는 `Category` 모델
- F803: 도서 정보와 카테고리를 저장하는 `Book` 모델
- F804: 도서에 연결된 게시글을 저장하는 `Thread` 모델
- F805: 게시글에 연결된 댓글을 저장하는 `Comment` 모델
- F806: 목록 및 상세 조회, 게시글과 댓글 입력 검증을 위한 Serializer

관계는 `Category → Book → Thread → Comment` 순서로 각각 1:N이다.
외래 키에는 `on_delete=models.CASCADE`를 사용하여 상위 데이터 삭제 시 연결된 데이터도 삭제한다.
ISBN은 앞자리 0을 유지할 수 있도록 문자열 필드인 `isbn`으로 저장한다.
생성 시간은 `auto_now_add=True`, 수정 시간은 `auto_now=True`로 자동 기록한다.

### 학습 내용

- ForeignKey로 모델 사이의 N:1 관계를 표현하고 역참조로 연결된 목록을 조회한다.
- ModelSerializer로 모델 필드에 맞는 입력 검증과 응답 데이터 생성을 처리한다.
- 중첩 Serializer와 `source`, `read_only=True`로 조회용 정보와 입력 필드를 구성한다.

### 구현하며 확인한 점

초기 데이터는 외래 키 관계 순서대로 불러와야 한다.
모델과 Serializer를 먼저 준비하면 이후 view에서 조회와 저장 흐름에 집중할 수 있다.
