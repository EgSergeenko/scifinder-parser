def visibility_of_elements_located(locator, number):
    def _predicate(driver):
        elements = driver.find_elements(*locator)
        if number and len(elements) != number:
            return False
        if all(element.is_displayed() for element in elements):
            return elements
    return _predicate
