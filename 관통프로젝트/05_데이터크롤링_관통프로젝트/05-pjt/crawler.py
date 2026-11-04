"""
crawler.py : 토스증권 커뮤니티 댓글 수집 모듈

03_toss_comments 에서 만든 함수를 한 파일에 모았습니다.
다른 파일에서는 fetch_comments() 하나만 가져다 쓰면 됩니다.

    from crawler import fetch_comments
    comments = fetch_comments('삼성전자', limit=20)
"""

import re
import time

from selenium import webdriver
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

MAIN_URL = 'https://www.tossinvest.com/'


# ------------------------------------------------------------
# 브라우저 실행 (headless 옵션 추가)
# ------------------------------------------------------------
def get_driver(headless=False):
    """옵션을 적용한 크롬 브라우저를 실행해 돌려준다"""
    chrome_options = webdriver.ChromeOptions()
    chrome_options.add_experimental_option('excludeSwitches', ['enable-logging'])
    if headless:
        # 창 없이 백그라운드로 실행 (웹 서비스 안에서 실행할 때)
        chrome_options.add_argument('--headless=new')
        # 창 크기를 지정하지 않으면 작은 화면(모바일) 배치로 그려질 수 있음
        chrome_options.add_argument('--window-size=1920,1080')
    return webdriver.Chrome(options=chrome_options)


# ------------------------------------------------------------
# 03_toss_comments 에서 만든 함수
# ------------------------------------------------------------
def open_main(driver):
    """토스증권 메인 페이지에 접속하고, 화면이 그려질 때까지 기다린다"""
    driver.get(MAIN_URL)

    # 왼쪽 메뉴(#ts-lnb)는 자바스크립트가 화면을 그린 뒤에 나타나는 요소
    # 최대 10초 동안 반복 확인 -> 나타나는 순간 바로 다음 줄로 진행
    # 10초가 지나도 없으면 TimeoutException 발생
    WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.CSS_SELECTOR, '#ts-lnb'))
    )
    print('[접속] 토스증권 메인 페이지 로딩 완료')


def close_popups(driver):
    """첫 진입 시 뜨는 안내 팝업의 닫기 버튼을 모두 누른다"""
    # 팝업은 페이지가 그려진 뒤 조금 늦게 뜨는 경우가 있어 잠깐 대기
    time.sleep(1)

    # XPath: //태그[@속성='값'] -> aria-label 이 '닫기'인 모든 button
    for close_btn in driver.find_elements(By.XPATH, "//button[@aria-label='닫기']"):
        try:
            if close_btn.is_displayed():
                # 일부 닫기 버튼은 다른 요소(왼쪽 메뉴)에 가려져 일반 click() 이 실패함
                # -> 자바스크립트로 버튼을 직접 클릭
                driver.execute_script('arguments[0].click();', close_btn)
                time.sleep(0.5)
        except Exception:
            # 닫기에 실패해도 진행에는 큰 문제가 없으므로 넘어감
            pass


def _normalise_name(text):
    """회사명 비교용: 공백·대소문자 차이만 무시한다."""
    return re.sub(r'\s+', '', text).casefold()


def _exact_result_name(element, requested):
    """검색 결과의 '종목명 한 줄'이 입력한 회사명과 동일할 때만 반환."""
    wanted = _normalise_name(requested)
    for line in element.text.splitlines():
        name = line.strip()
        if name and _normalise_name(name) == wanted:
            return name
    return None


def _get_page_stock_name(driver, requested):
    """Enter 이동 시 이름이 맞는지 확인 (브라우저 title을 무조건 신뢰하지 않음)."""
    for selector in ('h1', '[data-testid="stock-name"]', '[data-testid="stockName"]', 'h2'):
        for element in driver.find_elements(By.CSS_SELECTOR, selector):
            matched = _exact_result_name(element, requested)
            if matched:
                return matched

    # title은 '삼성바이오로직스 | 토스증권'처럼 서비스명이 뒤에 붙을 수 있음.
    title = driver.title or ''
    title_head = re.split(r'\s*[|·\-]\s*', title, maxsplit=1)[0].strip()
    if _normalise_name(title_head) == _normalise_name(requested):
        return title_head
    return None


