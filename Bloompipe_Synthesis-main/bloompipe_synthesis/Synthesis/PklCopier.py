# ===== Inits + Definitions =========================
import os
import shutil


# ===== Global-Variables =========================

# ===== Methods =========================

# Downloads the provided style onto the GPU Server
def getStyle(styleName):
    # Checks if .pkl file already exists
    if not os.path.exists("./" + str(styleName) + ".pkl"):
        print("Copying Style " + str(styleName) + ".pkl")

        shutil.copyfile(
            "./meta/pkls/" + str(styleName) + ".pkl",
            "./" + str(styleName) + ".pkl"
        )
