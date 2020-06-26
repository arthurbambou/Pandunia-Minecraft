from requests import get
import os
import json
import datetime
import zipfile
import csv

booleans = ["yes", "no"]

manifest = get("https://launchermeta.mojang.com/mc/game/version_manifest.json").json()


def isValidMinecraftVersion(minecraft_version):
    if minecraft_version is None:
        return False
    for version in manifest["versions"]:
        if version["id"] == minecraft_version:
            return True
    return False


def getMinecraftVersionInfos(minecraft_version_id):
    if minecraft_version_id is None:
        return None
    for version in manifest["versions"]:
        if version["id"] == minecraft_version_id:
            return version
    return None


class Command:
    def __init__(self, desc, callback):
        self.desc = desc
        self.callback = callback


def registerCommand(name, desc, callback):
    if name not in cmdList:
        cmdList[name] = Command(desc, callback)


def init():
    language_name = None
    while language_name is None or language_name is "":
        print("What is your language name?")
        language_name = input("-> ")
    language_region = None
    while language_region is None or language_region is "":
        print("What is your language region?")
        language_region = input("-> ")
    language_code = None
    while language_code is None or language_code is "":
        print("What is your language code? (Example: US English is en_us)")
        language_code = input("-> ")
    print("Is your language bidirectional?")
    language_bidirectional = str(input("-> ")).lower()
    while language_bidirectional is None or language_bidirectional not in booleans:
        print("Is your language bidirectional?")
        language_bidirectional = str(input("-> ")).lower()
    if language_bidirectional is "yes":
        language_bidirectional = True
    else:
        language_bidirectional = False
    minecraft_version_id = None
    while minecraft_version_id is None or isValidMinecraftVersion(minecraft_version_id) is not True:
        print("Which minecraft version do you want to translate first?")
        minecraft_version_id = input("-> ")
    minecraft_version = getMinecraftVersionInfos(minecraft_version_id)
    if datetime.datetime.strptime(str(minecraft_version["releaseTime"]).replace("+00:00", ""),
                                  "%Y-%m-%dT%H:%M:%S") >= datetime.datetime(2019, 11, 21):
        pack_format = 5
    elif datetime.datetime.strptime(str(minecraft_version["releaseTime"]).replace("+00:00", ""),
                                    "%Y-%m-%dT%H:%M:%S") >= datetime.datetime(2017, 11, 27):
        pack_format = 4
    elif datetime.datetime.strptime(str(minecraft_version["releaseTime"]).replace("+00:00", ""),
                                    "%Y-%m-%dT%H:%M:%S") >= datetime.datetime(2016, 8, 10):
        pack_format = 3
    elif datetime.datetime.strptime(str(minecraft_version["releaseTime"]).replace("+00:00", ""),
                                    "%Y-%m-%dT%H:%M:%S") >= datetime.datetime(2015, 7, 29):
        pack_format = 2
    else:
        pack_format = 1
    print("Initializing workspace")
    print("Generating mcmeta file")
    if not os.path.isdir("resourcepack"):
        os.mkdir("resourcepack")
    mcmeta = {
        "pack": {
            "description": language_name + " translation of Minecraft",
            "pack_format": pack_format
        },
        "language": {
            language_code: {
                "name": language_name,
                "region": language_region,
                "bidirectional": language_bidirectional
            }
        }
    }
    mcmeta_file = open("resourcepack/pack.mcmeta", "w")
    mcmeta_file.write(json.dumps(mcmeta, indent=4))
    mcmeta_file.close()
    print("Done")
    print("Downloading {} client jar".format(minecraft_version_id))
    if not os.path.isdir(".temp"):
        os.mkdir(".temp")
    if not os.path.isfile(".temp/client-{}.jar".format(minecraft_version_id)):
        minecraft_version_manifest = get(minecraft_version["url"]).json()
        client_jar_file = open(".temp/client-{}.jar".format(minecraft_version_id), "wb")
        client_jar_data = get(minecraft_version_manifest["downloads"]["client"]["url"]).content
        client_jar_file.write(client_jar_data)
        client_jar_file.close()
    print("Done")
    print("Extracting en_us.json file")
    jar_content = zipfile.ZipFile(".temp/client-{}.jar".format(minecraft_version_id), 'r')
    jar_content.extract('assets/minecraft/lang/en_us.json', '.temp/{}'.format(minecraft_version_id))
    jar_content.close()
    print("Done")
    print("Reading en_us.json file")
    en_us_file = open(".temp/{}/assets/minecraft/lang/en_us.json".format(minecraft_version_id), 'r')
    en_us = json.loads(en_us_file.read())
    print("Done")
    print("Making csv file")
    with open("translations.csv", 'w', newline='') as csvfile:
        csv_content = csv.writer(csvfile, dialect='excel')
        csv_content.writerow(['Keys', 'English', language_name])
        for entry in en_us:
            if entry == "language.name":
                csv_content.writerow([entry, en_us[entry], language_name])
            elif entry == "language.region":
                csv_content.writerow([entry, en_us[entry], language_region])
            elif entry == "language.code":
                csv_content.writerow([entry, en_us[entry], language_code])
            else:
                csv_content.writerow([entry, en_us[entry], ''])
        csvfile.close()
    en_us_file.close()
    print("Done")
    print("Cleaning temp")
    os.remove(".temp/client-{}.jar".format(minecraft_version_id))
    os.remove(".temp/{}/assets/minecraft/lang/en_us.json".format(minecraft_version_id))
    os.rmdir(".temp/{}/assets/minecraft/lang".format(minecraft_version_id))
    os.rmdir(".temp/{}/assets/minecraft".format(minecraft_version_id))
    os.rmdir(".temp/{}/assets".format(minecraft_version_id))
    os.rmdir(".temp/{}".format(minecraft_version_id))
    os.rmdir(".temp")
    print("Done")


