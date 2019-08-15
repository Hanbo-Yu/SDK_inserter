# encoding:utf-8
import os, shutil
import xml.dom.minidom
from xml.dom.minidom import parse

scriptPath = os.getcwd() + "/"
apkPath = scriptPath + "/apk/"
sdk = scriptPath + "/dragonmobile"


def pkgfetcher():
    manifest = "AndroidManifest.xml"
    xmlPath = scriptPath + app_name
    manifestFilePath = os.path.join(xmlPath, manifest)
    dom = parse(manifestFilePath)
    root = dom.documentElement
    activityList = root.getElementsByTagName('activity')
    MainActivity = ""
    for activity in activityList:
        if activity.toxml().find("android.intent.action.MAIN") > 0 \
                and activity.toxml().find("android.intent.category.LAUNCHER") > 0:
            MainActivity = activity.getAttribute('android:name')
        print("Activity is " + MainActivity)
        return MainActivity


def unpack(filename):
    print("**************Unpacking**************")
    apktool_command = "apktool d " + filename
    os.system(apktool_command)
    print("**************Unpacked**************")


def inject(path):
    smalipath = path + ".smali"
    print("**************Injecting: {0}**************".format(smalipath))
    with open(smalipath, "r", encoding="utf-8") as file:
        rawsmali = file.readlines()
        file.close()

        insertcode = [
            '\n',
            '    :try_start_5',
            '\n',
            '    invoke-static {p0}, Lcom/dragonmobile/sdk/api/Dragon;->engage(Landroid/content/Context;)V',
            '\n',
            '    :try_end_5',
            '\n',
            '    .catch Ljava/lang/Exception; {:try_start_5 .. :try_end_5} :catch_5',
            '\n\n',
            '    :catch_5',
            '\n'
        ]
        insertcode_tostring = "".join(insertcode)
        insert = insertcode_tostring
    i = 0
    for line in rawsmali:
        i = i + 1
        if line[:16] == "    invoke-super":
            if "onCreate(Landroid/os/Bundle;)V" in line:
                rawsmali.insert(i, insert)

    with open(smalipath, "w", encoding="utf-8") as file:
        file.writelines(rawsmali)
        file.close()
        print("**************Injected: {0}**************".format(smalipath))


def insert():
    smaliPath = scriptPath + app_name + "/smali/"
    smaliPath2 = scriptPath + app_name + "/smali_classes2/"
    pkg = pkgfetcher().replace(".", "/")
    MainActivity_Path = smaliPath + pkg
    if os.path.exists(MainActivity_Path) == True:
        MainActivity_Path = smaliPath2 + pkg
        smaliPath = smaliPath2
    istPath = smaliPath + "com/dragonmobile"
    foldercheck = os.path.exists(istPath)
    if foldercheck == True:
        shutil.rmtree(istPath)
    shutil.copytree(sdk, istPath)
    inject(MainActivity_Path)


def sign(file):
    print("**************Signing: {0}" + file + "**************")
    sign_command = 'jarsigner -digestalg SHA1 -sigalg MD5withRSA -verbose -keystore sigature.keystore -storepass "yuhanbo147258" -keypass "yuhanbo147258" -signedjar ' + app_name + '_Signed.apk ' + file + ' test'
    os.system(sign_command)
    print("**************Signed**************")


def pack(filename):
    print("**************Packing**************")
    apktool_command = "apktool b " + filename
    os.system(apktool_command)
    print("**************Packed**************")


if __name__ == '__main__':
    appList = []
    path = apkPath
    for root, dirs, files in os.walk(path):
        for file in files:
            filename = os.path.join(root, file)
            if filename.endswith('.apk'):
                appList.append(filename)
                # Add all apk into the list
        for item in appList:
            unpack(item)
        # #Unpack process
        for app in appList:
            app_split = os.path.basename(app)
            temp_list = os.path.splitext(app_split)
            app_name = temp_list[0]
            signFile = scriptPath + app_name + "/dist/" + app_name + ".apk"
            # Split apk name
            print("**************apkname: " + app_name + "**************")
            insert()
            pack(app_name)
            # Pack process
            sign(signFile)
    print("**************Program finished**************")