def search_company(driver, company_name):
    """입력한 회사와 정확히 일치하는 종목을 골라 종목명을 반환한다.

    일치 결과가 없으면 첫 번째 검색 결과를 무조건 선택하지 않는다.
    """
    company_name = company_name.strip()
    if not company_name:
        raise ValueError('회사명을 입력해주세요.')

    close_popups(driver)
    driver.execute_script('document.activeElement.blur(); document.body.focus();')
    ActionChains(driver).send_keys('/').perform()

    search_input = WebDriverWait(driver, 10).until(
        EC.visibility_of_element_located(
            (By.XPATH, "//input[@placeholder='검색어를 입력해주세요']")
        )
    )
    search_input.clear()
    search_input.send_keys(company_name)

    # 검색 모달의 실제 결과에서 '정확한 이름'의 항목을 찾는다.
    # a[href] 기반이며, 접근성 옵션/버튼 형태도 후보로 다룬다.
    selector = (
        "a[href*='/stocks/'], [role='option'], "
        "[role='listbox'] button"
    )

    def find_exact_item(current_driver):
        for item in current_driver.find_elements(By.CSS_SELECTOR, selector):
            try:
                if item.is_displayed() and _exact_result_name(item, company_name):
                    return item
            except Exception:
                continue
        return False

    try:
        item = WebDriverWait(driver, 8).until(find_exact_item)
    except TimeoutException:
        # 일부 화면에서는 검색 결과 링크가 노출되지 않고 Enter로만 이동함.
        # 이때도 실제 상세 페이지의 종목명이 일치하지 않으면 실패로 처리한다.
        search_input.send_keys(Keys.ENTER)
        get_stock_code(driver)
        try:
            matched_name = WebDriverWait(driver, 10).until(
                lambda d: _get_page_stock_name(d, company_name)
            )
        except TimeoutException as exc:
            raise ValueError(
                f'정확히 일치하는 종목을 확인할 수 없습니다: {company_name}'
            ) from exc
    else:
        matched_name = _exact_result_name(item, company_name)
        try:
            item.click()
        except Exception:
            driver.execute_script('arguments[0].click();', item)
        get_stock_code(driver)  # 종목 상세 페이지 이동 검증

    print(f'[검색] {company_name} -> {matched_name}')
    return matched_name


def get_stock_code(driver):
    """현재 실제 종목 페이지 URL (/stocks/A207940/...) 에서 코드 추출."""
    def parse_code(current_driver):
        match = re.search(r'/stocks/([A-Za-z0-9]+)(?:/|$)', current_driver.current_url)
        return match.group(1) if match else False

    stock_code = WebDriverWait(driver, 15).until(parse_code)
    print(f'[종목 코드] {stock_code} ({driver.current_url})')
    return stock_code


def open_community(driver, stock_code):
    """종목 코드로 커뮤니티 페이지 주소를 만들어 바로 이동한다"""
    community_url = f'https://www.tossinvest.com/stocks/{stock_code}/community'
    driver.get(community_url)

    # 댓글 영역(#stock-content)이 나타날 때까지 대기
    # 시간이 초과해도 프로그램을 멈추지 않고 안내만 출력
    try:
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, '#stock-content'))
        )
        print('[커뮤니티] 댓글 영역 로딩 완료')
    except TimeoutException:
        print('[커뮤니티] 10초 안에 댓글 영역을 찾지 못했습니다. 화면을 확인하세요.')


# 댓글 본문 선택자 : 클래스 이름이 아니라 "역할"을 나타내는 속성을 기준으로
#   - 개발자 도구에 보이는 클래스 이름(예: tc3tm85)은 사이트를 새로 배포할 때마다 바뀜
#   - style 안의 --fold-after-lines("N줄까지만 보여주고 접기")는 게시글 본문에만 있음
COMMENT_SELECTOR = "span[style*='--fold-after-lines']"