def upgrade():
    file_path = None
    while file_path is None:
        print("Path of your translation.csv file.")
        file_path = input("-> ")
    old_version_id = None
    while old_version_id is None or isValidMinecraftVersion(old_version_id) is False:
        print("Minecraft version of your language file")
        old_version_id = input("-> ")
    old_version = getMinecraftVersionInfos(old_version_id)
    new_version_id = None
    new_version = None
    while new_version_id is None or isValidMinecraftVersion(new_version_id) is False or new_version is None:
        print("Minecraft version you want to upgrade it to")
        new_version_id = input("-> ")
        if isValidMinecraftVersion(new_version_id):
            new_version = getMinecraftVersionInfos(new_version_id)
            if datetime.datetime.strptime(str(new_version["releaseTime"]).replace("+00:00", ""),
                                          "%Y-%m-%dT%H:%M:%S") <= datetime.datetime \
                    .strptime(str(old_version["releaseTime"]).replace("+00:00", ""), "%Y-%m-%dT%H:%M:%S"):
                print("The version you input is older than the previous version of your lang file!")
                new_version = None
    print("Opening CSV file")
    old_rows = []
    with open(file_path, 'r', newline='') as csv_file:
        csv_file_content = csv.reader(csv_file, dialect='excel')
        for row in csv_file_content:
            old_rows.append(row)
        csv_file.close()
    print("Done")
    print("Downloading {} client jar".format(new_version_id))
    if not os.path.isdir(".temp"):
        os.mkdir(".temp")
    if not os.path.isfile(".temp/client-{}.jar".format(new_version_id)):
        minecraft_version_manifest = get(new_version["url"]).json()
        client_jar_file = open(".temp/client-{}.jar".format(new_version_id), "wb")
        client_jar_data = get(minecraft_version_manifest["downloads"]["client"]["url"]).content
        client_jar_file.write(client_jar_data)
        client_jar_file.close()
    print("Done")
    print("Extracting en_us.json file")
    jar_content = zipfile.ZipFile(".temp/client-{}.jar".format(new_version_id), 'r')
    jar_content.extract('assets/minecraft/lang/en_us.json', '.temp/{}'.format(new_version_id))
    jar_content.close()
    print("Done")
    print("Reading en_us.json file")
    en_us_file = open(".temp/{}/assets/minecraft/lang/en_us.json".format(new_version_id), 'r')
    en_us = json.loads(en_us_file.read())
    en_us_file.close()
    print("Done")
    print("Comparing old and new entries")
    todo_key_list = ["New keys:", ""]
    removed_rows = 0
    to_remove = []
    for row in old_rows:
        keep = True
        if row[0] not in en_us:
            keep = False
        if row[0] == 'Keys':
            keep = True
        if keep is False:
            removed_rows = removed_rows + 1
            to_remove.append(row)
    for to_remove_entry in to_remove:
        old_rows.remove(to_remove_entry)
    print("Removed {} rows".format(removed_rows))
    new_rows = 0
    to_add = []
    for key in en_us:
        add = True
        for row in old_rows:
            if key == row[0]:
                add = False
        if add:
            new_rows = new_rows + 1
            to_add.append([key, en_us[key], ''])
            todo_key_list.append(key)
    for to_add_entry in to_add:
        old_rows.append(to_add_entry)
    print("Added {} rows".format(new_rows))
    index = 0
    replaced = 0
    todo_key_list.append("")
    todo_key_list.append("Changed keys:")
    todo_key_list.append("")
    for row in old_rows:
        if row[0] == 'Keys':
            continue
        else:
            index = index + 1
            replace = True
            if row[1] == en_us[row[0]]:
                replace = False
            if replace:
                replaced = replaced + 1
                new_row = [row[0], en_us[row[0]], '']
                old_rows[index] = new_row
                todo_key_list.append(row[0])
    print("Replaced {} rows".format(replaced))
    print("Sorting Rows")
    sorted_rows = [old_rows[0]]
    for key in en_us:
        for row in old_rows:
            if row[0] == key:
                sorted_rows.append(row)
    print("Done")
    print("Done")
    print("Creating upgraded CSV file")
    with open(file_path.replace(".csv", "") + "-{}.csv".format(new_version_id), 'w', newline='') as csvfile:
        csv_content = csv.writer(csvfile, dialect='excel')
        for entry in sorted_rows:
            csv_content.writerow(entry)
        csvfile.close()
    print("Done")
    print("Creating to_translate.txt file")
    with open("to_translate.txt", 'w') as todo_file:
        todo_file_content = todo_key_list[0]
        index = 0
        for todo in todo_key_list:
            if index == 0:
                index = index + 1
                continue
            todo_file_content = todo_file_content + "\n{}".format(todo)
            index = index + 1
        todo_file.write(todo_file_content)
        todo_file.close()
    print("Done")
    print("Cleaning temp")
    os.remove(".temp/client-{}.jar".format(new_version_id))
    os.remove(".temp/{}/assets/minecraft/lang/en_us.json".format(new_version_id))
    os.rmdir(".temp/{}/assets/minecraft/lang".format(new_version_id))
    os.rmdir(".temp/{}/assets/minecraft".format(new_version_id))
    os.rmdir(".temp/{}/assets".format(new_version_id))
    os.rmdir(".temp/{}".format(new_version_id))
    os.rmdir(".temp")
    print("Done")


