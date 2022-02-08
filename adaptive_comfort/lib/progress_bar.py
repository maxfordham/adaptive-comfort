import math as m

ANIMATIONSTRING = "◢◣◤◥"
ANIMATIONSTRING = "/-\|"
ANIMATIONSTRING = "⡀⡁⡂⡃⡄⡅⡆⡇⡈⡉⡊⡋⡌⡍⡎⡏⡐⡑⡒⡓⡔⡕⡖⡗⡘⡙⡚⡛⡜⡝⡞⡟⡠⡡⡢⡣⡤⡥⡦⡧⡨⡩⡪⡫⡬⡭⡮⡯⡰⡱⡲⡳⡴⡵⡶⡷⡸⡹⡺⡻⡼⡽⡾⡿⢀⢁⢂⢃⢄⢅⢆⢇⢈⢉⢊⢋⢌⢍⢎⢏⢐⢑⢒⢓⢔⢕⢖⢗⢘⢙⢚⢛⢜⢝⢞⢟⢠⢡⢢⢣⢤⢥⢦⢧⢨⢩⢪⢫⢬⢭⢮⢯⢰⢱⢲⢳⢴⢵⢶⢷⢸⢹⢺⢻⢼⢽⢾⢿⣀⣁⣂⣃⣄⣅⣆⣇⣈⣉⣊⣋⣌⣍⣎⣏⣐⣑⣒⣓⣔⣕⣖⣗⣘⣙⣚⣛⣜⣝⣞⣟⣠⣡⣢⣣⣤⣥⣦⣧⣨⣩⣪⣫⣬⣭⣮⣯⣰⣱⣲⣳⣴⣵⣶⣷⣸⣹⣺⣻⣼⣽⣾"
ANIMATIONSTRING = "⠁⠂⠄⡀⢀⠠⠐⠈"
DONECHARACTER = "⣿" #■ ⣿

def progress_bar(i, count, message="", show_progress=True, show_perc=True):
    '''
    Prints a continuously updating progress bar. Call in each iteration loop. example output:
    ########-. 162/200 (81.0%) : hdr_C43LONGTEST_lum5008.hdr
    Args:
        i (int): number in progress
        count (int): total number in progress
        message (str): string to be added onto end of message
        show_progress (bool): show a count of the progress
        show_perc (bool): show the percentage completion

    Returns:
        The string that was printed.
    '''
    if count > 0:
        perc = ((i+1)/count)*100
        done = m.floor(perc/10)
    else:
        perc = -1
        done = i
        
    output = "   ["
    output += done*DONECHARACTER
    if done < 10:
        output += ANIMATIONSTRING[i%len(ANIMATIONSTRING)]
    output += (10-done-1)*" "
    output += "]"

    if show_progress:
        output += " {0}/{1}".format(i+1, count)
    if show_perc:
        output += " ({0:.1f}%)".format(perc)
    if message:
        output += " : {0}".format(message)
    if perc<100:
        print(output, end="\r")
    else:
        print(output)

    return output

if __name__ == "__main__":
    import time
    for i in range(200):
        time.sleep(0.1)
        progress_bar(i, 200, "loading")
