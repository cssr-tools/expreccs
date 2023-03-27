""""
Script to plot the top surface for a CO2 model
"""

from datetime import timedelta
import numpy as np
import matplotlib.pyplot as plt
from mpl_toolkits.axes_grid1 import make_axes_locatable
from ecl.summary import EclSum
from ecl.eclfile import EclFile
from ecl.grid import EclGrid


def main():
    """Postprocessing"""
    path = "${dic["exe"]}/${dic["fol"]}/output/"
    dic = {"xcor": [], "ycor": []}
    dic["xmx"] = np.linspace(0, ${dic["site_dims"][0]}, ${dic["site_noCells"][0]} + 1)
    dic["ymy"] = np.linspace(0, ${dic["site_dims"][1]}, ${dic["site_noCells"][0]} + 1)
    dic["xcor"], dic["ycor"] = np.meshgrid(dic["xmx"], dic["ymy"][::-1])
    dic["saturation"] = np.zeros([len(dic["xmx"]) - 1, len(dic["ymy"]) - 1])
    dic["pressure"] = np.zeros([len(dic["xmx"]) - 1, len(dic["ymy"]) - 1])
    dic["mass"] = np.zeros([len(dic["xmx"]) - 1, len(dic["ymy"]) - 1])
    case = path + "SITE"
    dic["rst"] = EclFile(case + ".UNRST")
    dic["ini"] = EclFile(case + ".INIT")
    dic["grid"] = EclGrid(case + ".EGRID")
    dic["smsp"] = EclSum(case + ".SMSPEC")
    dic["sgas"] = dic["rst"].iget_kw("SGAS")
    dic["pres"] = dic["rst"].iget_kw("PRESSURE")
    dic["phiv"] = dic["ini"].iget_kw("PORV")
    dic["rhog"] = dic["rst"].iget_kw("GAS_DEN")
    dic["rhog_ref"] = 1.86843

    m_m = dic["sgas"][-1] * dic["rhog"][-1] * dic["phiv"][0]
    p_p = dic["pres"][-1]
    s_s = dic["sgas"][-1]

    for i in np.arange(0, len(dic["ymy"]) - 1):
        dic["saturation"][i, :] = s_s[
            i * (len(dic["xmx"]) - 1) : (i + 1) * (len(dic["xmx"]) - 1)
        ]
        dic["mass"][i, :] = m_m[
            i * (len(dic["xmx"]) - 1) : (i + 1) * (len(dic["xmx"]) - 1)
        ]
        dic["pressure"][i, :] = p_p[
            i * (len(dic["xmx"]) - 1) : (i + 1) * (len(dic["xmx"]) - 1)
        ]
    totalMass = sum(m_m)
    dic["mass"] /= totalMass

    for names in ["saturation", "mass", "pressure"]:
        fig, axis = plt.subplots()
        imag = axis.pcolormesh(
            dic["xcor"], dic["ycor"], dic[names], shading="flat", cmap="jet"
        )
        axis.axis("scaled")
        if names == "mass":
            axis.set_title(f"normalized {names} (Total mass: {sum(m_m) : .2E} [kg])")
        elif names == "pressure":
            axis.set_title(f"{names} [bar]")
        else:
            axis.set_title(f"{names}")
        divider = make_axes_locatable(axis)
        cax = divider.append_axes("right", size="5%", pad=0.05)
        vect = np.linspace(dic[names].min(), dic[names].max(), 5, endpoint=True)
        fig.colorbar(
            imag,
            cax=cax,
            orientation="vertical",
            ticks=vect,
            format=lambda x, _: f"{x:.2f}",
        )
        imag.set_clim(dic[names].min(), dic[names].max())
        fig.savefig(f"{names}.png", bbox_inches="tight")

    print(f"Total simulation time: {timedelta(seconds=${'{0:.2f}'.format(time)})}")

    case = path + 'REFERENCE'
    dic["rst"] = EclFile(case + ".UNRST")
    dic["ini"] = EclFile(case + ".INIT")
    dic["grid"] = EclGrid(case + ".EGRID")
    dic["smsp"] = EclSum(case + ".SMSPEC")
    dic["sgas"] = dic["rst"].iget_kw("SGAS")
    dic["pres"] = dic["rst"].iget_kw("PRESSURE")
    dic["phiv"] = dic["ini"].iget_kw("PORV")
    dic["fipn"] = dic["ini"].iget_kw("FIPNUM")
    dic["rhog"] = dic["rst"].iget_kw("GAS_DEN")
    
    inx = 0
    for cell in dic["grid"].cells():
        if dic["fipn"][0][cell.global_index] == 1:
            m_m[inx] -= dic['sgas'][-1][cell.global_index]*dic['rhog'][-1][cell.global_index]*dic["phiv"][0][cell.global_index]
            inx += 1

    for i in np.arange(0, len(dic["ymy"]) - 1):
        dic["mass"][i, :] = m_m[i * (len(dic["xmx"]) - 1) : (i + 1) * (len(dic["xmx"]) - 1)]
    dic["mass"] /= totalMass
    for names in ['mass']:
        fig, ax = plt.subplots()
        imag = ax.pcolormesh(dic['xcor'], dic['ycor'], dic[names], shading="flat", cmap="jet")
        ax.axis([dic['xcor'].min(), dic['xcor'].max(), dic['ycor'].min(), dic['ycor'].max()])
        ax.axis("scaled")
        if names == 'mass':
            ax.set_title(f"sum abs(massSite-massReference) ({abs(dic['mass']).sum() : .2E})")
        else:
            ax.set_title(f"{names}")
        divider = make_axes_locatable(ax)
        cax = divider.append_axes("right", size="5%", pad=1e-3)
        vect = np.linspace(dic[names].min(), dic[names].max(), 5, endpoint=True)
        fig.colorbar(
            imag, cax=cax, orientation="vertical", ticks=vect, format=lambda x, _: f"{x:.3f}"
        )
        imag.set_clim(dic[names].min(), dic[names].max())
        fig.savefig("difference.png", bbox_inches="tight")


if __name__ == "__main__":
    main()
