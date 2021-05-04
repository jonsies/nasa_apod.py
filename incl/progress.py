def printProgress(progress,length=10,
        prefix="",suffix="",sbar="[",ebar="]",
        mbar="-",fill="█"):

    if progress == 0:
        fill_len = 0
    else:
        fill_len = int(length/(100/progress))
    remain_bar = (length - fill_len) * mbar
    fill_bar = fill*fill_len

    print("\r{}{}{}{}{} {:3d}%{}".format(prefix,sbar,
        fill_bar,remain_bar,ebar,progress,suffix),end="")
    if progress == 100:
        print("")
