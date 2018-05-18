import scrapy

class CrazyItem(scrapy.Item):
    name = "crazy-item"

    house_id = scrapy.Field()
    postcode = scrapy.Field()
    latitude = scrapy.Field()
    longitude = scrapy.Field()
    property_type = scrapy.Field()
    num_of_bathrooms = scrapy.Field()
    num_of_bedrooms = scrapy.Field()
    num_of_receptions = scrapy.Field()
    description = scrapy.Field()
    price = scrapy.Field()

    # Zoopla users rating
    # scores
    overall_rating = scrapy.Field()

    # [community_and_safety, entertainment_and_nightlife,
    # parks_and_recreation, restaurants_and_shopping,
    # schools_and_public_service, transport_and_travel]
    cs_rating = scrapy.Field()
    en_rating = scrapy.Field()
    pr_rating = scrapy.Field()
    rs_rating = scrapy.Field()
    sp_rating = scrapy.Field()
    tt_rating = scrapy.Field()


    # [age_0_14, age_15_24, age_25_34, age_35_44,
    # age_45_54, age_55_64, age_65_plus]
    # Scotland may differ
    demographic = scrapy.Field()

    # Education
    # [level_4_plus_english_and_math, level_5_plus_english_and_math,
    # achieving_a_to_c, achieving_a_to_g, a_level_passes]
    education = scrapy.Field()

    # Crime
    # [crime_physical_violence, crime_robbery,
    # crime_domestic_burglary, crime_theft_of_vehicle,
    # crime_theft_from_vehicle]
    crime = scrapy.Field()

    #Counciltax
    # [tax_band_a, tax_band_b, tax_band_c,
    # tax_band_d, tax_band_e, tax_band_f,
    # tax_band_g, tax_band_h]
    counciltax = scrapy.Field()

    # Housing
    # [owned, owned_with_mortgage, privately_rented,
    # socially_rented, shared_ownership]
    housing = scrapy.Field()

    # Employment
    # [higher_managerial, professional, office_worker,
    # bussiness_owner, supervisory_tech, unemployed,
    # student]
    employment = scrapy.Field()

    # Family
    # [couple_without_children, couple_with_children
    # single_parent_family, pensioner, student
    # single_individual, other_household_structure]
    family = scrapy.Field()

    # Interest
    # [cinema, diy, eating_out, sports, football_supporter,
    # gardening, music, foreign_travel]
    interests = scrapy.Field()

    # Newspaper
    # [daily_express, daily_mail, daily_mirror,
    # daily_telegraph, the_guardian, the_independent
    # the_sun, the_times]
    newspapers = scrapy.Field()
