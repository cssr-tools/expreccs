""""
Script to plot the top surface for the reference, regionla, and site reservoirs.
"""

from datetime import timedelta
import argparse
import numpy as np
import matplotlib.pyplot as plt
from mpl_toolkits.axes_grid1 import make_axes_locatable
from ecl.summary import EclSum
from ecl.eclfile import EclFile
from ecl.grid import EclGrid


def main():
    """Postprocessing"""
    parser = argparse.ArgumentParser(description="Main script to plot the results")
    parser.add_argument(
        "-t",
        "--time",
        default=0.0,
        help="The workflow time.",
    )
    parser.add_argument(
        "-p",
        "--path",
        default="/Users/dmar/Github/expreccs/examples/output/output/",
        help="The path to the opm simulations.",
    )
    cmdargs = vars(parser.parse_known_args()[0])
    dic = {"path": cmdargs["path"].strip()}
    dic["rhog_ref"] = 1.86843  # CO2 reference density
    dic["sat_thr"] = 1e-3  # Threshold for the gas saturation
    dic["quantity"] = ["mass", "saturation", "pressure"]
    dic["units"] = ["kg", "-", "bar"]
    for reservoir in ["reference", "regional", "site", "site_openboundaries"]:
        case = dic["path"] + f"{reservoir.upper()}"
        dic[f"{reservoir}_rst"] = EclFile(case + ".UNRST")
        dic[f"{reservoir}_ini"] = EclFile(case + ".INIT")
        dic[f"{reservoir}_grid"] = EclGrid(case + ".EGRID")
        dic[f"{reservoir}_smsp"] = EclSum(case + ".SMSPEC")
        dic[f"{reservoir}_saturation"] = dic[f"{reservoir}_rst"].iget_kw("SGAS")
        dic[f"{reservoir}_pressure"] = dic[f"{reservoir}_rst"].iget_kw("PRESSURE")
        dic[f"{reservoir}_phiv"] = dic[f"{reservoir}_ini"].iget_kw("PORV")[0]
        dic[f"{reservoir}_density"] = dic[f"{reservoir}_rst"].iget_kw("GAS_DEN")
        dic[f"{reservoir}_fipn"] = np.array(dic[f"{reservoir}_ini"].iget_kw("FIPNUM"))[
            0
        ]
        dic[f"{reservoir}_indicator_array"] = []
        for quantity in dic["quantity"]:
            dic[f"{reservoir}_{quantity}_array"] = []
            for i in range(dic[f"{reservoir}_rst"].num_report_steps()):
                if quantity == "mass":
                    dic[f"{reservoir}_{quantity}_array"].append(
                        np.array(
                            dic[f"{reservoir}_saturation"][i]
                            * dic[f"{reservoir}_density"][i]
                            * dic[f"{reservoir}_phiv"]
                        )
                    )
                elif quantity == "saturation":
                    dic[f"{reservoir}_indicator_array"].append(
                        np.array(dic[f"{reservoir}_saturation"][i]) > dic["sat_thr"]
                    )
                    dic[f"{reservoir}_{quantity}_array"].append(
                        np.array(dic[f"{reservoir}_saturation"][i])
                    )
                else:
                    dic[f"{reservoir}_{quantity}_array"].append(
                        np.array(dic[f"{reservoir}_{quantity}"][i])
                    )
    final_time_maps(dic)
    over_time_distance(dic)
    over_time_max_difference(dic)
    difference(dic)
    print(f"Total simulation time: {timedelta(seconds=float(cmdargs['time']))}")


