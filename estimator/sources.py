
UK_INCOMETAX_SOURCE = {
    "title": "HMRC - Income Tax rates and allowances",
    "tax_year": "2026/27",
    "url": "https://www.gov.uk/government/publications/rates-and-allowances-income-tax/income-tax-rates-and-allowances-current-and-past",
}

SWISS_TAX_SOURCE = {
    "title": "Swiss Federal Tax Administration - Tax Calculator",
    "tax_year": "2026",
    "url": "https://swisstaxcalculator.estv.admin.ch/",
}

SWISS_AHV_SOURCE = {
    "title": "Swiss AHV/IV/EO Contributions",
    "tax_year": "2026",
    "url": "https://www.ahv-iv.ch/p/2.01.e",
}

SWISS_ALV_SOURCE = {
    "title": "Swiss Unemployment Insurance",
    "tax_year": "2026",
    "url": "https://www.ahv-iv.ch/p/890.e",
}

UK_SWISS_SOCIAL_SOURCE = {
    "title": "GOV.UK - Social Security for Workers Coming to the UK",
    "url": "https://www.gov.uk/guidance/social-security-contributions-for-workers-coming-to-the-uk-from-the-eea-or-switzerland",
}

UK_HOUSING_SOURCE = {
    "title": "HMRC - Employee Living Accommodation",
    "url": "https://www.gov.uk/guidance/company-provided-living-accommodation-480-chapter-21",
}

UK_RELOCATION_SOURCE = {
    "title": "HMRC - Qualifying Relocation Costs",
    "url": "https://www.gov.uk/expenses-and-benefits-relocation/whats-exempt",
}

UK_TEMP_HOUSING_SOURCE = {
    "title": "HMRC - Relocation Expenses Appendix 7",
    "url": "https://www.gov.uk/guidance/relocation-expenses-480-appendix-7",
}

UK_SECONDMENT_SOURCE = {
    "title": "HMRC - Employees on Secondment to the UK",
    "url": "https://www.gov.uk/hmrc-internal-manuals/employment-income-manual/eim77010",
}

UK_ACCOMMODATION_SOURCE = {
    "title": "HMRC - Accommodation at Temporary Workplaces",
    "url": "https://www.gov.uk/hmrc-internal-manuals/employment-income-manual/eim31836",
}

UK_TEMP_RELOCATION_SOURCE = {
    "title": "HMRC - Temporary Living Accommodation and Relocation Relief",
    "url": "https://www.gov.uk/hmrc-internal-manuals/employment-income-manual/eim03117",
}

UK_RELOCATION_REPORT_SOURCE = {
    "title": "HMRC - Reporting and Paying Tax on Relocation Costs",
    "url": "https://www.gov.uk/expenses-and-benefits-relocation/what-to-report-and-pay",
}

UK_NI_SOURCE = {
    "title": "HMRC - Employer National Insurance Rates and Thresholds",
    "tax_year": "2026/27",
    "url": "https://www.gov.uk/guidance/rates-and-thresholds-for-employers-2026-to-2027",
}


SOURCE_GROUPS = {
    "UK Income Tax": [
        UK_INCOMETAX_SOURCE       
    ],

    "Swiss Tax and Social Security": [
        SWISS_TAX_SOURCE,
        SWISS_AHV_SOURCE,
        SWISS_ALV_SOURCE,
    ],

    "UK National Insurance and Coverage": [
        UK_NI_SOURCE,
        UK_SWISS_SOCIAL_SOURCE,
    ],

    "Accommodation and Secondment": [
        UK_HOUSING_SOURCE,
        UK_ACCOMMODATION_SOURCE,
        UK_SECONDMENT_SOURCE,
    ],

    "Relocation Expenses and Exemptions": [
        UK_RELOCATION_SOURCE,
        UK_TEMP_HOUSING_SOURCE,
        UK_TEMP_RELOCATION_SOURCE,
        UK_RELOCATION_REPORT_SOURCE,
    ],
}

SECTION_SOURCES = {
    "year1_tax": [
        UK_INCOMETAX_SOURCE,
    ],

    "year2_tax": [
        UK_INCOMETAX_SOURCE,
    ],

    "swiss_tax": [
        SWISS_TAX_SOURCE,
    ],

    "swiss_social": [
        SWISS_AHV_SOURCE,
        SWISS_ALV_SOURCE,
    ],

    "uk_ni": [
        UK_NI_SOURCE,
        UK_SWISS_SOCIAL_SOURCE,
    ],

    "accommodation": [
        UK_HOUSING_SOURCE,
        UK_ACCOMMODATION_SOURCE,
        UK_SECONDMENT_SOURCE,
    ],

    "relocation": [
        UK_RELOCATION_SOURCE,
        UK_TEMP_HOUSING_SOURCE,
        UK_TEMP_RELOCATION_SOURCE,
        UK_RELOCATION_REPORT_SOURCE,
    ],

    "coverage": [
        UK_SWISS_SOCIAL_SOURCE,
    ],
}
