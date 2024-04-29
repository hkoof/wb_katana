#!/usr/bin/env python

import sys
import datetime
import tomllib

max_fuel_liters = 74
max_fuel_mass = 0.72 * max_fuel_liters

kg_min = 560
kg_max = 730

arms = [ .250, .270, .290, .310, .330, .350, .370, .390 ]

moment_min = kg_min * arms[0]
moment_max = kg_max * arms[-1]

def start_diagram():
    import matplotlib.pyplot as plt

    margin = 14

    color_off_limits = '0.8'
    color_valid_area = 'white'

    fig, (diagram, info) = plt.subplots(2, 1, figsize=(7,7), height_ratios=(3,2) )
    info.axis("off")

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

    return plt, diagram, info


def load_profile(path):
    with open(path, 'rb') as fd:
        profile = tomllib.load(fd)
    return profile


def calc(empty_weight, empty_moment, pob, baggage, fuel=0.0):
    weight = empty_weight + pob + baggage + fuel
    moment = empty_moment
    moment += 0.143 * pob
    moment += 0.824 * (baggage + fuel)  # same arm
    return weight, moment


def is_within_limits(weight, moment):
    if weight < float(kg_min):
        return False
    if weight > float(kg_max):
        return False

    arm = moment / weight 
    if arm < arms[0]:
        return False
    if arm > arms[-1]:
        return False

    return True


if __name__ == "__main__":
    if len(sys.argv) == 2:
        profile_filename = sys.argv[1]
    else:
        profile_filename = 'example.toml'
    profile = load_profile(profile_filename)

    title = profile['title']
    callsign = profile['callsign']
    date = profile.get('date')
    if not date:
        today = datetime.date.today()
        date = f'{today.year}-{today.month}-{today.day}'

    empty_weight = profile['empty_weight']
    empty_moment = profile['empty_moment']

    pilot_name = profile.get('pilot_name', 'Pilot')
    pax_name = profile.get('pax_name', 'Pax')

    pilot_weight = profile['pilot_weight']
    pax_weight = profile['pax_weight']
    pob_weight = pilot_weight + pax_weight

    bagage_weight = profile['baggage']
    zero_fuel_weight, zero_fuel_moment = calc(empty_weight, empty_moment, pob_weight, bagage_weight)

    fuel_liters = profile['fuel']
    fuel_weight = fuel_liters * 0.72
    takeoff_weight, takeoff_moment = calc(empty_weight, empty_moment, pob_weight, bagage_weight, fuel_weight)

    plt, diagram, info = start_diagram()

    zero_fuel_OK = is_within_limits(zero_fuel_weight, zero_fuel_moment)
    takeoff_fuel_OK = is_within_limits(takeoff_weight, takeoff_moment)
    if zero_fuel_OK and takeoff_fuel_OK:
        plot_color = 'green'
    else:
        plot_color = 'red'

    diagram.plot(
        [ zero_fuel_moment, takeoff_moment ],
        [ zero_fuel_weight, takeoff_weight ],
        color=plot_color,
        marker='.',
    ) 

    txt = f'''
{title}    {callsign}    {date}

Pilot, {pilot_name} (kg): {pilot_weight}
Pax, {pax_name} (kg): {pax_weight}
Baggage (kg): {bagage_weight}
Fuel: {fuel_liters} litres, {fuel_weight} kg
'''
    info.text(0, 0, txt)
    plt.show()