def difference(dic):
    """
    Function to plot the difference between the reference and site simulations
    in the last time step

    Args:
        dic (dict): Global dictionary with required parameters

    Returns:
        dic (dict): Global dictionary with new added parameters

    """
    for reservoir in ["site", "site_openboundaries"]:
        for j, quantity in enumerate(dic["quantity"]):
            dic[f"{reservoir}_difference_{quantity}"] = (
                dic[f"reference_{quantity}_array"][-1][dic["reference_fipn"] == 1]
                - dic[f"{reservoir}_{quantity}_array"][-1]
            )
            if quantity == "mass":
                dic[f"{reservoir}_difference_{quantity}"] /= dic[
                    f"{reservoir}_mass_array"
                ][-1].sum()
            dic[f"{reservoir}_difference_{quantity}_plot"] = np.zeros(
                [len(dic["site_ymy"]) - 1, len(dic["site_xmx"]) - 1]
            )
            for i in np.arange(0, len(dic["site_ymy"]) - 1):
                dic[f"{reservoir}_difference_{quantity}_plot"][i, :] = dic[
                    f"{reservoir}_difference_{quantity}"
                ][i * (len(dic["site_xmx"]) - 1) : (i + 1) * (len(dic["site_xmx"]) - 1)]
            fig, axis = plt.subplots()
            imag = axis.pcolormesh(
                dic[f"{reservoir}_xcor"],
                dic[f"{reservoir}_ycor"],
                dic[f"{reservoir}_difference_{quantity}_plot"],
                shading="flat",
                cmap="jet",
            )
            axis.axis(
                [
                    dic[f"{reservoir}_xcor"].min(),
                    dic[f"{reservoir}_xcor"].max(),
                    dic[f"{reservoir}_ycor"].min(),
                    dic[f"{reservoir}_ycor"].max(),
                ]
            )
            axis.axis("scaled")
            axis.set_xlabel("[m]")
            axis.set_ylabel("[m]")
            axis.set_title(
                f"sum abs({quantity}Reference-{quantity}Site)"
                + f"={abs(dic[f'{reservoir}_difference_{quantity}_plot']).sum():.2E}"
                + f" [{dic['units'][j]}]"
            )
            divider = make_axes_locatable(axis)
            cax = divider.append_axes("right", size="5%", pad=1e-3)
            vect = np.linspace(
                dic[f"{reservoir}_difference_{quantity}_plot"].min(),
                dic[f"{reservoir}_difference_{quantity}_plot"].max(),
                5,
                endpoint=True,
            )
            fig.colorbar(
                imag,
                cax=cax,
                orientation="vertical",
                ticks=vect,
                format=lambda x, _: f"{x:.3f}",
            )
            imag.set_clim(
                dic[f"{reservoir}_difference_{quantity}_plot"].min(),
                dic[f"{reservoir}_difference_{quantity}_plot"].max(),
            )
            fig.savefig(f"{reservoir}_difference_{quantity}.png", bbox_inches="tight")
            plt.close()


def over_time_distance(dic):
    """
    Function to plot the distance from the closest saturation cell to the site border

    Args:
        dic (dict): Global dictionary with required parameters

    """
    dic["fig"], dic["axis"] = [], []
    color = ["b", "g", "r"]
    linestyle = ["--", "-.", ":"]
    fig, axis = plt.subplots()
    dic["fig"].append(fig)
    dic["axis"].append(axis)
    dic["boxi"] = dic["site_grid"].getNodePos(0, 0, 0)
    dic["boxf"] = dic["site_grid"].getNodePos(
        dic["site_grid"].getNX(),
        dic["site_grid"].getNY(),
        dic["site_grid"].getNZ(),
    )
    dic["dx_half_size"] = (
        0.5 * (dic["boxf"][0] - dic["boxi"][0]) / (dic["site_grid"].getNX())
    )
    dic["dy_half_size"] = (
        0.5 * (dic["boxf"][1] - dic["boxi"][1]) / (dic["site_grid"].getNY())
    )
    for j, reservoir in enumerate(["site", "site_openboundaries", "reference"]):
        dic[f"{reservoir}_indicator_plot"] = []
        for quantity in dic["quantity"][1:]:
            dic[f"{reservoir}_difference_{quantity}"] = []
        for nrst in range(dic[f"{reservoir}_rst"].num_report_steps()):
            if reservoir == "reference":
                indx = [
                    dic[f"{reservoir}_indicator_array"][nrst][k]
                    and dic["reference_fipn"][k] == 1
                    for k in range(len(dic["reference_fipn"]))
                ]
                points = dic[f"{reservoir}_grid"].export_position(
                    dic[f"{reservoir}_grid"].export_index()[indx]
                )
            else:
                points = dic[f"{reservoir}_grid"].export_position(
                    dic[f"{reservoir}_grid"].export_index()[
                        dic[f"{reservoir}_indicator_array"][nrst]
                    ]
                )
            if points.size > 0:
                closest_distance = np.zeros(4)
                for i, border in enumerate(
                    [
                        dic["boxi"][0] + dic["dx_half_size"],
                        dic["boxf"][0] - dic["dx_half_size"],
                    ]
                ):
                    closest_distance[i] = min(
                        np.array([abs(row[0] - border) for row in points])
                    )
                for i, border in enumerate(
                    [
                        (dic["boxi"][1] + dic["dy_half_size"]),
                        (dic["boxf"][1] - dic["dy_half_size"]),
                    ]
                ):
                    closest_distance[i + 2] = min(
                        np.array([abs(row[1] - border) for row in points])
                    )
                dic[f"{reservoir}_indicator_plot"].append(closest_distance.min())
            else:
                dic[f"{reservoir}_indicator_plot"].append(
                    (dic["boxf"][0] - dic["boxi"][0]) / 2.0
                )
        dic["axis"][-1].plot(
            dic[f"{reservoir}_rst"].dates,
            dic[f"{reservoir}_indicator_plot"],
            color=color[j],
            linestyle=linestyle[j],
            label=f"{reservoir}",
        )
    dic["axis"][-1].set_title(
        "Minimum " + r"CO$_2$" + f' distance to the borders (sat thr={dic["sat_thr"]})'
    )
    dic["axis"][-1].set_ylabel("Distance [m]", fontsize=12)
    dic["axis"][-1].set_xlabel("Time", fontsize=12)
    dic["axis"][-1].legend()
    dic["axis"][-1].xaxis.set_tick_params(size=6, rotation=45)
    dic["fig"][-1].savefig("distance_from_border.png", bbox_inches="tight")
    plt.close()


