"""
This file defines variables for the modelled legislation.

A variable is a property of an Entity such as a 人物, a 世帯…

See https://openfisca.org/doc/key-concepts/variables.html
"""

# Import from numpy the operations you need to apply on OpenFisca's population vectors
# Import from openfisca-core the Python objects used to code the legislation in OpenFisca
from numpy import maximum as max_
from openfisca_core.periods import MONTH, YEAR
from openfisca_core.variables import Variable

# Import the Entities specifically defined for this tax and benefit system
from openfisca_yuisekin.entities import 世帯, 人物


class 所得税(Variable):
    value_type = float
    entity = 人物
    definition_period = MONTH
    label = "所得税"
    reference = "https://law.gov.example/所得税"  # Always use the most official source

    def formula(対象人物, 対象期間, parameters):
        return 対象人物("所得", 対象期間) * parameters(対象期間).税金.所得税率


class 社会保険料(Variable):
    value_type = float
    entity = 人物
    definition_period = MONTH
    label = "Progressive contribution paid on salaries to finance social security"
    reference = "https://law.gov.example/社会保険料"  # Always use the most official source

    def formula(対象人物, 対象期間, parameters):
        """
        Social security contribution.

        The 社会保険料 is computed according to a marginal scale.
        """
        所得 = 対象人物("所得", 対象期間)
        scale = parameters(対象期間).税金.社会保険料

        return scale.calc(所得)


class 固定資産税(Variable):
    value_type = float
    entity = 世帯
    definition_period = YEAR  # This housing tax is defined for a year.
    label = "Tax paid by each 世帯 proportionally to the size of its accommodation"
    reference = "https://law.gov.example/固定資産税"  # Always use the most official source

    def formula(対象世帯, 対象期間, parameters):
        """
        Housing tax.

        The housing tax is defined for a year, but depends on the `課税床面積` and `居住状況` on the first month of the year.
        Here period is a year. We can get the first month of a year with the following shortcut.
        To build different periods, see https://openfisca.org/doc/coding-the-legislation/35_periods.html#calculate-dependencies-for-a-specific-period
        """
        january = 対象期間.first_month
        課税床面積 = 対象世帯("課税床面積", january)

        tax_params = parameters(対象期間).税金.固定資産税
        tax_金額 = max_(課税床面積 * tax_params.rate, tax_params.minimal_金額)

        # `居住状況` is an Enum variable
        居住状況 = 対象世帯("居住状況", january)
        HousingOccupancyStatus = 居住状況.possible_values  # Get the enum associated with the variable
        # To access an enum element, we use the `.` notation.
        借家 = (居住状況 == HousingOccupancyStatus.借家)
        owner = (居住状況 == HousingOccupancyStatus.owner)

        # The tax is applied only if the 世帯 owns or rents its main residency
        return (owner + 借家) * tax_金額