def read_visible_comments(driver, comments):
    """지금 화면에 보이는 댓글을 comments 리스트에 추가한다 (중복 제외)"""
    for span in driver.find_elements(By.CSS_SELECTOR, COMMENT_SELECTOR):
        text = span.text.strip()
        if text and text not in comments:
            comments.append(text)


def find_scroll_container(driver):
    """댓글 목록을 감싼 내부 스크롤 영역을 찾는다 (없으면 None)"""
    # 댓글 목록은 페이지 전체(window)가 아니라 내부의 별도 스크롤 상자에서 스크롤됨
    # data-id 가 'base-ui-' 로 시작하고 '-viewport' 로 끝나는 div
    try:
        return driver.find_element(
            By.CSS_SELECTOR, "div[data-id^='base-ui-'][data-id$='-viewport']"
        )
    except Exception:
        return None


def collect_comments(driver, limit=20, max_scroll=30):
    """스크롤을 반복하며 댓글을 최대 limit 개까지 모아 돌려준다"""
    # 첫 댓글이 화면에 그려질 때까지 대기
    try:
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, COMMENT_SELECTOR))
        )
    except TimeoutException:
        print('[수집] 댓글을 찾지 못했습니다. 선택자가 바뀌었는지 확인하세요.')
        return []

    scroll_container = find_scroll_container(driver)
    comments = []
    prev_count = -1  # 직전 반복의 댓글 개수
    stagnant_rounds = 0  # 댓글 개수가 그대로인 횟수

    for scroll in range(max_scroll):
        read_visible_comments(driver, comments)
        print(f'[수집] 스크롤 {scroll + 1}회 -> 누적 {len(comments)}개')

        # 목표 개수 도달 또는 스크롤 상자가 없으면 종료
        if len(comments) >= limit or scroll_container is None:
            break

        # 스크롤해도 5번 연속 늘지 않으면 더 이상 댓글이 없다고 판단
        if len(comments) == prev_count:
            stagnant_rounds += 1
            if stagnant_rounds >= 5:
                break
        else:
            stagnant_rounds = 0
        prev_count = len(comments)

        # 스크롤 상자를 클릭해 포커스를 준 뒤 End 키 -> 상자 맨 아래로 스크롤
        scroll_container.click()
        scroll_container.send_keys(Keys.END)
        time.sleep(1.5)  # 새 댓글을 불러올 시간

    # 마지막 스크롤에서 limit 보다 많이 모일 수 있으므로 정확히 잘라서 반환
    return comments[:limit]


# ------------------------------------------------------------
# 외부에서 사용할 함수 : 회사명 => 댓글 리스트
# ------------------------------------------------------------
def fetch_stock_comments(company_name, limit=20, headless=False):
    """회사명 => {'stock_code', 'stock_name', 'comments'} (실패하면 comments 가 빈 리스트)"""
    driver = get_driver(headless)
    try:
        open_main(driver)
        stock_name = search_company(driver, company_name)
        stock_code = get_stock_code(driver)
        open_community(driver, stock_code)
        comments = collect_comments(driver, limit=limit)
        return {'stock_code': stock_code, 'stock_name': stock_name, 'comments': comments}
    except (TimeoutException, ValueError) as exc:
        print(f'[수집 실패] {company_name}: {exc}')
        return {'stock_code': '', 'stock_name': '', 'comments': []}
    finally:
        driver.quit()


# 이 파일을 직접 실행할 때만 동작 (import 할 때는 실행되지 않음)
if __name__ == '__main__':
    result = fetch_stock_comments('삼성바이오로직스', limit=5)
    print(f"종목명: {result['stock_name']} / 종목코드: {result['stock_code']}")
    for idx, comment in enumerate(result['comments'], 1):
        print(f'{idx:02d}. {comment}')