def over_time_max_difference(dic):
    """
    Function to plot the the max difference between pressure and saturation.

    Args:
        dic (dict): Global dictionary with required parameters

    """
    dic["fig"], dic["axis"] = [], []
    color = ["b", "g", "r"]
    linestyle = [":", "--", "-."]
    for quantity in dic["quantity"][1:]:
        fig, axis = plt.subplots()
        dic["fig"].append(fig)
        dic["axis"].append(axis)
        dic[f"reference_maximum_{quantity}"] = []
    for j, reservoir in enumerate(["site", "site_openboundaries"]):
        for quantity in dic["quantity"][1:]:
            dic[f"{reservoir}_difference_{quantity}"] = []
            dic[f"{reservoir}_maximum_{quantity}"] = []
            fig, axis = plt.subplots()
            dic["fig"].append(fig)
            dic["axis"].append(axis)
        for nrst in range(dic[f"{reservoir}_rst"].num_report_steps()):
            for quantity in dic["quantity"][1:]:
                dic[f"{reservoir}_difference_{quantity}"].append(
                    max(
                        abs(
                            np.array(dic[f"reference_{quantity}_array"][nrst])[
                                dic["reference_fipn"] == 1
                            ]
                            - dic[f"{reservoir}_{quantity}_array"][nrst]
                        )
                    )
                )
                dic[f"{reservoir}_maximum_{quantity}"].append(
                    max(dic[f"{reservoir}_{quantity}_array"][nrst])
                )
                if reservoir == "site":
                    dic[f"reference_maximum_{quantity}"].append(
                        max(
                            dic[f"reference_{quantity}_array"][nrst][
                                dic["reference_fipn"] == 1
                            ]
                        )
                    )
        for i, quantity in enumerate(dic["quantity"][1:]):
            label = (
                f"{reservoir} (max {quantity} of "
                + f"{np.array(dic[f'{reservoir}_maximum_{quantity}']).max():.2E}"
                + f"[{dic['units'][i+1]}])"
            )
            dic["axis"][i].plot(
                dic[f"{reservoir}_rst"].dates,
                dic[f"{reservoir}_difference_{quantity}"],
                color=color[j],
                linestyle=linestyle[j],
                label=label,
            )
    for i, quantity in enumerate(dic["quantity"][1:]):
        dic["axis"][i].set_title(
            f"Maximum {quantity} difference (w.r.t. reference, max {quantity} of "
            + f"{np.array(dic[f'reference_maximum_{quantity}']).max():.2E} [{dic['units'][i+1]}]))"
        )
        dic["axis"][i].set_ylabel(f"Difference [{dic['units'][i+1]}]", fontsize=12)
        dic["axis"][i].set_xlabel("Time", fontsize=12)
        dic["axis"][i].legend()
        dic["axis"][i].xaxis.set_tick_params(size=6, rotation=45)
        dic["fig"][i].savefig(
            f"maximum_{quantity}_difference_over_time.png", bbox_inches="tight"
        )
        plt.close()


