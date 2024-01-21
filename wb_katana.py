#!/usr/bin/env python

import tomllib

def show_diagram():
    import matplotlib.pyplot as plt

    margin = 20

    color_off_limits = '0.8'
    color_valid_area = 'white'

    kg_min = 560
    kg_max = 730

    arms = [ .250, .270, .290, .310, .330, .350, .370, .390 ]

    moment_min = kg_min * arms[0]
    moment_max = kg_max * arms[-1]

    fig, (diagram, info) = plt.subplots(2, 1, figsize=(5,7), height_ratios=(1,1) )

    info.axis("off")
    info.text(0, 0, '''Aap
Noot
Mies
    Wim
Zus     Jet
'''
)

    # Plot same arm lines as in POH
    #
    for arm in arms:
        diagram.plot(
            [ kg_min * arm, kg_max * arm],
            [ kg_min, kg_max ],
            color='0.6',
            linewidth=0.5
            #'linestyle': ':',
        )

        diagram.text(
             kg_max * arm + 2, kg_max + 3,
             '{} mm'.format(int(1000 * arm)),
             fontsize=6,
             rotation=60,
             rotation_mode='anchor',
             transform_rotates_text=True
        )

    # Fill off limits COG area with grey
    #
    diagram.fill(
        [
            moment_min - margin,
            moment_max + margin, 
            moment_max + margin,
            moment_min - margin,
        ],

        [
            kg_min - margin,
            kg_min - margin,
            kg_max + 2 * margin,   # extra space for arm line labels
            kg_max + 2 * margin,   # idem
        ],

        color='0.8',
    )

    # Fill permissible COG area white
    #
    diagram.fill(
        [
            moment_min,
            kg_min * arms[-1], 
            moment_max,
            kg_max * arms[0],
        ],

        [
            kg_min,
            kg_min,
            kg_max,
            kg_max,
        ],

        color=color_valid_area,
    )

    # Black lines around permissible COG area
    #
    diagram.plot( [ moment_min, kg_min * arms[-1] ], [ kg_min, kg_min], color='black' )
    diagram.plot( [ moment_min, kg_max * arms[0] ], [ kg_min, kg_max], color='black' )
    diagram.plot( [ kg_max * arms[0], moment_max ], [ kg_max, kg_max ], color='black' )
    diagram.plot( [ kg_min * arms[-1], moment_max ], [ kg_min, kg_max], color='black' )

    diagram.set_xlabel('Moment (kg.m)')
    diagram.set_ylabel('Weight (kg)')

    plt.show()

def load_profile(path):
    with open(path, 'rb') as fd:
        profile = tomllib.load(fd)
    return profile


def calc(pob, baggage, fuel=0.0):
    weight = pob + baggage + fuel
    moment = 0.0
    moment += 0.143 * pob
    moment += 0.824 * (baggage + fuel)  # same arm
    return weight, moment


if __name__ == "__main__":
    profile = load_profile('d-ecpu.toml')
    print(profile)

    empty_weight = profile['empty_weight']
    empty_moment = profile['empty_moment']

    pilot_name = profile.get('pilot_name', 'Pilot')
    pax_name = profile.get('pax_name', 'Pax')

    pilot_weight = profile['pilot_weight']
    pax_weight = profile['pax_weight']
    pob_weight = pilot_weight + pax_weight

    bagage_weight = profile['baggage']
    zero_fuel_weight, zero_fuel_moment = calc(pob_weight, bagage_weight)

    fuel_liters = profile['fuel']
    fuel_weight = fuel_liters * 0.72
    takeoff_fuel_weight, takeoff_fuel_moment = calc(pob_weight, bagage_weight)

    show_diagram()
