#!/usr/bin/env python

""""
Script to write the saturation functions
"""

import numpy as np


def krwe(sew, krw):
    # Wetting relative permeability
    return ${dic['krwf'].strip()}


def krce(sew, krc):
    # CO2 relative permeability
    return ${dic['krcf'].strip()}


def pcwce(sew, pec):
    # Capillary pressure
    return ${dic['pcwcf'].strip()}


def safu_evaluation():
    # Saturation function assignation

    # Properties: srw, 1 - sg, krw, krg, pe
    safu = [[0.0] * 5 for _ in range(${len(dic['safu'])})]
    % for i, _ in enumerate(dic['safu']):
    % for j, _ in enumerate(dic['safu'][i]):
    safu[${i}][${j}] = ${dic['safu'][i][j]}
    % endfor
    % endfor

    with open(
        "${dic['exe']}/${dic['fol']}/preprocessing/TABLES.INC",
        "w",
        encoding="utf8",
    ) as file:
        file.write("SGOF\n")
        for _, para in enumerate(safu):
            sco2 = np.linspace(1 - para[1], 1 - para[0], 19)
            sew = abs((1 - sco2 - para[0]) / (para[1] - para[0]))
            if sco2[0] > 0:
                file.write(
                    f"0.00000 {krce(sew[0], para[3]) :E}"
                    f" {abs(krwe(sew[0], para[2])) :E}"
                    f" {pcwce(sew[0], para[4]) : E} \n"
                )
            for i, value in enumerate(sco2[:-1]):
                file.write(
                    f"{value:E} {krce(sew[i], para[3]) :E}"
                    f" {krwe(sew[i], para[2]) :E}"
                    f" {pcwce(max(sew[i], 1e-2), para[4]) : E} \n"
                )
            file.write(
                    f"{sco2[-1]:E} {krce(sew[-1], para[3]) :E}"
                    f" {krwe(0., para[2]) :E}"
                    f" {pcwce(max(sew[-1], 1e-2), para[4]) : E} \n"
                )
            file.write("/\n")


if __name__ == "__main__":
    safu_evaluation()
