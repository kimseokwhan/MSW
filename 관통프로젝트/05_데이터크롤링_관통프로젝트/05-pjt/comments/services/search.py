"""F603 회사 검색 — crawler.py의 검증된 검색 로직을 재사용."""

from crawler import get_driver, get_stock_code, open_main
from crawler import search_company as select_exact_company


def search_company(name):
    """회사명 -> {company_name, company_code, company_url}.

    실제 페이지의 종목명과 코드만 반환한다. 일치하지 않으면 예외 발생.
    """
    driver = get_driver(headless=True)
    try:
        open_main(driver)
        matched_name = select_exact_company(driver, name)
        code = get_stock_code(driver)
        return {
            'company_name': matched_name,
            'company_code': code,
            'company_url': driver.current_url,
        }
    finally:
        driver.quit()