def final_time_maps(dic):
    """
    Function to plot the 2D maps for the different reservoirs and quantities

    Args:
        dic (dict): Global dictionary with required parameters

    """
    for reservoir in ["reference", "regional", "site", "site_openboundaries"]:
        dic["boxi"] = dic[f"{reservoir}_grid"].getNodePos(0, 0, 0)
        dic["boxf"] = dic[f"{reservoir}_grid"].getNodePos(
            dic[f"{reservoir}_grid"].getNX(),
            dic[f"{reservoir}_grid"].getNY(),
            dic[f"{reservoir}_grid"].getNZ(),
        )
        dic[f"{reservoir}_xmx"] = np.linspace(
            dic["boxi"][0], dic["boxf"][0], dic[f"{reservoir}_grid"].get_nx() + 1
        )
        dic[f"{reservoir}_ymy"] = np.linspace(
            dic["boxi"][1], dic["boxf"][1], dic[f"{reservoir}_grid"].get_ny() + 1
        )
        dic[f"{reservoir}_xcor"], dic[f"{reservoir}_ycor"] = np.meshgrid(
            dic[f"{reservoir}_xmx"], dic[f"{reservoir}_ymy"][::-1]
        )
        for quantity in dic["quantity"]:
            dic[f"{reservoir}_{quantity}_plot"] = np.zeros(
                [len(dic[f"{reservoir}_ymy"]) - 1, len(dic[f"{reservoir}_xmx"]) - 1]
            )
            if quantity == "mass":
                for i in np.arange(0, len(dic[f"{reservoir}_ymy"]) - 1):
                    dic[f"{reservoir}_{quantity}_plot"][-1 - i, :] = (
                        dic[f"{reservoir}_{quantity}_array"][-1][
                            i
                            * (len(dic[f"{reservoir}_xmx"]) - 1) : (i + 1)
                            * (len(dic[f"{reservoir}_xmx"]) - 1)
                        ]
                        / dic[f"{reservoir}_mass_array"][-1].sum()
                    )
            else:
                for i in np.arange(0, len(dic[f"{reservoir}_ymy"]) - 1):
                    dic[f"{reservoir}_{quantity}_plot"][-1 - i, :] = dic[
                        f"{reservoir}_{quantity}_array"
                    ][-1][
                        i
                        * (len(dic[f"{reservoir}_xmx"]) - 1) : (i + 1)
                        * (len(dic[f"{reservoir}_xmx"]) - 1)
                    ]
            fig, axis = plt.subplots()
            if quantity == "mass":
                imag = axis.pcolormesh(
                    dic[f"{reservoir}_xcor"],
                    dic[f"{reservoir}_ycor"],
                    dic[f"{reservoir}_{quantity}_plot"],
                    shading="flat",
                    cmap="jet",
                )
                axis.set_title(
                    f"normalized {quantity} (Total mass: "
                    + f"{dic[f'{reservoir}_mass_array'][-1].sum() : .2E} [kg])"
                )
            elif quantity == "pressure":
                imag = axis.pcolormesh(
                    dic[f"{reservoir}_xcor"],
                    dic[f"{reservoir}_ycor"],
                    dic[f"{reservoir}_{quantity}_plot"],
                    shading="flat",
                    cmap="jet",
                )
                axis.set_title(f"{quantity} [bar]")
            else:
                imag = axis.pcolormesh(
                    dic[f"{reservoir}_xcor"],
                    dic[f"{reservoir}_ycor"],
                    dic[f"{reservoir}_{quantity}_plot"],
                    shading="flat",
                    cmap="jet",
                )
                axis.set_title(f"{quantity} [-]")
            axis.axis("scaled")
            axis.set_xlabel("[m]")
            axis.set_ylabel("[m]")
            divider = make_axes_locatable(axis)
            cax = divider.append_axes("right", size="5%", pad=0.05)
            vect = np.linspace(
                dic[f"{reservoir}_{quantity}_plot"].min(),
                dic[f"{reservoir}_{quantity}_plot"].max(),
                5,
                endpoint=True,
            )
            fig.colorbar(
                imag,
                cax=cax,
                orientation="vertical",
                ticks=vect,
                format=lambda x, _: f"{x:.2f}",
            )
            imag.set_clim(
                dic[f"{reservoir}_{quantity}_plot"].min(),
                dic[f"{reservoir}_{quantity}_plot"].max(),
            )
            fig.savefig(f"{reservoir}_{quantity}.png", bbox_inches="tight")
            plt.close()

    return dic


if __name__ == "__main__":
    main()
