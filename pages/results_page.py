import math
import re

from selenium.common import TimeoutException
from selenium.webdriver.common.by import By

from common.utils import clean_text, get_xpath
from models.reaction import Reaction
from models.reference import Reference
from models.stage import Stage
from pages.base_page import BasePage


class ResultsPage(BasePage):
    RESULTS_LIST_ITEM = (By.TAG_NAME, 'sf-reaction-group')
    VIEW_ALL_BUTTON = (By.CLASS_NAME, 'reaction-view-group')
    CLOSE_BUTTON = (By.XPATH, "//button[@aria-label='Close Modal']")
    CAS_NUMBER = (By.CLASS_NAME, 'registry-number')

    def parse_scheme(self, scheme):
        # tabular_component = scheme.find(
        #     'sf-tabular-inorganic',
        # )
        # if tabular_component is not None:
        #     return []
        reactants = self.parse_components(
            scheme, 'reaction-tile-reactant',
        )
        products = self.parse_components(
            scheme, 'reaction-tile-product',
        )
        reaction_divs = scheme.find_all(
            'div', {'class': 'component-item'},
        )
        reactions = []
        for reaction_div in reaction_divs:
            yield_value, reaction_id, stages, reference = self.parse_reaction(
                reaction_div,
            )
            reaction = Reaction(
                reaction_id=reaction_id,
                reactants=reactants,
                products=products,
                stages=stages,
                stages_number=len(stages),
                yield_value=yield_value,
                reference=reference,
            )
            reactions.append(reaction)
        return reactions

    def parse_components(self, scheme, component_class):
        component_divs = scheme.find_all(
            'div', {'class': component_class},
        )
        components = []
        for component_div in component_divs:
            no_image_div = component_div.find(
                'div', {'class': 'rn-no-image'},
            )
            group_div = component_div.find('figcaption')
            if no_image_div is not None:
                components.append(
                    no_image_div.get_text(),
                )
            elif group_div is not None:
                components.append(
                    '-'.join(group_div['id'].split('-')[3:]),
                )
            else:
                component_text = component_div.find(
                    'img',
                )['alt'].split('.')[0]
                components.append(
                    component_text.split()[-1],
                )
        return components

    def parse_reaction(self, reaction):
        yield_value = reaction.find(
            'span', {'class': 'yield-value'},
        ).get_text()
        reaction_id = reaction.find(
            'span', {'class': 'reaction-view-detail'},
        ).get_text()
        reference = self.parse_reference(
            reaction,
        )
        stage_divs = reaction.find_all(
            'div', {'class': 'summary-stage'},
        )
        stages = []
        for idx, stage_div in enumerate(stage_divs):
            reagents, catalysts, solvents, other_conditions = self.parse_stage(
                stage_div,
            )
            stage = Stage(
                stage_number=idx + 1,
                reagents=reagents,
                catalysts=catalysts,
                solvents=solvents,
                other_conditions=other_conditions,
            )
            stages.append(stage)
        return yield_value, reaction_id, stages, reference

    def parse_reference(self, reaction):
        title = clean_text(
            reaction.find(
                'h4', {'class': 'reaction-reference-title'},
            ).get_text(),
        )
        authors = reaction.find(
            'span', {'class': 'authors-text'},
        )
        if authors is None:
            authors = reaction.find(
                'span', {'class': 'inventors-text'},
            )
        if authors is not None:
            authors = clean_text(
                authors.text.split(';')[0].strip(),
            )
        else:
            authors = ''
        bibliography = clean_text(
            reaction.find(
                'div', {'class': 'bibliography'},
            ).get_text(),
        )
        return Reference(
            title=title,
            authors=authors,
            bibliography=bibliography,
        )

    def parse_stage(self, stage):
        reagents = self.parse_condition_type(
            stage, 'stage-reagent',
        )
        catalysts = self.parse_condition_type(
            stage, 'stage-catalyst',
        )
        solvents = self.parse_condition_type(
            stage, 'stage-solvent',
        )
        other_conditions_div = stage.find(
            'span', {'class': 'stage-conditions'},
        )
        other_conditions = ''
        if other_conditions_div is not None:
            other_conditions = clean_text(
                other_conditions_div.get_text(),
            )
        return reagents, catalysts, solvents, other_conditions

    def parse_condition_type(self, stage, condition_type):
        spans = stage.find_all(
            'span', {'class': condition_type},
        )
        components = []
        for span in spans:
            component = clean_text(
                span.get_text(),
            ).removesuffix(' ,')
            if component.endswith('…'):
                component_link = span.find('a')
                self.click((By.XPATH, get_xpath(component_link)))
                components.append(self.find_element(self.CAS_NUMBER).text)
                self.escape()
            else:
                components.append(component)
        return components

    def parse(self, page_size, subpage_size):
        reactions = []
        for scheme_idx in range(page_size):
            self.wait_page_loading(page_size)
            main_page_source = self.get_page_source(no_delay=True)
            scheme = main_page_source.find_all(
                self.RESULTS_LIST_ITEM[1],
            )[scheme_idx]
            view_all_button = scheme.find(
                'div', {'class': self.VIEW_ALL_BUTTON[1]},
            )
            if view_all_button is not None:
                svg_icon = view_all_button.find('svg')
                xpath = get_xpath(view_all_button.find('a'))
                self.click((By.XPATH, xpath))
                if svg_icon is not None:
                    main_page_source = self.get_page_source(no_delay=False)
                    scheme = main_page_source.find_all(
                        self.RESULTS_LIST_ITEM[1],
                    )[scheme_idx]
                    reactions.extend(self.parse_scheme(scheme))
                else:
                    reactions.extend(self.parse_subpage(subpage_size))
            else:
                reactions.extend(self.parse_scheme(scheme))
        return reactions

    def parse_subpage(self, page_size):
        self.wait_page_loading(1)
        subpage_source = self.get_page_source(no_delay=True)
        subpage_url = '/'.join(
            self.get_current_url().split('/')[:-1],
        )

        scheme = subpage_source.find(
            self.RESULTS_LIST_ITEM[1],
        )
        conditions_number_text = scheme.find(
            'span', {'class': 'reaction-title-sub'},
        ).get_text()
        conditions_number = int(
            re.findall(r'\d+', conditions_number_text)[0],
        )
        pages_number = math.ceil(conditions_number / page_size)

        reactions = []
        for page in range(pages_number):
            reactions.extend(self.parse_scheme(scheme))
            if page + 1 != pages_number:
                next_page_url = '{url}/{page}'.format(
                    url=subpage_url,
                    page=page + 2,
                )
                self.go_to(next_page_url)
                self.wait_page_loading(1)
                subpage_source = self.get_page_source(no_delay=True)
                scheme = subpage_source.find(
                    self.RESULTS_LIST_ITEM[1],
                )

        for _ in range(pages_number):
            self.back()

        return reactions

    def wait_page_loading(self, page_size):
        for _ in range(self.n_retries):
            try:
                return self.wait_elements(
                    self.RESULTS_LIST_ITEM, page_size,
                )
            except TimeoutException:
                self.refresh()
        raise TimeoutException(
            'The page failed to load after {0} retries'.format(
                self.n_retries,
            ),
        )