def build():
    file_path = None
    while file_path is None:
        print("Path of your translation.csv file.")
        file_path = input("-> ")
    print("Reading CSV file")
    csv_rows = []
    with open(file_path, 'r', newline='') as csv_file:
        csv_file_content = csv.reader(csv_file, dialect='excel')
        for row in csv_file_content:
            csv_rows.append(row)
        csv_file.close()
    print("Done")
    print("Reading pack.mcmeta")
    with open("resourcepack/pack.mcmeta", 'r') as mcmeta_file:
        mcmeta = json.loads(mcmeta_file.read())
        mcmeta_file.close()
    print("Done")
    print("Generating lang file")
    if mcmeta["pack"]["pack_format"] > 3:
        lang_file_content = {}
        for row in csv_rows:
            if row is not csv_rows[0]:
                if row[2] is not "":
                    lang_file_content[row[0]] = row[2]
        if not os.path.isdir("resourcepack/assets"):
            os.mkdir("resourcepack/assets")
        if not os.path.isdir("resourcepack/assets/minecraft"):
            os.mkdir("resourcepack/assets/minecraft")
        if not os.path.isdir("resourcepack/assets/minecraft/lang"):
            os.mkdir("resourcepack/assets/minecraft/lang")
        with open("resourcepack/assets/minecraft/lang/{}.json".format(lang_file_content["language.code"]),
                  'w') as lang_file:
            lang_file.write(json.dumps(lang_file_content, indent=4))
            lang_file.close()
    print("Done")
    print("Building Resource pack ZIP")
    resourcepack_zip = zipfile.ZipFile("{}_Translation.zip".format(csv_rows[0][2]), 'w')
    resourcepack_zip.write("resourcepack/pack.mcmeta", "pack.mcmeta")
    if mcmeta["pack"]["pack_format"] > 3:
        resourcepack_zip.write("resourcepack/assets/minecraft/lang/{}.json".format(csv_rows[3][2]),
                               "assets/minecraft/lang/{}.json".format(csv_rows[3][2]))
    resourcepack_zip.close()
    print("Done")


