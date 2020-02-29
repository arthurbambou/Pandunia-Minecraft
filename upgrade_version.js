const minecraftVersion = require("./config.json").minecraftVersion;
const fs = require("fs")

const newLang = require("./en_us.json")
const oldLang = require("./resourcepack/assets/minecraft/lang/en_us.json")
const pandunia = require("./resourcepack/assets/minecraft/lang/qpn.json")

lg(`Upgrading lang files from ${minecraftVersion.old} to ${minecraftVersion.new}`)

var newLangInfo = {
    keys : [],
    values : []
}

for(x in newLang) {
    newLangInfo.keys.push(x)
    newLangInfo.values.push(newLang[x])
}
lg(newLangInfo.keys)

var oldLangInfo = {
    keys : [],
    values : []
}

for(x in oldLang) {
    oldLangInfo.keys.push(x)
    oldLangInfo.values.push(oldLang[x])
}

var panduniaInfo = {
    keys : [],
    values : []
}

for(x in pandunia) {
    panduniaInfo.keys.push(x)
    panduniaInfo.values.push(pandunia[x])
}

var newPandunia = {
    keys: [],
    values: []
}

var toTranslate = []

for(var a = 0; a < oldLangInfo.keys.length; a++) {
    var index = newLangInfo.keys.indexOf(oldLangInfo.keys[a])
    if (index > -1) {
        newPandunia.keys[index] = oldLangInfo.keys[a]
        if ((oldLangInfo.values[a] == newLangInfo.values[index]) && (newLangInfo.values[index] != "")) {
            newPandunia.values[index] = panduniaInfo.values[a]
        } else {
            newPandunia.values[index] = newLangInfo.values[index]
            toTranslate.push(newPandunia.keys[index])
        }
    }
}

for(var a = 0; a < newLangInfo.keys.length; a++) {
    var okeys = oldLangInfo.keys
    var nkeys = newLangInfo.keys
    var index = okeys.indexOf(nkeys[a])
    if (index == -1) {
        newPandunia.keys[a] = nkeys[a]
        newPandunia.values[a] = newLangInfo.values[a]
        toTranslate.push(newPandunia.keys[a])
    }
}

var panduniaObject = {}

for(var b = 0; b < newPandunia.keys.length; b++) {
    panduniaObject[newPandunia.keys[b]] = newPandunia.values[b]
}

fs.writeFileSync("./resourcepack/assets/minecraft/lang/qpn.json", JSON.stringify(panduniaObject,null, 2))
fs.writeFileSync("./resourcepack/assets/minecraft/lang/en_us.json", JSON.stringify(newLang, null, 2))

var string = ""

for(x in toTranslate) {
    string = string + toTranslate[x] + "\n"
}

fs.writeFileSync("./totranslate.txt", string)












function lg(string) {
    console.log(string);
}