def importPack():
    file_path = None
    while file_path is None:
        print("Path to the language pack files")
        file_path = input("-> ")
    minecraft_version_id = None
    while minecraft_version_id is None or isValidMinecraftVersion(minecraft_version_id) is not True:
        print("Which minecraft version was your language pack made for?")
        minecraft_version_id = input("-> ")
    minecraft_version = getMinecraftVersionInfos(minecraft_version_id)
    print("Reading mcmeta file")
    mcmeta = {}
    with open(os.path.join(file_path, "pack.mcmeta")) as mcmeta_file:
        mcmeta = json.loads(mcmeta_file.read())
        mcmeta_file.close()
    language_meta = {}
    for language in mcmeta["language"]:
        language_meta = mcmeta["language"][language]
        language_meta["code"] = language
    print("Done")
    print("Downloading {} client jar".format(minecraft_version_id))
    if not os.path.isdir(".temp"):
        os.mkdir(".temp")
    if not os.path.isfile(".temp/client-{}.jar".format(minecraft_version_id)):
        minecraft_version_manifest = get(minecraft_version["url"]).json()
        client_jar_file = open(".temp/client-{}.jar".format(minecraft_version_id), "wb")
        client_jar_data = get(minecraft_version_manifest["downloads"]["client"]["url"]).content
        client_jar_file.write(client_jar_data)
        client_jar_file.close()
    print("Done")
    print("Extracting en_us.json file")
    jar_content = zipfile.ZipFile(".temp/client-{}.jar".format(minecraft_version_id), 'r')
    jar_content.extract('assets/minecraft/lang/en_us.json', '.temp/{}'.format(minecraft_version_id))
    jar_content.close()
    print("Done")
    print("Reading en_us.json file")
    en_us_file = open(".temp/{}/assets/minecraft/lang/en_us.json".format(minecraft_version_id), 'r')
    en_us = json.loads(en_us_file.read())
    en_us_file.close()
    print("Done")
    print("Reading {}.json file".format(language_meta["code"]))
    lang_file = open(os.path.join(file_path, "assets/minecraft/lang/{}.json".format(language_meta["code"])))
    lang_json = json.loads(lang_file.read())
    lang_file.close()
    print("Done")
    print("Generating CSV file")
    with open("translations.csv", 'w', newline='') as csvfile:
        csv_content = csv.writer(csvfile, dialect='excel')
        csv_content.writerow(['Keys', 'English', language_meta["name"]])
        for key in en_us:
            if lang_json.get(key) is None:
                csv_content.writerow([key, en_us[key], ''])
            else:
                csv_content.writerow([key, en_us[key], lang_json[key]])
        csvfile.close()
    print("Done")
    print("Cleaning temp")
    os.remove(".temp/client-{}.jar".format(minecraft_version_id))
    os.remove(".temp/{}/assets/minecraft/lang/en_us.json".format(minecraft_version_id))
    os.rmdir(".temp/{}/assets/minecraft/lang".format(minecraft_version_id))
    os.rmdir(".temp/{}/assets/minecraft".format(minecraft_version_id))
    os.rmdir(".temp/{}/assets".format(minecraft_version_id))
    os.rmdir(".temp/{}".format(minecraft_version_id))
    os.rmdir(".temp")
    print("Done")


cmdList = {}
cmdName = None

registerCommand("init", "Initializes a workspace to make a minecraft language file", init)
registerCommand("upgrade", "Upgrade workspace to another version of minecraft", upgrade)
registerCommand("build", "Build your language resourcepack", build)
registerCommand("importPack", "Import a language pack and setup a workspace for it", importPack)

while cmdName not in cmdList:
    if cmdName is not None:
        print("\nInvalid command!")
    print("What command do you want to use?")
    for cmd in cmdList:
        print("- " + cmd + ": " + cmdList[cmd].desc)
    cmdName = input("-> ")


cmdList[cmdName].callback()
